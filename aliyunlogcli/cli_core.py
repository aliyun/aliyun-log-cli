
import jmespath
from aliyun.log import LogException, LogClient
import six.moves.configparser as configparser
from docopt import docopt, DocoptExit
from six import StringIO
from .version import __version__, USER_AGENT
from .config import load_config, LOG_CONFIG_SECTION
from .parser import *
import sys
import json
import logging
logger = logging.getLogger(__name__)


def configure_confidential(secure_id, secure_key, endpoint, client_name=LOG_CONFIG_SECTION):
    """ configure confidential
    :type secure_id: string
    :param secure_id: secure id

    :type secure_key: string
    :param secure_key: secure key

    :type endpoint: string
    :param endpoint: endpoint

    :type client_name: string
    :param client_name: section name, default is "main"

    :return:
    """

    config = configparser.ConfigParser()

    config.read(LOG_CREDS_FILENAME)

    if not config.has_section(client_name):
        config.add_section(client_name)

    config.set(client_name, 'access-id', secure_id)
    config.set(client_name, 'access-key', secure_key)
    config.set(client_name, 'region-endpoint', endpoint)

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
                if "aliyun log " + second_cmd + " " in cmd:
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


def show_result(result):
    if result != "" and result != b'':
        print(json.dumps(result, sort_keys=True))


def main():
    method_types, method_param_usage, optdoc, usage = parse_method_types_optdoc_from_class(LogClient,
                                                                                           LOG_CLIENT_METHOD_BLACK_LIST)

    arguments = docopt_ex(optdoc, usage, method_param_usage, hlp=False, ver=__version__)
    if arguments is None:
        return

    system_options = normalize_system_options(arguments)

    # process normal log command
    if arguments.get('log', False):
        access_id, access_key, endpoint, jmes_filter = load_config(system_options)
        method_name, args = normalize_inputs(arguments, method_types)
        assert endpoint and access_id and access_key, ValueError("endpoint, access_id or key is not configured")
        client = LogClient(endpoint, access_id, access_key)
        client.set_user_agent(USER_AGENT)

        assert hasattr(client, method_name), "Unknown parsed command:" + method_name

        ret = None
        try:
            ret = getattr(client, method_name)(**args)

            if jmes_filter and ret is not None and ret.get_body():
                # filter with jmes
                try:
                    show_result(jmespath.compile(jmes_filter).search(ret.get_body()))
                except jmespath.exceptions.ParseError as ex:
                    logger.error("fail to parse with JMSE path, original data: %s", ex)
                    show_result(ret.get_body())
                    exit(1)
            elif ret is not None:
                show_result(ret.get_body())

        except LogException as ex:
            if ret is not None:
                show_result(ret.get_body())
            else:
                print(ex)
            exit(2)

    # process configure command
    elif arguments.get('configure', False):
        args = arguments['<secure_id>'], arguments['<secure_key>'], arguments['<endpoint>'], \
               arguments['<client_name>'] or LOG_CONFIG_SECTION
        configure_confidential(*args)
