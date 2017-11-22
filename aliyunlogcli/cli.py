
from jmespath.exceptions import ParseError
from parser import *
from __init__ import __version__, USER_AGENT
from aliyun.log import LogException, LogClient
import six.moves.configparser as configparser
from docopt import docopt
from config import load_config

import collections
from six import StringIO


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


def _get_str(obj, enclosed=True):
    if enclosed:
        return repr(obj)
    return str(obj)

def _sort_str_dict(obj, enclosed=False):
    buf = StringIO()
    if isinstance(obj, dict):
        buf.write('{')
        for i, x in enumerate(sorted(obj)):
            if i == 0:
                buf.write("{0}: {1}".format(_sort_str_dict(x, True), _sort_str_dict(obj[x], True)))
            else:
                buf.write(", {0}: {1}".format(_sort_str_dict(x, True), _sort_str_dict(obj[x], True)))

        buf.write('}')
        return buf.getvalue()
    elif isinstance(obj, list):
        buf.write('[')
        for i, x in enumerate(obj):
            if i == 0:
                buf.write("{0}".format(_sort_str_dict(x, True)))
            else:
                buf.write(", {0}".format(_sort_str_dict(x, True)))
        buf.write(']')
        return buf.getvalue()
    else:
        return _get_str(obj, enclosed)


def main():
    method_types, optdoc = parse_method_types_optdoc_from_class(LogClient, LOG_CLIENT_METHOD_BLACK_LIST)

    arguments = docopt(optdoc, version=__version__)
    system_options = normalize_system_options(arguments)

    # process normal log command
    if arguments.get('log', False):
        access_id, access_key, endpoint, jmes_filter = load_config(system_options)
        method_name, args = normalize_inputs(arguments, method_types)
        assert endpoint and access_id and access_key, ValueError("endpoint, access_id or key is not configured")
        client = LogClient(endpoint, access_id, access_key)
        client.set_user_agent(USER_AGENT)

        assert hasattr(client, method_name), "Unknown parsed command:" + method_name

        try:
            ret = getattr(client, method_name)(**args)

            if jmes_filter and ret is not None and ret.get_body():
                # filter with jmes
                try:
                    print(jmespath.compile(jmes_filter).search(ret.get_body()))
                except jmespath.exceptions.ParseError as ex:
                    print("**fail to parse with JMSE path, original data: ", ex)
                    print(_sort_str_dict(ret.get_body()))
                    exit(1)
            elif ret is not None:
                print(_sort_str_dict(ret.get_body()))

        except LogException as ex:
            print(_sort_str_dict(ex.get_resp_body()))
            exit(2)

    # process configure command
    elif arguments.get('configure', False):
        args = arguments['<secure_id>'], arguments['<secure_key>'], arguments['<endpoint>'], \
               arguments['<client_name>'] or LOG_CONFIG_SECTION
        configure_confidential(*args)


if __name__ == '__main__':
    main()


# def test_convert():
    # d1 = {1:'\n'}
    # print(_sort_str_dict(d1))
    # assert r"{1: '\n'}" == _sort_str_dict(d1)
    #
    # d1 = {1:'\t'}
    # print(_sort_str_dict(d1))
    # assert r"{1: '\t'}" == _sort_str_dict(d1)
    #
    # d1 = "123"
    # print(_sort_str_dict(d1))
    # assert """123""" == _sort_str_dict(d1)
    #
    # d1 = ""
    # print(_sort_str_dict(d1))
    # assert """""" == _sort_str_dict(d1)
    #
    # d1 = 123
    # print(_sort_str_dict(d1))
    # assert """123""" == _sort_str_dict(d1)
    #
    # d1 = [1,'2', 3]
    # print(_sort_str_dict(d1))
    # assert """[1, '2', 3]""" == _sort_str_dict(d1)
    #
    # d1 = {1:1, '3':3, 2:'2'}
    # print(_sort_str_dict(d1))
    # assert """{1: 1, 2: '2', '3': 3}""" == _sort_str_dict(d1)
    #
    # d1 = [1,'2', {1:1, '3':3, 2:'2'}]
    # print(_sort_str_dict(d1))
    # assert """[1, '2', {1: 1, 2: '2', '3': 3}]""" == _sort_str_dict(d1)
    #
    # d1 = {1:{1:1, '3':3, 2:'2'}, '3':{1:1, '3':{1:1, '3':3, 2:'2'}, 2:'2'}, 2:'2'}
    # print(_sort_str_dict(d1))
    # assert """{1: {1: 1, 2: '2', '3': 3}, 2: '2', '3': {1: 1, 2: '2', '3': {1: 1, 2: '2', '3': 3}}}""" == _sort_str_dict(d1)
    #
    # exit(10)
