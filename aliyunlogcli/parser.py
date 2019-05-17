import inspect
import json
import re

from aliyun import log
from aliyun.log import *
from aliyun.log.util import Util
from .config import *
from .config import load_default_config_from_file_env, load_confidential_from_file, LOG_CONFIG_SECTION, verify_sts_token


try:
    from collections import OrderedDict
except ImportError:
    # for py2.6 case
    from ordereddict import OrderedDict

from six import StringIO
import logging
logger = logging.getLogger(__name__)


def _read_file_input(value):
    if isinstance(value, (six.binary_type, six.text_type)) and value.startswith('file://'):
        with open(value[7:], "r") as f:
            return f.read()

    return value


def _file_input(fn):
    def wrapped(*args, **kwargs):
        args = tuple(_read_file_input(x) for x in args)
        kwargs = dict((k, _read_file_input(v)) for k, v in kwargs)
        return fn(*args, **kwargs)

    return wrapped


def _parse_method(func):
    if inspect.ismethod(func):
        func = func.__func__

    if not inspect.isfunction(func):
        # it's not a function, just return default.
        return [], 0

    if six.PY2:
        arg_info = inspect.getargspec(func)
    else:
        arg_info = inspect.getfullargspec(func)
    args = arg_info.args
    defaults = arg_info.defaults or []

    if 'self' in args:
        args = args[1:]

    option_arg_pos = len(args) - len(defaults)
    return args, option_arg_pos


def normalize_system_options(arguments):
    ret = {}

    for option in SYSTEM_OPTIONS:
        k = '--' + option
        v = arguments.get(k, None)
        if v is not None:
            ret[option] = v
            arguments[k] = None  # remove it from arguments

    return ret


def _parse_method_cli(func):
    args, option_arg_pos = _parse_method(func)

    ptn = r'^\s*\:param[ \t]+(\w+)[ \t]*\:[ \t]*([^\n]*?)\s*$'
    param_docs = dict(re.findall(ptn, func.__doc__ or '', re.MULTILINE))
    param_usage_doc = ''

    args_list = ''
    for i, arg in enumerate(args):
        if i >= option_arg_pos:
            arg_doc = '[--' + arg + '=<value>] '
        else:
            arg_doc = '--' + arg + '=<value> '

        args_list += arg_doc
        param_usage_doc += arg_doc + '\t\t: ' + param_docs.get(arg, arg) + "\n"

    opt_doc = 'aliyunlog log ' + func.__name__ + ' ' + args_list + SYSTEM_OPTIONS_STR + '\n'

    return opt_doc, param_usage_doc


def _to_bool(s):
    if isinstance(s, bool):
        return s

    if isinstance(s, (int, float)):
        return bool(s)

    if isinstance(s, (six.binary_type, six.text_type)):
        if str(s).lower().strip() in ("true", "1", "t", "yes", "y"):
            return True
        elif str(s).lower().strip() in ("false", "0", "f", "no", "f"):
            return False

    raise ValueError("fail to convert value to bool with value: {0}".format(s))


@_file_input
def _to_dict(s):
    try:
        if isinstance(s, dict):
            v = s
        else:
            v = json.loads(s)
            if not isinstance(v, dict):
                raise ValueError("input is not dict")

        for s1 in v:
            if not isinstance(s1, (six.text_type, six.binary_type)):
                raise ValueError("input is not dict")

        return v
    except Exception as ex:
        logger.error("failed to convert value='{0}' to type dict, detail={1}".format(s, str(ex)))
        raise


@_file_input
def _to_list(s):
    try:
        if isinstance(s, (list, tuple)):
            return s

        v = json.loads(s)
        if not isinstance(v, list):
            raise ValueError("input is not list")

        return v
    except Exception:
        logger.error("failed to convert value='{0}' to type string list".format(s))
        raise


def _assert_string_list(v):
    for s1 in v:
        if not isinstance(s1, (six.text_type, six.binary_type)):
            raise ValueError("input is not string list: " + str(v))


@_file_input
def _to_int_list(s):
    try:
        v = _to_list(s)
        new_v = []
        for s1 in v:
            if not isinstance(s1, int):
                new_v.append(int(s1))
                continue
            else:
                new_v.append(s1)

        return new_v
    except Exception:
        logger.error("failed to convert value='{0}' to type int list".format(s))
        raise


