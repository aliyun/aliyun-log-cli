
import jmespath
from aliyun.log import LogException, LogClient
import six.moves.configparser as configparser
from docopt import docopt, DocoptExit
from six import StringIO
from .parser import _get_grouped_usage
from .version import __version__, USER_AGENT
from .config import load_config, LOG_CONFIG_SECTION, GLOBAL_OPTION_SECTION, \
    GLOBAL_OPTION_KEY_FORMAT_OUTPUT, GLOBAL_OPTION_KEY_DEFAULT_CLIENT
from .parser import *
from .parser import _to_string_list
import sys
import json
import logging
from json import JSONEncoder
from functools import partial
from .config import monkey_patch

logger = logging.getLogger(__name__)


def configure_confidential(secure_id, secure_key, endpoint, client_name=LOG_CONFIG_SECTION, sts_token=None):
    """ configure confidential
    :type secure_id: string
    :param secure_id: secure id

    :type secure_key: string
    :param secure_key: secure key

    :type endpoint: string
    :param endpoint: endpoint

    :type client_name: string
    :param client_name: section name, default is "main"

    :type sts_token: string
    :param sts_token: sts token name, default is None

    :return:
    """

    config = configparser.ConfigParser()

    config.read(LOG_CREDS_FILENAME)

    if not config.has_section(client_name):
        config.add_section(client_name)

    config.set(client_name, 'access-id', secure_id)
    config.set(client_name, 'access-key', secure_key)
    config.set(client_name, 'region-endpoint', endpoint)
    config.set(client_name, 'sts-token', verify_sts_token(secure_id, sts_token))

    with open(LOG_CREDS_FILENAME, 'w') as configfile:
        config.write(configfile)


def configure_default_options(options):
    if not options:
        return

    config = configparser.ConfigParser()

    config.read(LOG_CREDS_FILENAME)

    if not config.has_section(GLOBAL_OPTION_SECTION):
        config.add_section(GLOBAL_OPTION_SECTION)

    if GLOBAL_OPTION_KEY_FORMAT_OUTPUT in options:
        config.set(GLOBAL_OPTION_SECTION, GLOBAL_OPTION_KEY_FORMAT_OUTPUT, options[GLOBAL_OPTION_KEY_FORMAT_OUTPUT])
    if GLOBAL_OPTION_KEY_DEFAULT_CLIENT in options:
        config.set(GLOBAL_OPTION_SECTION, GLOBAL_OPTION_KEY_DEFAULT_CLIENT, options[GLOBAL_OPTION_KEY_DEFAULT_CLIENT])
    if GLOBAL_OPTION_KEY_DECODE_OUTPUT in options:
        config.set(GLOBAL_OPTION_SECTION, GLOBAL_OPTION_KEY_DECODE_OUTPUT, options[GLOBAL_OPTION_KEY_DECODE_OUTPUT])

    with open(LOG_CREDS_FILENAME, 'w') as configfile:
        config.write(configfile)

def _parse_cmd_pattern_param(cmd):
    pattern = re.compile(r'--([a-zA-Z0-9_-]+)=<[a-zA-Z0-9_-]+>|\[--([a-zA-Z0-9_-]+)=<[a-zA-Z0-9_-]+>\]')

    required_arguments = set()
    optional_arguments = set()

    matches = pattern.finditer(cmd)
    for match in matches:
        required_argument, optional_argument = match.groups()
        if required_argument:
            required_arguments.add(required_argument)
        if optional_argument:
            optional_arguments.add(optional_argument)
    return required_arguments, optional_arguments

def _print_log_invalid_param_msg(method, args, cmd_patterns, method_param_usage):
    def _print_usage():
        print("Usage:")
        for cmd in cmd_patterns:
            print(cmd)
        print("\nOptions:")
        print(method_param_usage[method])
        print(GLOBAL_OPTIONS_STR)
    try:
        if len(cmd_patterns) == 1:
            cmd_pattern = cmd_patterns[0]
            required_arguments, optional_arguments = _parse_cmd_pattern_param(cmd_pattern)
            cmd_prefix = 'aliyunlog log ' + method + ' '
            full_cmd = cmd_prefix + ' '.join(args)
            # find missing required params
            for param_name in required_arguments:
                if '--' + param_name + '=' not in full_cmd:
                    print("Missing required parameter '{}'.\n".format(param_name))
                    _print_usage()
                    return
            # find unknown params
            pattern = re.compile(r'^--([a-zA-Z0-9_-]+)=')
            err_indicator_offset = len(cmd_prefix)
            for arg in args:
                match = re.search(pattern, arg)
                if match:
                    param_name = match.group(1)
                    if param_name not in required_arguments and param_name not in optional_arguments:
                        print("Unknown parameter '{}'.".format(param_name))
                        print(full_cmd)
                        print(' ' * err_indicator_offset + '^' * len(arg))
                        _print_usage()
                        return
                err_indicator_offset += len(arg) + 1
    except Exception as ex:
        logger.error("fail to print_log_invalid_param_msg: %s", ex)

    print("Invalid parameters.\n")
    _print_usage()

