import os
from collections import namedtuple
import six.moves.configparser as configparser
import six
import jmespath
from jmespath.exceptions import ParseError
import logging
from logging.handlers import RotatingFileHandler
from .exceptions import IncompleteAccountInfoError

LOG_CLIENT_METHOD_BLACK_LIST = (r'_.+', r'\w+acl', 'set_source', 'delete_shard', 'heart_beat',
                                'set_user_agent', 'get_unicode', 'list_logstores', 'put_log_raw'
                                )

LOG_CREDS_FILENAME = "%s/.aliyunlogcli" % os.path.expanduser('~')
DEFAULT_DEBUG_LOG_FILE_PATH = "%s/aliyunlogcli.log" % os.path.expanduser('~')
DEFAULT_DEBUG_LOG_FORMAT = "%(asctime)s %(levelname)s %(process)s:%(threadName)s:%(filename)s:%(lineno)d %(funcName)s %(message)s"

LOG_CONFIG_SECTION = "main"
GLOBAL_OPTION_SECTION = "__option__"
GLOBAL_OPTION_KEY_FORMAT_OUTPUT = "format-output"
GLOBAL_OPTION_KEY_DEFAULT_CLIENT = "default-client"
GLOBAL_OPTION_KEY_DECODE_OUTPUT = "decode-output"

STS_TOKEN_SEP = "::"

SYSTEM_OPTIONS = ['access-id', 'access-key', 'sts-token', 'region-endpoint', 'client-name', 'jmes-filter', 'format-output',
                  'decode-output']
SYSTEM_OPTIONS_STR = ' '.join('[--' + x + '=<value>]' for x in SYSTEM_OPTIONS)

SystemConfig = namedtuple('SystemConfig', "access_id access_key endpoint sts_token, jmes_filter format_output decode_output")

API_GROUP = [('project$', 'Project'), 'logstore', ('index|topics', "Index"),
             ('logtail_config', "Logtail Config"), ('machine', "Machine Group"), 'shard',
             'cursor', ('log|histogram', "Logs"), ('consumer|check_point', "Consumer Group"), 'shipper',
             'dashboard', 'savedsearch', 'alert', ('external_store', "External Store")]

GLOBAL_OPTIONS_STR = """
Global Options:
[--access-id=<value>]		        : use this access id in this command
[--access-key=<value>]		        : use this access key in this command
[--sts-token=<value>]		        : use this sts token in this command
[--region-endpoint=<value>]	        : use this endpoint in this command
[--client-name=<value>]		        : use this client name in configured accounts
[--jmes-filter=<value>]		        : filter results using JMES syntax
[--format-output=json,no_escape]    : print formatted json results or else print in one line; if escape non-ANSI or not with `no_escape`. like: "json", "json,no_escape", "no_escape"
[--decode-output=<value>]	        : encoding list to decode response, comma separated like "utf8,lartin1,gbk", default is "utf8". 

Refer to http://aliyun-log-cli.readthedocs.io/ for more info.
"""

USAGE_STR_TEMPLATE = """
Usage:

1. aliyunlog log <subcommand> [parameters | global options]
2. aliyunlog configure <access_id> <access_key> <endpoint> [<client-name>] [sts_token]
3. aliyunlog configure [--format-output=json,no_escape] [--default-client=<client_name>] [--decode-output=utf8,latin1]
4. aliyunlog [--help | --version]


Examples:

1. aliyunlog configure AKID123 AKKEY123 cn-hangzhou.log.aliyuncs.com
2. aliyunlog configure --format-output=json,no_escape --default-client=beijing
3. aliyunlog log create_project --project_name="test"
4. aliyunlog configure AKID124 AKKey123 cn-hangzhou.log.aliyuncs.com main StsTokenValue1234

Subcommand:
{grouped_api}
""" + GLOBAL_OPTIONS_STR

MORE_DOCOPT_CMD = """aliyunlog configure <secure_id> <secure_key> <endpoint> [<client_name>] [<sts_token>]
aliyunlog configure [--format-output=json,no_escape] [--default-client=<client_name>] [--decode-output=utf8,latin1]
"""

DEBUG_SECTION_NAME = "__logging__"


def _get_section_option(config, section_name, option_name, default=None):
    if six.PY3:
        return config.get(section_name, option_name, fallback=default)
    else:
        return config.get(section_name, option_name) if config.has_option(section_name, option_name) else default


def load_kv_from_file(section, key, default=None):
    # load key value from file
    config = configparser.SafeConfigParser()
    config.read(LOG_CREDS_FILENAME)

    return _get_section_option(config, section, key, default)


def load_config_from_cloudshell(default_ak_id='', default_ak_key='', default_endpoint=''):
    # Cloudshell envs
    access_id = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID', default_ak_id)
    access_key = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_SECRET', default_ak_key)
    endpoint = os.environ.get('ALIBABA_CLOUD_DEFAULT_REGION', default_endpoint)
    if endpoint and not endpoint.endswith('.com'):
        endpoint = endpoint + '.log.aliyuncs.com'

    return access_id, access_key, endpoint


def verify_sts_token(ac_id, sts_token, use=False):
    sts_token = sts_token or ""

    if sts_token:
        if STS_TOKEN_SEP in sts_token:
            if sts_token.startswith(ac_id):
                if not use:
                    return sts_token
                else:
                    v = sts_token.split(STS_TOKEN_SEP)[1]
                    if not v:
                        v = None
                    return v
        else:
            if not use:
                return ac_id + STS_TOKEN_SEP + sts_token
            else:
                return sts_token

    if use:
        return None
    else:
        return ""


