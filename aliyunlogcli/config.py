import os
from collections import namedtuple
import six.moves.configparser as configparser
import six
import jmespath
from jmespath.exceptions import ParseError

LOG_CLIENT_METHOD_BLACK_LIST = (r'_.+', r'\w+acl', 'set_source', 'delete_shard', 'heart_beat',
                                'set_user_agent', 'get_unicode',
                                )

LOG_CREDS_FILENAME = "%s/.aliyunlogcli" % os.path.expanduser('~')
LOG_CONFIG_SECTION = "main"

SYSTEM_OPTIONS = ['access-id', 'access-key', 'region-endpoint', 'client-name', 'jmes-filter']
SYSTEM_OPTIONS_STR = ' '.join('[--' + x + '=<value>]' for x in SYSTEM_OPTIONS)

SystemConfig = namedtuple('SystemConfig', "access_id access_key endpoint jmes_filter")

API_GROUP = [('project$', 'Project'), 'logstore', ('index|topics', "Index"),
             ('logtail_config', "Logtail Config"), ('machine', "Machine Group"), 'shard',
             'cursor', ('log|histogram', "Logs"), ('consumer|check_point', "Consumer Group"), 'shipper']

GLOBAL_OPTIONS_STR = """
Global Options:
[--access-id=<value>]		: use this access id in this command
[--access-key=<value>]		: use this access key in this command
[--region-endpoint=<value>]	: use this endpoint in this command
[--client-name=<value>]		: use this client name in configured accounts
[--jmes-filter=<value>]		: filter results using JMES syntax

Refer to http://aliyun-log-cli.readthedocs.io/ for more info.
"""

USAGE_STR_TEMPLATE = """
Usage:

1. aliyun log <subcommand> [parameters | global options]
2. aliyun configure <access_id> <access-key> <endpoint> [<client-name>]
3. aliyun [--help | --version]

Examples:

1. aliyun configure AKID123 AKKEY123 cn-hangzhou.log.aliyuncs.com
2. aliyun log create_project --project_name="test"

Subcommand:
{grouped_api}
""" + GLOBAL_OPTIONS_STR

MORE_DOCOPT_CMD = """aliyun configure <secure_id> <secure_key> <endpoint> [<client_name>]
"""


def load_config_from_file(client_name):
    # load config from file
    config = configparser.ConfigParser()
    config.read(LOG_CREDS_FILENAME)
    access_id, access_key, endpoint = '', '', ''

    if config.has_section(client_name):
        if six.PY3:
            access_id = config.get(client_name, 'access-id', fallback='')
            access_key = config.get(client_name, 'access-key', fallback='')
            endpoint = config.get(client_name, 'region-endpoint', fallback='')
        else:
            access_id = config.get(client_name, 'access-id', '')
            access_key = config.get(client_name, 'access-key', '')
            endpoint = config.get(client_name, 'region-endpoint', '')

    return access_id, access_key, endpoint


def load_default_config_from_file_env():
    access_id, access_key, endpoint = load_config_from_file(LOG_CONFIG_SECTION)

    # load config from envs
    access_id = os.environ.get('ALIYUN_LOG_CLI_ACCESSID', access_id)
    access_key = os.environ.get('ALIYUN_LOG_CLI_ACCESSKEY', access_key)
    endpoint = os.environ.get('ALIYUN_LOG_CLI_ENDPOINT', endpoint)

    return access_id, access_key, endpoint


def load_config(system_options):
    # load config from file
    config = configparser.ConfigParser()
    config.read(LOG_CREDS_FILENAME)

    # get section name
    client_name = LOG_CONFIG_SECTION
    client_name = os.environ.get('ALIYUN_LOG_CLI_CLIENT_NAME', client_name)
    client_name = system_options.get('client-name', client_name)

    access_id, access_key, endpoint = load_config_from_file(client_name)

    # load config from envs
    access_id = os.environ.get('ALIYUN_LOG_CLI_ACCESSID', access_id)
    access_key = os.environ.get('ALIYUN_LOG_CLI_ACCESSKEY', access_key)
    endpoint = os.environ.get('ALIYUN_LOG_CLI_ENDPOINT', endpoint)

    # load config from command lines
    access_id = system_options.get('access-id', access_id)
    access_key = system_options.get('secure-key', access_key)
    endpoint = system_options.get('region-endpoint', endpoint)

    assert access_id and access_key and endpoint, ValueError("Access id/key or endpoint is empty!")

    # load jmes filter from cmd
    jmes_filter = system_options.get('jmes-filter', '')
    if jmes_filter:
        try:
            jmespath.compile(jmes_filter)
        except jmespath.exceptions.ParseError as ex:
            print(ex)
            raise ValueError("Invalid JMES filter path")

    return SystemConfig(access_id, access_key, endpoint, jmes_filter)
