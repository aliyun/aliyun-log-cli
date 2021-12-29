import os
import json
from collections import namedtuple
import six.moves.configparser as configparser
import six
import jmespath
from jmespath.exceptions import ParseError
import logging
from logging.handlers import RotatingFileHandler
from .exceptions import IncompleteAccountInfoError
import requests
from aliyunsdkcore import client
from aliyunsdksts.request.v20150401 import AssumeRoleRequest

LOG_CLIENT_METHOD_BLACK_LIST = (r'_.+', r'\w+acl', 'set_source', 'delete_shard', 'heart_beat',
                                'set_user_agent', 'get_unicode', 'list_logstores', 'put_log_raw'
                                )

LOG_CREDS_FILENAME = "%s/.aliyunlogcli" % os.path.expanduser('~')
ALIYUN_CLI_CONF_FILENAME = "%s/.aliyun/config.json" % os.path.expanduser('~')
DEFAULT_DEBUG_LOG_FILE_PATH = "%s/aliyunlogcli.log" % os.path.expanduser('~')
DEFAULT_DEBUG_LOG_FORMAT = "%(asctime)s %(levelname)s %(process)s:%(threadName)s:%(filename)s:%(lineno)d %(funcName)s %(message)s"
ECS_RAM_ROLE_URL = "http://100.100.100.200/latest/meta-data/Ram/security-credentials/"

LOG_CONFIG_SECTION = "main"
GLOBAL_OPTION_SECTION = "__option__"
GLOBAL_OPTION_KEY_FORMAT_OUTPUT = "format-output"
GLOBAL_OPTION_KEY_DEFAULT_CLIENT = "default-client"
GLOBAL_OPTION_KEY_DECODE_OUTPUT = "decode-output"

STS_TOKEN_SEP = "::"

SYSTEM_OPTIONS = ['access-id', 'access-key', 'sts-token', 'region-endpoint', 'client-name', 'jmes-filter', 'format-output',
                  'decode-output', 'profile']
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
[--profile=<value>]	                : use the authentication mode in this command, specify authentication profile configured from Alibaba Cloud CLI.

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

    # access_id, access_key, endpoint = load_config_from_cloudshell()
    # sts_token = ""

    access_id = _get_section_option(config, client_name, 'access-id', "")
    access_key = _get_section_option(config, client_name, 'access-key', "")
    endpoint = _get_section_option(config, client_name, 'region-endpoint', "")
    sts_token = _get_section_option(config, client_name, 'sts-token', "")
    sts_token = verify_sts_token(access_id, "")

    return access_id, access_key, endpoint, sts_token


def load_default_config_from_file_env():
    access_id, access_key, endpoint, sts_token = load_confidential_from_file(LOG_CONFIG_SECTION)

    # load config from envs
    access_id = os.environ.get('ALIYUN_LOG_CLI_ACCESSID', access_id)
    access_key = os.environ.get('ALIYUN_LOG_CLI_ACCESSKEY', access_key)
    endpoint = os.environ.get('ALIYUN_LOG_CLI_ENDPOINT', endpoint)
    sts_token = os.environ.get('ALIYUN_LOG_CLI_STS_TOKEN', sts_token)

    return access_id, access_key, endpoint, sts_token

def parse_authenticity_from_response(response):
    if isinstance(response, bytes):
        response = response.decode()
    response = json.loads(response)
    credentials = response.get("Credentials")
    sts_token = credentials.get("SecurityToken", "")
    ak_id = credentials.get("AccessKeyId", "")
    ak_key = credentials.get("AccessKeySecret", "")
    return ak_id, ak_key, sts_token

def parse_xml_info_from_assumerole(access_id, access_key, endpoint, ram_role_arn):
    endpoint = endpoint.rstrip(".log.aliyuncs.com") if endpoint.endswith(".log.aliyuncs.com") else endpoint
    clt = client.AcsClient(access_id, access_key, endpoint)
    # 构造"AssumeRole"请求
    request = AssumeRoleRequest.AssumeRoleRequest()
    # 指定角色
    request.set_RoleArn(ram_role_arn)
    # 设置会话名称，审计服务使用此名称区分调用者
    request.set_RoleSessionName('etl-test')
    # 发起请求，并得到response
    response = clt.do_action_with_exception(request)
    ak_id, ak_key, sts_token = parse_authenticity_from_response(response)
    return ak_id, ak_key, sts_token