@_file_input
def _to_string_list(s):
    if isinstance(s, (six.text_type, six.binary_type)):
        return re.split(r'[\s\|\,]+', s)

    try:
        v = _to_list(s)
        _assert_string_list(v)

        return v
    except Exception:
        logger.error("failed to convert value='{0}' to type string list".format(s))
        raise


@_file_input
def to_logitem_list(s):
    try:
        if isinstance(s, list):
            v = s
        else:
            v = json.loads(s)

            if isinstance(v, list):
                raise ValueError("input is not list")

        new_v = []
        for s1 in v:
            if isinstance(s1, LogItem):
                new_v.append(s1)
                continue

            if not isinstance(s1, dict) or 'contents' not in s1 or not isinstance(s1['contents'], list):
                raise ValueError("content of input is not log item")

            for content in s1['contents']:
                _assert_string_list(content)
            new_v.append(LogItem(s1.get('timestamp', None), s1['contents']))

        return new_v

    except Exception:
        logger.error("failed to convert value='{0}' to type list of log item".format(s))
        raise


def _request_maker(cls):
    @_file_input
    def maker(json_str):
        args_list, option_arg_pos = _parse_method(cls.__init__)
        if hasattr(cls, 'from_json'):
            # there's a from json method, try to use it
            try:
                j = json.loads(json_str)
                extjson = Util.convert_unicode_to_str(j)
                if option_arg_pos == 0:
                    obj = cls()
                    new_obj = obj.from_json(extjson)
                    if new_obj is None:
                        return obj      # expecting it's updated
                    else:
                        return new_obj  # expecting return a new obj
                else:
                    # expect the from_json is static method.
                    return cls.from_json(extjson)

            except Exception as ex:
                logger.warn("fail to load input via method from_json, try to call constructor for cls: "
                            + str(cls) + "\n\tex:" + str(ex))

        method_type = _parse_method_params_from_doc(cls.__doc__)
        j = json.loads(json_str)
        # verify if all mandantory args exists
        for i, arg in enumerate(args_list):
            if i >= option_arg_pos:
                break
            if arg not in j:
                raise ValueError("args:{0} is missed".format(arg))

        # verify if all inputs exists in parameters
        for k in j:
            if k not in args_list:
                raise ValueError("args:{0} is unexpected".format(k))

        # convert all values to expected type
        converted_args = _convert_args(j, method_type)

        return cls(**converted_args)

    return maker


def _requests_maker(*cls_args):
    def maker(json_str):

        for cls in cls_args:
            try:
                obj = _request_maker(cls)(json_str)
                return obj
            except IOError as ex:
                logger.warn("IO error: %s, %s", ex, json_str)
            except Exception as ex:
                logger.warn("skip it to next, ignore error: " + str(ex))

        logger.warn("cannot construct relative object for json '{0}' with cls list {1}".format(json_str, cls_args))
        return json_str

    return maker


def _chained_method_maker(*method_list):
    def maker(value):
        exceptions = []
        for method in method_list:
            try:
                obj = method(value)
                return obj
            except Exception as ex:
                exceptions.append(str(ex))
                logger.debug("error to call {0}, detail: {1}, skip to next".format(method, str(ex)))

        logger.warn("*** cannot construct relative object '{0}' with value '{1}', detail: {2}".format(str(method_list), value, exceptions))
        return value

    return maker


def _make_log_client(to_client):
    if to_client:
        if to_client == LOG_CONFIG_SECTION:
            access_id, access_key, endpoint, sts_token = load_default_config_from_file_env()
        else:
            access_id, access_key, endpoint, sts_token = load_confidential_from_file(to_client)

        assert endpoint and access_id and access_key, \
            ValueError("endpoint, access_id or key is not configured for section {0}".format(to_client))

        return LogClient(endpoint, access_id, access_key, securityToken=verify_sts_token(access_id, sts_token, use=True))

    raise ValueError("fail to convert section {0} to log client instance.".format(to_client))


types_maps = {
    'string': str, 'str': str,
    'bool': _to_bool, 'boolean': _to_bool,
    'int': int, 'double': float,
    'int list': _to_int_list,
    'string list': _to_string_list,
    'string array': _to_string_list,
    'dict': _to_dict,
    'list': _to_list,
    'list<logitem>': to_logitem_list,
    'logclient': _make_log_client
}