def load_confidential_from_file(client_name):
    # load config from file
    config = configparser.ConfigParser()
    config.read(LOG_CREDS_FILENAME)

    access_id, access_key, endpoint = load_config_from_cloudshell()
    sts_token = ""

    access_id = _get_section_option(config, client_name, 'access-id', access_id)
    access_key = _get_section_option(config, client_name, 'access-key', access_key)
    endpoint = _get_section_option(config, client_name, 'region-endpoint', endpoint)
    sts_token = _get_section_option(config, client_name, 'sts-token', sts_token)
    sts_token = verify_sts_token(access_id, sts_token)

    return access_id, access_key, endpoint, sts_token


def load_default_config_from_file_env():
    access_id, access_key, endpoint, sts_token = load_confidential_from_file(LOG_CONFIG_SECTION)

    # load config from envs
    access_id = os.environ.get('ALIYUN_LOG_CLI_ACCESSID', access_id)
    access_key = os.environ.get('ALIYUN_LOG_CLI_ACCESSKEY', access_key)
    endpoint = os.environ.get('ALIYUN_LOG_CLI_ENDPOINT', endpoint)
    sts_token = os.environ.get('ALIYUN_LOG_CLI_STS_TOKEN', sts_token)

    return access_id, access_key, endpoint, sts_token


def load_config(system_options):
    # load config from file
    config = configparser.ConfigParser()
    config.read(LOG_CREDS_FILENAME)

    # get section name
    client_name = load_kv_from_file(GLOBAL_OPTION_SECTION, GLOBAL_OPTION_KEY_DEFAULT_CLIENT, LOG_CONFIG_SECTION) or LOG_CONFIG_SECTION
    client_name = os.environ.get('ALIYUN_LOG_CLI_CLIENT_NAME', client_name)
    client_name = system_options.get('client-name', client_name)
    format_output = load_kv_from_file(GLOBAL_OPTION_SECTION, GLOBAL_OPTION_KEY_FORMAT_OUTPUT, '')
    decode_output = load_kv_from_file(GLOBAL_OPTION_SECTION, GLOBAL_OPTION_KEY_DECODE_OUTPUT, ("utf8", "latin1"))

    access_id, access_key, endpoint, sts_token = load_confidential_from_file(client_name)

    # load config from envs
    access_id = os.environ.get('ALIYUN_LOG_CLI_ACCESSID', access_id)
    access_key = os.environ.get('ALIYUN_LOG_CLI_ACCESSKEY', access_key)
    endpoint = os.environ.get('ALIYUN_LOG_CLI_ENDPOINT', endpoint)
    sts_token = os.environ.get('ALIYUN_LOG_CLI_STS_TOKEN', sts_token)
    format_output = os.environ.get('ALIYUN_LOG_CLI_FORMAT_OUTPUT', format_output)
    decode_output = os.environ.get('ALIYUN_LOG_CLI_DECODE_OUTPUT', decode_output)

    # load config from command lines
    access_id = system_options.get('access-id', access_id)
    access_key = system_options.get('access-key', access_key)
    endpoint = system_options.get('region-endpoint', endpoint)
    sts_token = system_options.get('sts-token', sts_token)
    format_output = system_options.get('format-output', format_output)
    decode_output = system_options.get('decode-output', decode_output)

    if not (access_id and access_key and endpoint):
        raise IncompleteAccountInfoError("Access id/key or endpoint is empty!")

    # load jmes filter from cmd
    jmes_filter = system_options.get('jmes-filter', '')
    if jmes_filter:
        try:
            jmespath.compile(jmes_filter)
        except jmespath.exceptions.ParseError as ex:
            print(ex)
            raise ValueError("Invalid JMES filter path")

    return SystemConfig(access_id, access_key, endpoint, sts_token, jmes_filter, format_output, decode_output)


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


def config_logging_from_config_file():
    # load debug config from file
    config = configparser.RawConfigParser()
    config.read(LOG_CREDS_FILENAME)

    filename = DEFAULT_DEBUG_LOG_FILE_PATH
    level = "warn"          # use string first
    fmt = DEFAULT_DEBUG_LOG_FORMAT
    datefmt = None
    filebytes = 100 * 1024 * 1024
    backupcount = 5

    client_name = DEBUG_SECTION_NAME
    if config.has_section(client_name):
        filename = _get_section_option(config, client_name, 'filename', filename)
        level = _get_section_option(config, client_name, 'level', level)
        fmt = _get_section_option(config, client_name, 'format', fmt)
        datefmt = _get_section_option(config, client_name, 'datefmt', datefmt)
        filebytes = int(_get_section_option(config, client_name, 'filebytes', filebytes))
        backupcount = int(_get_section_option(config, client_name, 'backupcount', backupcount))

    root = logging.getLogger()
    handler = RotatingFileHandler(filename, maxBytes=filebytes, backupCount=backupcount)
    root.setLevel(__LOGGING_LEVEL_MAP.get(level.lower().strip(), logging.WARN))
    root.addHandler(handler)
    handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))


class monkey_patch(object):
    def __init__(self, src_obj, src_prop, dst=None):
        self.src_obj = src_obj
        self.src_prop = src_prop
        self.activated = False

        if hasattr(self.src_obj, self.src_prop):
            self.origin = getattr(self.src_obj, self.src_prop)
            setattr(self.src_obj, self.src_prop, dst)
            self.activated = True

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.activated:
            setattr(self.src_obj, self.src_prop, self.origin)