def parse_ecs_ram_role_authenticity_from_response(ram_role_name):
    url = ECS_RAM_ROLE_URL + ram_role_name
    response = requests.get(url)
    content = response.content
    if isinstance(content, bytes):
        content = content.decode()
    authenticity = json.loads(content)
    ak_id = authenticity.get("AccessKeyId", "")
    ak_key = authenticity.get("AccessKeySecret", "")
    sts_token = authenticity.get("SecurityToken", "")
    return ak_id, ak_key, sts_token

def load_confidential_from_aliyun_client_file(config_file, profile_mode='', ak_id="", ak_key="", endpoint="", sts_token=""):
    user_define_profile = True if profile_mode else False
    try:
        with open(config_file) as cf:
            cf_content = json.load(cf)
        current_profile = cf_content.get("current")
        profiles = cf_content.get("profiles")
        profile = None
        for _profile in profiles:
            profile_name = _profile.get("name")
            if (user_define_profile and profile_name == profile_mode) or (profile_name == current_profile and not user_define_profile):
                profile = _profile
                break
        current_mode = profile.get("mode")
        access_id = profile.get("access_key_id", ak_id)
        access_key = profile.get("access_key_secret", ak_key)
        endpoint = profile.get("region_id", endpoint)
        endpoint = endpoint + '.log.aliyuncs.com' if endpoint != "" else "cn-hangzhou.log.aliyuncs.com"
        sts_token = profile.get("sts_token", sts_token)
        #RamRoleArn config
        if current_mode == "RamRoleArn":
            ram_role_arn = profile.get("ram_role_arn")
            ak_id, ak_secret, sts_token = parse_xml_info_from_assumerole(access_id, access_key, endpoint, ram_role_arn)
            return ak_id, ak_secret, endpoint, sts_token
        #EcsRamRole config
        if current_mode == "EcsRamRole":
            ram_role_name = profile.get("ram_role_name")
            ak_id, ak_secret, sts_token = parse_ecs_ram_role_authenticity_from_response(ram_role_name)
            return ak_id, ak_secret, endpoint, sts_token
    except Exception as e:
        return "", "", "", ""
    return access_id, access_key, endpoint, sts_token


