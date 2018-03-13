import os
from collections import namedtuple
import six.moves.configparser as configparser
import six
import jmespath
from jmespath.exceptions import ParseError
import logging

LOG_CLIENT_METHOD_BLACK_LIST = (r'_.+', r'\w+acl', 'set_source', 'delete_shard', 'heart_beat',
                                'set_user_agent', 'get_unicode', 'list_logstores'
                                )

LOG_CREDS_FILENAME = "%s/.aliyunlogcli" % os.path.expanduser('~')
DEFAULT_DEBUG_LOG_FILE_PATH = "%s/aliyunlogcli.log" % os.path.expanduser('~')
DEFAULT_DEBUG_LOG_FORMAT = "%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(funcName)s %(message)s"

LOG_CONFIG_SECTION = "main"
GLOBAL_OPTION_SECTION = "__option__"
GLOBAL_OPTION_KEY_FORMAT_OUTPUT = "format-output"
GLOBAL_OPTION_KEY_DEFAULT_CLIENT = "default-client"

SYSTEM_OPTIONS = ['access-id', 'access-key', 'region-endpoint', 'client-name', 'jmes-filter', 'format-output']
SYSTEM_OPTIONS_STR = ' '.join('[--' + x + '=<value>]' for x in SYSTEM_OPTIONS)

SystemConfig = namedtuple('SystemConfig', "access_id access_key endpoint jmes_filter format_output")

API_GROUP = [('project$', 'Project'), 'logstore', ('index|topics', "Index"),
             ('logtail_config', "Logtail Config"), ('machine', "Machine Group"), 'shard',
             'cursor', ('log|histogram', "Logs"), ('consumer|check_point', "Consumer Group"), 'shipper',
             'dashboard', 'savedsearch', 'alert']

GLOBAL_OPTIONS_STR = """
Global Options:
[--access-id=<value>]		: use this access id in this command
[--access-key=<value>]		: use this access key in this command
[--region-endpoint=<value>]	: use this endpoint in this command
[--client-name=<value>]		: use this client name in configured accounts
[--jmes-filter=<value>]		: filter results using JMES syntax
[--format-output=json]		: print formatted json results or else print in one line

Refer to http://aliyun-log-cli.readthedocs.io/ for more info.
"""

USAGE_STR_TEMPLATE = """
Usage:

1. aliyunlog log <subcommand> [parameters | global options]
2. aliyunlog configure <access_id> <access-key> <endpoint> [<client-name>]
3. aliyunlog configure [--format-output=json] [--default-client=<client_name>]
4. aliyunlog [--help | --version]

Examples:

1. aliyunlog configure AKID123 AKKEY123 cn-hangzhou.log.aliyuncs.com
2. aliyunlog configure --format-output=json --default-client=beijing
3. aliyunlog log create_project --project_name="test"

Subcommand:
{grouped_api}
""" + GLOBAL_OPTIONS_STR

MORE_DOCOPT_CMD = """aliyun configure <secure_id> <secure_key> <endpoint> [<client_name>]
aliyun configure [--format-output=json] [--default-client=<client_name>]
"""

DEBUG_SECTION_NAME = "__logging__"


def load_kv_from_file(section, key, default=None):
    # load key value from file
    config = configparser.ConfigParser()
    config.read(LOG_CREDS_FILENAME)

    if config.has_section(section):
        if six.PY3:
            return config.get(section, key, fallback=default)
        else:
            return config.get(section, key, default)

    return default


def load_confidential_from_file(client_name):
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
    access_id, access_key, endpoint = load_confidential_from_file(LOG_CONFIG_SECTION)

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
    client_name = load_kv_from_file(GLOBAL_OPTION_SECTION, GLOBAL_OPTION_KEY_DEFAULT_CLIENT, LOG_CONFIG_SECTION) or LOG_CONFIG_SECTION
    client_name = os.environ.get('ALIYUN_LOG_CLI_CLIENT_NAME', client_name)
    client_name = system_options.get('client-name', client_name)
    format_output = load_kv_from_file(GLOBAL_OPTION_SECTION, GLOBAL_OPTION_KEY_FORMAT_OUTPUT, '')

    access_id, access_key, endpoint = load_confidential_from_file(client_name)

    # load config from envs
    access_id = os.environ.get('ALIYUN_LOG_CLI_ACCESSID', access_id)
    access_key = os.environ.get('ALIYUN_LOG_CLI_ACCESSKEY', access_key)
    endpoint = os.environ.get('ALIYUN_LOG_CLI_ENDPOINT', endpoint)
    format_output = os.environ.get('ALIYUN_LOG_CLI_FORMAT_OUTPUT', format_output)

    # load config from command lines
    access_id = system_options.get('access-id', access_id)
    access_key = system_options.get('access-key', access_key)
    endpoint = system_options.get('region-endpoint', endpoint)
    format_output = system_options.get('format-output', format_output)

    assert access_id and access_key and endpoint, ValueError("Access id/key or endpoint is empty!")

    # load jmes filter from cmd
    jmes_filter = system_options.get('jmes-filter', '')
    if jmes_filter:
        try:
            jmespath.compile(jmes_filter)
        except jmespath.exceptions.ParseError as ex:
            print(ex)
            raise ValueError("Invalid JMES filter path")

    return SystemConfig(access_id, access_key, endpoint, jmes_filter, format_output)


def _get_section_option(config, section_name, option_name, default=None):
    if six.PY3:
        return config.get(section_name, option_name, fallback=default)
    else:
        return config.get(section_name, option_name) if config.has_option(section_name, option_name) else default


__LOGGING_LEVEL_MAP = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARN,
    "warning": logging.WARN,
    "information": logging.INFO,
    "error": logging.ERROR,
    "err": logging.ERROR,
    "critical": logging.CRITICAL,
    "fat": logging.FATAL,
    "fatal": logging.FATAL
}


def load_debug_from_config_file():
    # load debug config from file
    config = configparser.RawConfigParser()
    config.read(LOG_CREDS_FILENAME)

    opt = {"filename": DEFAULT_DEBUG_LOG_FILE_PATH, "level": logging.WARN, "format": DEFAULT_DEBUG_LOG_FORMAT}
    client_name = DEBUG_SECTION_NAME
    if config.has_section(client_name):
        filename = _get_section_option(config, client_name, 'filename', None)
        level = _get_section_option(config, client_name, 'level', None)
        filemode = _get_section_option(config, client_name, 'filemode', None)
        fmt = _get_section_option(config, client_name, 'format', None)
        datefmt = _get_section_option(config, client_name, 'datefmt', None)

        if filename is not None:
            opt['filename'] = filename
        if filemode is not None:
            opt['filemode'] = filemode
        if fmt is not None:
            opt['format'] = fmt
        if datefmt is not None:
            opt['datefmt'] = datefmt

        opt['level'] = __LOGGING_LEVEL_MAP.get(level.lower().strip(), logging.WARN)

    return opt