def docopt_ex(doc, usage, method_param_usage, hlp=True, ver=None):
    argv = sys.argv[1:]

    # support customized help
    if len(argv) <= 0 or "--help" in argv[0]:
        print(usage)
        return

    first_cmd = argv[0]

    try:
        return docopt(doc, help=hlp, version=ver)
    except DocoptExit as ex:
        # show customized error
        if first_cmd == "configure":
            print("Invalid configure parameters.\n")
            print("Usage:\n" + MORE_DOCOPT_CMD)
            return
        elif first_cmd == "log":
            if len(argv) == 1:
                print("Missing aliyunlog log subcommand, example usage:")
                print("aliyunlog log get_project --project_name=test")
                print('              ^^^^^^^^^^^')
                print('Supported aliyunlog log subcommands:')
                print(_get_grouped_usage())
                return
            second_cmd = argv[1]
            cmd_patterns = []
            for supported_cmd in doc.split("\n"):
                if "aliyunlog log " + second_cmd + " " in supported_cmd:
                    cmd_patterns.append(supported_cmd)

            if len(cmd_patterns) == 0 or second_cmd not in method_param_usage:
                print("Unknown aliyunlog log subcommand: " + second_cmd)
                print('aliyunlog log ' + second_cmd + ' ' + ' '.join(argv[2:]))
                print('              ' + '^' * len(second_cmd))
                print(usage)
                return

            _print_log_invalid_param_msg(second_cmd, argv[1:], cmd_patterns, method_param_usage)
            return
        else:
            print("Unknown command: '{}'.".format(first_cmd))
            print('aliyunlog log ' + first_cmd)
            print('              ' + '^' * len(first_cmd))
            print(usage)


def get_encoder_cls(encodings):
    class NonUtf8Encoder(JSONEncoder):
        def default(self, obj):
            if isinstance(obj, six.binary_type):
                for encoding in encodings:
                    try:
                        return obj.decode(encoding)
                    except UnicodeDecodeError as ex:
                        pass
                return obj.decode('utf8', "ignore")

            return JSONEncoder.default(self, obj)

    return NonUtf8Encoder


def show_result(result, format_output, decode_output=None):
    encodings = decode_output or ('utf8', 'latin1', 'gbk')
    if result != "" and result != b'':
        if isinstance(result, (six.text_type, six.binary_type)):
            try:
                print(result)
            except UnicodeEncodeError as ex:
                # workaround issue #59 temporarily
                logger.warning("fail to print result: %s", ex)
                print(result.encode('utf8'))
        else:
            fmt = format_output.lower().strip()
            escape = 'no_escape' not in fmt
            json_fmt = 'json' in fmt
            if six.PY2:
                last_ex = None
                for encoding in encodings:
                    try:
                        if json_fmt:
                            result = json.dumps(result, sort_keys=True, indent=2, separators=(',', ': '),
                                             encoding=encoding, ensure_ascii=escape)
                        else:
                            result = json.dumps(result, sort_keys=True, encoding=encoding, ensure_ascii=escape)
                        if not escape:
                            # for redirection consideration
                            print(result.encode('utf8'))
                        else:
                            print(result)

                        break
                    except UnicodeDecodeError as ex:
                        last_ex = ex
                    except UnicodeEncodeError as ex:
                        last_ex = ex
                else:
                    raise last_ex
            else:
                if json_fmt:
                    print(json.dumps(result, sort_keys=True, indent=2, separators=(',', ': '),
                                     cls=get_encoder_cls(encodings), ensure_ascii=escape))
                else:
                    print(json.dumps(result, sort_keys=True, cls=get_encoder_cls(encodings),
                                     ensure_ascii=escape))


def _log_response_converter(data):
    return data if isinstance(data, list) else data['data']
        
def _process_response_data(data, jmes_filter, format_output, decode_output):
    if data is not None:
        if jmes_filter:
            # filter with jmes
            try:
                if 'no_escape' in format_output.strip().lower():
                    with monkey_patch(json, 'dumps', partial(json.dumps, ensure_ascii=False)):
                        result = jmespath.compile(jmes_filter).search(data)
                else:
                    result = jmespath.compile(jmes_filter).search(data)

                show_result(result, format_output, decode_output)
            except jmespath.exceptions.ParseError as ex:
                logger.error("fail to parse with JMES path, original data: %s", ex)
                show_result(data, format_output, decode_output)
                exit(1)
        else:
            show_result(data, format_output, decode_output)