def load_config(system_options):
    access_id, access_key, endpoint, sts_token = '', '', '', ''
    # load config from file
    config = configparser.ConfigParser()
    config.read(LOG_CREDS_FILENAME)

    # get section name
    client_name = load_kv_from_file(GLOBAL_OPTION_SECTION, GLOBAL_OPTION_KEY_DEFAULT_CLIENT, LOG_CONFIG_SECTION) or LOG_CONFIG_SECTION
    client_name = os.environ.get('ALIYUN_LOG_CLI_CLIENT_NAME', client_name)
    client_name = system_options.get('client-name', client_name)
    format_output = load_kv_from_file(GLOBAL_OPTION_SECTION, GLOBAL_OPTION_KEY_FORMAT_OUTPUT, '')
    decode_output = load_kv_from_file(GLOBAL_OPTION_SECTION, GLOBAL_OPTION_KEY_DECODE_OUTPUT, ("utf8", "latin1"))

    #load config from aliyun cfg file
    _access_id, _access_key, _endpoint, _sts_token = load_confidential_from_aliyun_client_file(ALIYUN_CLI_CONF_FILENAME)
    endpoint = _endpoint or endpoint
    if all((_access_id, _access_key)):
        access_id, access_key, sts_token = _access_id, _access_key, _sts_token

    #load config from aliyun-cli envs
    alicloud_access_id, alicloud_access_key, alicloud_endpoint, alicloud_sts_token = os.environ.get('ALICLOUD_ACCESS_KEY_ID'), os.environ.get('ALICLOUD_ACCESS_KEY_SECRET'), \
        os.environ.get('ALICLOUD_REGION_ID'), os.environ.get('SECURITY_TOKEN')
    endpoint = alicloud_endpoint or endpoint
    if all((alicloud_access_id, alicloud_access_key)):
        access_id, access_key, sts_token = alicloud_access_id, alicloud_access_key, alicloud_sts_token

    alibabacloud_access_id, alibabacloud_access_key, alibabacloud_endpoint, alibabacloud_sts_token = os.environ.get('ALIBABACLOUD_ACCESS_KEY_ID'), os.environ.get('ALIBABACLOUD_ACCESS_KEY_SECRET'), \
        os.environ.get('ALIBABACLOUD_REGION_ID'), os.environ.get('SECURITY_TOKEN')
    endpoint = alibabacloud_endpoint or endpoint
    if all((alibabacloud_access_id, alibabacloud_access_key)):
        access_id, access_key, sts_token = alibabacloud_access_id, alibabacloud_access_key, alibabacloud_sts_token

    #load config from cloudshell envs
    alicloud_access_id, alicloud_access_key, alicloud_endpoint, alicloud_sts_token = os.environ.get('ALICLOUD_ACCESS_KEY'), os.environ.get('ALICLOUD_SECRET_KEY'), \
        os.environ.get('ALICLOUD_REGION'), os.environ.get('SECURITY_TOKEN')
    endpoint = alicloud_endpoint or endpoint
    if all((alicloud_access_id, alicloud_access_key)):
        access_id, access_key, sts_token = alicloud_access_id, alicloud_access_key, alicloud_sts_token

    alibabacloud_access_id, alibabacloud_access_key, alibabacloud_endpoint, alibabacloud_sts_token = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID'), os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_SECRET'), \
        os.environ.get('ALIBABA_CLOUD_DEFAULT_REGION'), os.environ.get('ALIBABA_CLOUD_SECURITY_TOKEN')
    endpoint = alibabacloud_endpoint or endpoint
    if all((alibabacloud_access_id, alibabacloud_access_key)):
        access_id, access_key, sts_token = alibabacloud_access_id, alibabacloud_access_key, alibabacloud_sts_token

    if endpoint and not endpoint.endswith('.com'):
        endpoint = endpoint + '.log.aliyuncs.com'

    #load config from sls cfg file
    sls_access_id, sls_access_key, sls_endpoint, sls_sts_token = load_confidential_from_file(client_name)
    endpoint = sls_endpoint or endpoint
    if all((sls_access_id, sls_access_key)):
        access_id, access_key, sts_token = sls_access_id, sls_access_key, sls_sts_token

    # load config from sls envs
    aliyun_access_id, aliyun_access_key, aliyun_endpoint, aliyun_sts_token = os.environ.get('ALIYUN_LOG_CLI_ACCESSID'), os.environ.get('ALIYUN_LOG_CLI_ACCESSKEY'), \
        os.environ.get('ALIYUN_LOG_CLI_ENDPOINT'), os.environ.get('ALIYUN_LOG_CLI_STS_TOKEN')
    endpoint = aliyun_endpoint or endpoint
    if all((aliyun_access_id, aliyun_access_key)):
        access_id, access_key, sts_token = aliyun_access_id, aliyun_access_key, aliyun_sts_token
    format_output = os.environ.get('ALIYUN_LOG_CLI_FORMAT_OUTPUT', format_output)
    decode_output = os.environ.get('ALIYUN_LOG_CLI_DECODE_OUTPUT', decode_output)

    # load config from profile mode
    profile = system_options.get('profile', '')
    if profile:
        pro_access_id, pro_access_key, pro_endpoint, pro_sts_token = load_confidential_from_aliyun_client_file(ALIYUN_CLI_CONF_FILENAME, profile_mode=profile)
        endpoint = pro_endpoint or endpoint
        if all((pro_access_id, pro_access_key)):
            access_id, access_key, sts_token = pro_access_id, pro_access_key, pro_sts_token

    # load config from command lines
    _access_id, _access_key, _endpoint, _sts_token = system_options.get('access-id'), system_options.get('access-key'), \
                                                     system_options.get('region-endpoint'), system_options.get('sts-token')
    endpoint = _endpoint or endpoint
    if all((_access_id, _access_key)):
        access_id, access_key, sts_token = _access_id, _access_key, _sts_token
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

