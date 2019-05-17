
import jmespath
from aliyun.log import LogException, LogClient
import six.moves.configparser as configparser
from docopt import docopt, DocoptExit
from six import StringIO
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
            print("Invalid parameters.\n")
            print("Usage:\n" + MORE_DOCOPT_CMD)
            return
        elif first_cmd == "log" and len(argv) > 1:
            second_cmd = argv[1]
            header_printed = False
            for cmd in doc.split("\n"):
                if "aliyunlog log " + second_cmd + " " in cmd:
                    if not header_printed:
                        print("Invalid parameters.\n")
                        print("Usage:")
                        header_printed = True

                    print(cmd)

            if header_printed and second_cmd in method_param_usage:
                print("\nOptions:")
                print(method_param_usage[second_cmd])
                print(GLOBAL_OPTIONS_STR)
            else:
                print("Unknown subcommand.")
                print(usage)

        else:
            print("Unknown command.\n")
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


def _process_response(ret, jmes_filter, format_output, decode_output):
    if hasattr(ret, 'get_body'):
        data = ret.get_body()
        _process_response_data(data, jmes_filter, format_output, decode_output)

        return data
    elif inspect.isgenerator(ret):
        for x in ret:
            _process_response(x, jmes_filter, format_output, decode_output)
    else:
        logger.warning("unknown response data: %s", ret)


def main():
    method_types, method_param_usage, optdoc, usage = parse_method_types_optdoc_from_class(LogClient,
                                                                                           LOG_CLIENT_METHOD_BLACK_LIST)

    arguments = docopt_ex(optdoc, usage, method_param_usage, hlp=False, ver=USER_AGENT)
    if arguments is None:
        exit(1)

    system_options = normalize_system_options(arguments)

    # process normal log command
    if arguments.get('log', False):
        try:
            access_id, access_key, endpoint, sts_token, jmes_filter, format_output, decode_output = load_config(system_options)

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

        client = LogClient(endpoint, access_id, access_key, securityToken=verify_sts_token(access_id, sts_token, use=True))
        client.set_user_agent(USER_AGENT)

        assert hasattr(client, method_name), "Unknown parsed command:" + method_name

        data = None
        try:
            ret = getattr(client, method_name)(**args)
            jmes_filter = jmes_filter.replace("\\n", '\n')  # parse faked \n
            data = _process_response(ret, jmes_filter, format_output, decode_output)

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
            args = arguments['<secure_id>'], arguments['<secure_key>'], arguments['<endpoint>'], \
                   arguments['<client_name>'] or LOG_CONFIG_SECTION, arguments['<sts_token>']

            if args[0] is None or args[1] is None or args[2] is None:
                print("Invalid parameters.\n")
                print("Usage:\n" + MORE_DOCOPT_CMD)
                exit(1)

            configure_confidential(*args)

    # process configure command
    elif arguments.get('option', False):
        # process global options
        options = dict((k.replace('--', ''), v) for k, v in arguments.items() if k.startswith('--') and v is not None)
        options.update(system_options)
        if options:
            configure_default_options(options)
        else:
            args = arguments['<secure_id>'], arguments['<secure_key>'], arguments['<endpoint>'], \
                   arguments['<client_name>'] or LOG_CONFIG_SECTION, arguments['<sts_token>']

            if args[0] is None or args[1] is None or args[1] is None:
                print("Invalid parameters.\n")
                print("Usage:\n" + MORE_DOCOPT_CMD)
                exit(1)

            configure_confidential(*args)