def _process_response(ret, jmes_filter, format_output, decode_output, data_converter):
    if hasattr(ret, 'get_body'):
        data = ret.get_body()
        if data_converter is not None:
            data = data_converter(data)
        _process_response_data(data, jmes_filter, format_output, decode_output)

        return data
    elif inspect.isgenerator(ret):
        for x in ret:
            _process_response(x, jmes_filter, format_output, decode_output, data_converter)
    else:
        logger.warning("unknown response data: %s", ret)


def main():
    method_types, method_param_usage, optdoc, usage = parse_method_types_optdoc_from_class(LogClient)

    arguments = docopt_ex(optdoc, usage, method_param_usage, hlp=False, ver=USER_AGENT)
    if arguments is None:
        exit(1)

    system_options = normalize_system_options(arguments)

    # process normal log command
    if arguments.get('log', False):
        try:
            access_id, access_key, endpoint, sts_token, jmes_filter, format_output, decode_output,\
                sign_version, region_id = load_config(system_options)

            decode_output = _to_string_list(decode_output)  # convert decode to list if any

            method_name, args = normalize_inputs(arguments, method_types)
            if not (endpoint and access_id and access_key):
                raise IncompleteAccountInfoError("endpoint, access_id or key is not configured")

        except IncompleteAccountInfoError as ex:
            print("""
Error!

The default account is not configured or the command doesn't have a well-configured account passed. 

Fix it by either configuring a default account as: 
> aliyunlog configure <access_id> <access-key> <endpoint>
> aliyunlog configure <access_id> <access-key> main <sts_token>

or use option --client-name to specify a well-configured account as:
> aliyunlog configure <access_id> <access-key> <endpoint> <user-bj>
> aliyunlog configure <access_id> <access-key> <endpoint> <user-bj> <sts_token>
> aliyunlog log .....  --client-name=user-bj

Refer to https://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_configure_cli_en.html for more info.

            """)
            exit(2)

        client = LogClient(endpoint,
                           access_id,
                           access_key,
                           securityToken=verify_sts_token(access_id, sts_token, use=True),
                           auth_version=sign_version,
                           region=region_id)
        client.set_user_agent(USER_AGENT)

        assert hasattr(client, method_name), "Unknown parsed command:" + method_name

        data = None
        try:
            ret = getattr(client, method_name)(**args)
            jmes_filter = jmes_filter.replace("\\n", '\n')  # parse faked \n
            converter = None
            if method_name in ['get_log', 'get_logs', 'get_log_all', 'get_log_all_v2', 'get_project_logs',
                               'execute_logstore_sql',
                               'execute_project_sql']:
                converter = _log_response_converter
            data = _process_response(ret, jmes_filter, format_output, decode_output, converter)

        except LogException as ex:
            if data is not None:
                show_result(data, format_output)
            else:
                print(ex)
            logger.error("fail to call subcommand: " + str(ex), exc_info=True)
            exit(3)

    # process configure command
    elif arguments.get('configure', False):
        # process global options
        options = dict((k.replace('--', ''), v) for k, v in arguments.items() if k.startswith('--') and v is not None)
        options.update(system_options)
        if options:
            configure_default_options(options)
        else:
            for param in ['<access_id>', '<access_key>', '<endpoint>']:
                if not arguments[param]:
                    print("Missing required parameter '{}'.\n".format(param))
                    print("Usage:\n" + MORE_DOCOPT_CMD)
                    exit(1)
            args = arguments['<access_id>'], arguments['<access_key>'], arguments['<endpoint>'], \
                   arguments['<client_name>'] or LOG_CONFIG_SECTION, arguments['<sts_token>']

            configure_confidential(*args)

    # process configure command
    elif arguments.get('option', False):
        # process global options
        options = dict((k.replace('--', ''), v) for k, v in arguments.items() if k.startswith('--') and v is not None)
        options.update(system_options)
        if options:
            configure_default_options(options)
        else:
            for param in ['<access_id>', '<access_key>', '<endpoint>']:
                if not arguments[param]:
                    print("Missing required parameter '{}'.\n".format(param))
                    print("Usage:\n" + MORE_DOCOPT_CMD)
                    exit(1)
            args = arguments['<access_id>'], arguments['<access_key>'], arguments['<endpoint>'], \
                   arguments['<client_name>'] or LOG_CONFIG_SECTION, arguments['<sts_token>']

            configure_confidential(*args)