def _find_multiple_cls(t):
    results = re.split(r"\s+(?:or|OR|Or)\s+|/|\||,", t.strip())
    find_cls = []
    find_method_list = []
    for t in results:
        t = t.strip()
        if t and t in dir(log) and inspect.isclass(getattr(log, t)):
            find_cls.append(getattr(log, t))
        elif t.lower() in types_maps:
            find_method_list.append(types_maps.get(t.lower()))

    if find_cls and find_method_list:
        # combine two kind of caller together
        handler = _requests_maker(*find_cls)
        find_method_list.append(handler)
        return _chained_method_maker(*find_method_list)
    elif find_cls:
        return _requests_maker(*find_cls)
    elif find_method_list:
        return _chained_method_maker(*find_method_list)

    return None


def _parse_method_params_from_doc(doc):
    if not doc:
        return None

    ptn = r'^\s*\:type[ \t]+(\w+)[ \t]*\:[ \t]*([^\n]*?)\s*$'
    key_type_list = re.findall(ptn, doc, re.MULTILINE)

    param_handlers = dict((k, types_maps.get(t.lower().strip(), None)) for k, t in key_type_list)

    unsupported_types = [(k, t) for k, t in key_type_list if param_handlers.get(k, None) is None]
    if unsupported_types:
        for k, t in unsupported_types:
            handler = _find_multiple_cls(t)
            if handler is not None:
                # add to type maps
                types_maps[t] = handler

                # add to returned value
                param_handlers[k] = handler
                continue

            logger.warn("unknown types: %s, %s", k, t)

    return param_handlers


def _match_black_list(method_name, black_list):
    for l in black_list:
        if re.match(l, method_name):
            return True
    return False


def _attach_more_cmd_docopt():
    return MORE_DOCOPT_CMD


def _get_grouped_usage(method_list):
    dct = OrderedDict()
    for k in API_GROUP:
        des = k[1] if isinstance(k, (list, tuple)) else k.title()
        dct[des] = []

    for x in method_list:
        for k in API_GROUP:
            key = k[0] if isinstance(k, (list, tuple)) else k
            des = k[1] if isinstance(k, (list, tuple)) else k.title()
            if re.search(key, x):
                dct[des].append(x)
                break
        else:
            if "Others" not in dct:
                dct["Others"] = []
            dct["Others"].append(x)

    usage = StringIO()
    for k, v in dct.items():
        usage.write("\n\t")
        usage.write(k)
        usage.write("\n\t" + "-" * 35)
        for d in sorted(v):
            usage.write("\n\t")
            usage.write(d)

        usage.write("\n")

    return usage.getvalue()


def _get_method_list(cls, black_list=None):
    if black_list is None:
        black_list = (r'^_.+',)

    method_list = []
    for k in dir(cls):
        m = getattr(cls, k, None)
        if not k.startswith('_') and not _match_black_list(k, black_list) \
                and (inspect.isfunction(m) or inspect.ismethod(m)):
            method_list.append(k)

    return method_list


def parse_method_types_optdoc_from_class(cls, black_list=None):
    method_list = _get_method_list(cls, black_list)
    params_types = {}
    params_doc = {}

    cli_usage_doc = USAGE_STR_TEMPLATE.format(grouped_api=_get_grouped_usage(method_list))

    opt_doc = 'Usage:\n'
    opt_doc += MORE_DOCOPT_CMD

    for m in method_list:
        method = getattr(cls, m, None)
        if method:
            p = _parse_method_params_from_doc(method.__doc__)
            params_types[m] = p

            method_opt_doc, method_usage_doc = _parse_method_cli(method)
            opt_doc += method_opt_doc

            params_doc[m] = method_usage_doc

    opt_doc += '\n'
    return params_types, params_doc, opt_doc, cli_usage_doc


def _convert_args(args_values, method_types):
    # convert args
    converted_args = {}
    for arg, value in args_values.items():
        if arg in method_types:
            t = method_types[arg]
            if t not in (None, str):
                try:
                    converted_args[arg] = t(value)
                except Exception:
                    logger.error("failed to convert parameter '{0}' value='{1}' to type {2}".format(arg, value, t))
                    raise
                continue

        converted_args[arg] = value

    return converted_args


def normalize_inputs(arguments, method_types):
    method_name = ''
    for m in method_types:
        if m in arguments and arguments[m]:
            method_name = m
            break

    if not method_name:
        raise ValueError("unknown command:" + method_name)

    real_args = dict((k.replace('--', ''), v) for k, v in arguments.items() if k.startswith('--') and v is not None)

    # convert args
    converted_args = _convert_args(real_args, method_types[method_name])

    return method_name, converted_args
