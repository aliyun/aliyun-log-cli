import inspect
import json
import re

from aliyun import log
from aliyun.log import *
from aliyun.log.util import Util
from .config import *
from .config import load_default_config_from_file_env, load_config_from_file, LOG_CONFIG_SECTION


def _parse_method(func):
    if inspect.ismethod(func):
        func = func.__func__
    arg_info = inspect.getargspec(func)
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

    args_list = ''
    for i, arg in enumerate(args):
        if i >= option_arg_pos:
            args_list += '[--' + arg + '=<value>] '
        else:
            args_list += '--' + arg + '=<value> '

    doc = 'aliyun log ' + func.__name__ + ' ' + args_list + SYSTEM_OPTIONS_STR + '\n'

    return doc


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
    except Exception:
        print("** failed to convert value='{0}' to type dict".format(s))
        raise


def _to_list(s):
    try:
        if isinstance(s, list):
            return s

        v = json.loads(s)
        if not isinstance(v, list):
            raise ValueError("input is not list")

        return v
    except Exception:
        print("** failed to convert value='{0}' to type string list".format(s))
        raise


def _assert_string_list(v):
    for s1 in v:
        if not isinstance(s1, (six.text_type, six.binary_type)):
            raise ValueError("input is not string list: " + str(v))


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
        print("** failed to convert value='{0}' to type int list".format(s))
        raise


def _to_string_list(s):
    try:
        v = _to_list(s)
        _assert_string_list(v)

        return v
    except Exception:
        print("** failed to convert value='{0}' to type string list".format(s))
        raise


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
        print("** failed to convert value='{0}' to type list of log item".format(s))
        raise


def _request_maker(cls):
    def maker(json_str):
        args_list, option_arg_pos = _parse_method(cls.__init__)

        if json_str.startswith('file://'):
            with open(json_str[7:], "r") as f:
                json_str = f.read()

        if option_arg_pos == 0 and hasattr(cls, 'from_json'):
            # there's a from json method, try to use it
            try:
                j = json.loads(json_str)
                extjson = Util.convert_unicode_to_str(j)
                obj = cls()
                obj.from_json(extjson)

                return obj
            except Exception as ex:
                print("** fail to load input via method from_json, try to call constructor for cls: "
                      + str(cls) + "\nex:" + str(ex))

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
                print("*** IO error: ", ex, json_str)
            except Exception as ex:
                continue

        print("*** cannot construct relative object for json {0} with cls list {1}".format(json_str, cls_args))
        return json_str

    return maker


def _make_log_client(to_client):
    if not to_client:
        if to_client == LOG_CONFIG_SECTION:
            access_id, access_key, endpoint = load_default_config_from_file_env()
        else:
            access_id, access_key, endpoint = load_config_from_file(to_client)

        assert endpoint and access_id and access_key, \
            ValueError("endpoint, access_id or key is not configured for section {0}".format(to_client))

        return LogClient(endpoint, access_id, access_key)

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
    results = re.split(r"\s+or\s+|/|\||,", t.strip(), re.IGNORECASE)
    find_cls = []
    for t in results:
        t = t.strip()
        if t and t in dir(log) and inspect.isclass(getattr(log, t)):
            find_cls.append(getattr(log, t))

    if find_cls:
        handler = _requests_maker(*find_cls)
        return handler

    return None


def _parse_method_params_from_doc(doc):
    if not doc:
        return None

    ptn = r'\:type\s+(\w+)\s*\:\s*([\w\. <>]+)\s*.+?(?:\:param\s+\1\:\s*([^\n]+)\s*)?'
    m = re.findall(ptn, doc, re.MULTILINE)

    params = dict((k, types_maps.get(t.lower().strip(), None)) for k, t, d in m)

    unsupported_types = [(k, t, d) for k, t, d in m if params.get(k, None) is None]
    if unsupported_types:
        for k, t, d in unsupported_types:
            handler = _find_multiple_cls(t)
            if handler is not None:
                # add to type maps
                types_maps[t] = handler

                # add to returned value
                params[k] = handler
                continue

            print("***** unknown types: ", k, t, d)

    return params


def _match_black_list(method_name, black_list):
    for l in black_list:
        if re.match(l, method_name):
            return True
    return False


def _attach_more_cmd():
    cmd = """aliyun configure <secure_id> <secure_key> <endpoint> [<client_name>]\n"""

    return cmd


def parse_method_types_optdoc_from_class(cls, black_list=None):
    if black_list is None:
        black_list = (r'^_.+',)

    method_list = []
    for k in dir(cls):
        m = getattr(cls, k, None)
        if not k.startswith('_') and not _match_black_list(k, black_list) \
                and (inspect.isfunction(m) or inspect.ismethod(m)):
            method_list.append(k)

    params_types = {}

    doc = 'Usage:\n'
    doc += _attach_more_cmd()

    for m in method_list:
        method = getattr(cls, m, None)
        if method:
            p = _parse_method_params_from_doc(method.__doc__)
            params_types[m] = p

            doc += _parse_method_cli(method)

    doc += '\n'
    return params_types, doc


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
                    print("** failed to convert parameter '{0}' value='{1}' to type {2}".format(arg, value, t))
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
