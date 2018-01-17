# 用户手册

[![Documentation Status](https://readthedocs.org/projects/aliyun-log-cli/badge/?version=latest)](http://aliyun-log-cli.readthedocs.io/?badge=latest)
[![Pypi Version](https://badge.fury.io/py/aliyun-log-cli.svg)](https://badge.fury.io/py/aliyun-log-cli)
[![Travis CI](https://travis-ci.org/aliyun/aliyun-log-cli.svg?branch=master)](https://travis-ci.org/aliyun/aliyun-log-cli)
[![Development Status](https://img.shields.io/pypi/status/aliyun-log-cli.svg)](https://pypi.python.org/pypi/aliyun-log-cli/)
[![Python version](https://img.shields.io/pypi/pyversions/aliyun-log-cli.svg)](https://pypi.python.org/pypi/aliyun-log-cli/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/aliyun/aliyun-log-python-sdk/blob/master/LICENSE)

[README in English](https://github.com/aliyun/aliyun-log-cli/blob/master/README.md)

<h1 id="内容">内容</h1>
* [用户手册](#内容)
    * [简介](#简介)
      * [基本介绍](#基本介绍)
      * [主要功能](#主要功能)
    * [安装](#安装)
      * [操作系统](#操作系统)
      * [支持版本](#支持版本)
      * [安装方式](#安装方式)
      * [完整参数列表](#完整参数列表)
    * [配置说明](#配置说明)
      * [配置AK与服务入口](#配置ak与服务入口)
      * [修改配置文件](#修改配置文件)
      * [多账户](#多账户)
    * [输入输出](#输入输出)
      * [输入](#输入)
      * [参数校验](#参数校验)
      * [输出](#输出)
      * [输出过滤](#输出过滤)
    * [命令参考](#命令参考)
      * [命令规范](#命令规范)
         * [命令别名](#命令别名)
         * [子命令与参数](#子命令与参数)
         * [全局选项](#全局选项)
      * [命令类别](#命令类别)
         * [项目组管理](#1-项目组管理)
         * [日志库管理](#2-日志库管理)
         * [分区管理](#3-分区管理)
         * [机器组管理](#4-机器组管理)
         * [Logtail配置管理](#5-客户端配置管理)
         * [机器组与Logtail配置关联](#6-机器组与客户端配置关联)
         * [索引管理](#7-索引管理)
         * [游标操作](#8-游标操作)
         * [日志读写与消费](#9-日志读写与消费)
         * [投递管理](#10-投递管理)
         * [消费组管理](#11-消费组管理)
    * [错误诊断](#错误诊断)
    * [其他资源](#其他资源)
    

<h1 id="简介">简介</h1>

日志服务(SLS)提供了Web和SDK的方式进行日志采集、管理、查询和分析。为了满足越来越多的的自动化日志配置查询分析的需求，现重磅发布SLS的命令行工具(Command Line Interface - CLI)。

<h2 id="基本介绍">基本介绍</h2>

日志服务命令行工具CLI支持几乎所有操作，日志查询支持完整性检查与自动分页、支持多账户与跨域复制。

<h2 id="主要功能">主要功能</h2>

- 支持大部分的日志服务REST接口。
- 支持多账号，方便测试与跨域操作。
- 日志查询完整性查询与自动分页。
- 支持多种方式存储和配置秘钥，适用于各种情况。
- 支持通过命令行或者文件的形式输入复杂参数，并校验参数内容格式。
- 支持JMES过滤器对结果进行进一步处理，方便选择特定信息。
- 跨平台（Windows/Linux和Mac）支持，基于Python（Py2.6+和Py3.3+平台友好），支持Pip安装。


<h1 id="安装">安装</h1>

<h2 id="操作系统">操作系统</h2>

日志服务CLI支持以下操作系统：

- Windows
- Mac OS
- Linux

<h2 id="支持版本">支持版本</h2>

Python 2.6、2.7、3.3、3.4、3.5、3.6、PyPy和PyPy3。

<h2 id="安装方式">安装方式</h2>

执行以下命令安装日志服务CLI。

```shell
> pip install -U aliyun-log-cli
```

<h2 id="完整参数列表">完整参数列表</h2>

执行以下命令查看日志服务CLI参数列表。
```shell
> aliyun --help
```

<h1 id="配置说明">配置说明</h1>

参考[SDK配置](https://help.aliyun.com/document_detail/29064.html?spm=5176.doc29068.2.8.SWJhYZ)获得访问秘钥的ID和Key以及访问入口Endpoint，构建一个LogClient的客户端。


<h2 id="配置AK与服务入口">配置AK与服务入口</h2>

日志服务CLI支持通过以下三种方式配置访问秘钥与入口，如果同时配置多种方式, 优先顺序是: 参数, 环境变量, 最后是本地配置文件. 

- 参数

```shell
> aliyun log create_project ..... --access-id=<value> --access-key=<value> --endpoint=<value>
```

  **注意:** 任意log子命令都支持以上方式定义特定的AK与Endpoint(覆盖后面的方式)


- 环境变量

  - ALIYUN_LOG_CLI_ACCESSID
  - ALIYUN_LOG_CLI_ACCESSKEY
  - ALIYUN_LOG_CLI_ENDPOINT

- 本地配置文件

  将存储AK与Endpoint在~/.aliyunlogcli, 默认使用的块名是`main`

```ini
[main]
access-id=
access-key=
endpoint=
```

<h2 id="修改配置文件">修改配置文件</h2>

Configure命令可以修改配置文件内容.

```shell
> aliyun configure access_id access_key cn-beijing.log.aliyun.com
```

<h2 id="多账户">多账户</h2>

1. 存储于多个账户, 以便在特定情况下使用(例如测试):

```shell
> aliyun configure access_id1 access_key1 cn-beijing.log.aliyun.com
> aliyun configure access_id2 access_key2 cn-hangzhou.log.aliyun.com test
```

  AK将存储为:

```ini
[main]
access-id=access_id1
access-key=access_key1
endpoint=cn-beijing.log.aliyun.com

[test]
access-id=access_id2
access-key=access_key2
endpoint=cn-hangzhou.log.aliyun.com
```

2. 使用特定账户

任意命令都可以通过选项`--client-name=<value>`来使用特定配置的账户, 例如:

```shell
> aliyun log create_project ..... --client-name=test
```

将使用`test`的AK来进行操作.

3. 其他情况

某些情况下也需要跨账户操作, 例如:

```shell
> aliyun log copy_project --from_project="p1" --to_project="p1" --to_client=test
```

将`main`账户下对应的项目`p1`复制到账户`test`下的`p1`


<h1 id="输入输出">输入输出</h1>

<h2 id="输入">输入</h2>

1. 一般输入

```shell
> aliyun log get_logs --request="{\"topic\": \"\", \"logstore\": \"logstore1\", \"project\": \"dlq-test-cli-123\", \"toTime\": \"123\", \"offset\": \"0\", \"query\": \"*\", \"line\": \"10\", \"fromTime\": \"123\", \"reverse\":\"false\"}"
```

2. 文件输入

也可以将上面参数放到一个文件里面, 简化命令行, 需要义`file://`开头+文件路径即可:

```shell
> aliyun log get_logs --request="file://./get_logs.json"
```


文件`get_logs.json`内容如下, 注意: 文件中不需要反斜杠`\`来转义.

```json
{
  "topic": "",
  "logstore": "logstore1",
  "project": "project1",
  "toTime": "12345679",
  "offset": "0",
  "query": "*",
  "line": "10",
  "fromTime": "1234567",
  "reverse": "true"
}
```

<h2 id="参数校验">参数校验</h2>

- 必填的参数没有填写时会报错, 输出参数列表

- 参数格式本身会进行校验, 例如int, bool, string list, 特定数据结构等

- bool支持的形式有:

  - true (大小写不敏感), T, 1
  - false (大小写不敏感), F, 0

- 字符串列表支持的形式为["s1", "s2"]


<h2 id="输出">输出</h2>

1. 对于Create, Update, Delete操作, 一般脚本无输出, exit code=0表示成功.

2. 对于Get/List操作, 以json格式输出内容

3. 错误情况下, 以如下格式返回错误:

```json
{
  "errorCode":"...",
  "errorMessage":"..."
}
```

<h2 id="输出过滤">输出过滤</h2>

支持通过[JMES](http://jmespath.org/)过滤输出的结果.

例如:

```shell
> aliyun log get_logs ...
```

以上命令的输出是:

```json
{
  "count": 3,
   "logstores": ["logstore3", "logstore1", "logstore2"],
   "total": 3
}
```

通过以下命令可以获取第二以及后面的Logstore的名字: 

```shell
> aliyun log get_logs ... --jmes-filter="logstores[2:]"
```

输出:

```shell
["logstore1", "logstore2"]
```

<h1 id="命令参考">命令参考</h1>

<h2 id="命令规范">命令规范</h2>

```shell
1. aliyun log <subcommand> [parameters | global options]
2. aliyun configure <access_id> <access-key> <endpoint> [<client-name>]
3. aliyun [--help | --version]
```


<h2 id="命令别名">命令别名</h2>
日志服务的CLI也有一个别名`aliyunlog`, 如果`aliyun`这个命令冲突了, 可以尝试使用`aliyunlog`:

```shell
1. aliyunlog log <subcommand> [parameters | global options]
2. aliyunlog configure <access_id> <access-key> <endpoint>
3. aliyunlog [--help | --version]
```

<h2 id="子命令与参数">子命令与参数</h2>

日志服务命令行工具背后依赖于日志服务的Python SDK, 相关子命令对应于`aliyun.log.LogClient`的方法, 参数和可选参数也一一对应.
具体支持的API参数, 请参考[映射的Python SDK API](http://aliyun-log-cli.readthedocs.io/en/latest/api.html)

**例子:**

```python
def create_logstore(self, project_name, logstore_name, ttl=2, shard_count=30):
```

对应命令行:

```shell
> aliyun log create_logstore
  --project_name=<value>
  --logstore_name=<value>
  [--ttl=<value>]
  [--shard_count=<value>]
```

<h2 id="全局选项">全局选项</h2>

所有命令都支持如下的全局选项:

```
    [--access-id=<value>]
    [--access-key=<value>]
    [--region-endpoint=<value>]
    [--client-name=<value>]
    [--jmes-filter=<value>]
```

<h2 id="命令类别">命令类别</h2>

 1. [项目组管理](#1-项目组管理)
 2. [日志库管理](#2-日志库管理)
 3. [分区管理](#3-分区管理)
 4. [机器组管理](#4-机器组管理)
 5. [Logtail配置管理](#5-客户端配置管理)
 6. [机器组与Logtail配置关联](#6-机器组与客户端配置关联)
 7. [索引管理](#7-索引管理)
 8. [游标操作](#8-游标操作)
 9. [日志读写与消费](#9-日志读写与消费)
 10. [投递管理](#10-投递管理)
 11. [消费组管理](#11-消费组管理)

<h3 id="1-项目组管理">1. 项目组管理</h3>

- list_project
- create_project
- get_project
- delete_project
- **copy_project**
  - 复制所有源project的logstore, logtail, machine group和index配置等到目标project中.

```shell
> aliyun log copy_project --from_project="p1" --to_project="p1" --to_client="account2"
```

  - 注意: `to_client`是通过aliyun configure配置的其他账户, 也可以不传或传`main`同域复制.
  - 参考[跨域复制项目组配置](./tutorials/tutorial_manage_cross_region_copy.html)了解如何跨域复制项目组配置.

<h3 id="2-日志库管理">2. 日志库管理</h3>

- create_logstore
- delete_logstore
- get_logstore
- update_logstore
- list_logstore


<h3 id="3-分区管理">3. 分区管理</h3>

- list_shards
- split_shard
- merge_shard



<h3 id="4-机器组管理">4. 机器组管理</h3>

- create_machine_group
   - 部分参数格式:

```json
{
 "machine_list": [
   "machine1",
   "machine2"
 ],
 "machine_type": "userdefined",
 "group_name": "group_name2",
 "group_type": "Armory",
 "group_attribute": {
   "externalName": "ex name",
   "groupTopic": "topic x"
 }
}
```

- delete_machine_group
- update_machine_group
- get_machine_group
- list_machine_group
- list_machines

<h3 id="5-客户端配置管理">5. Logtail配置管理</h3>

- create_logtail_config
   - 参考[创建Logtail配置](./tutorials/tutorial_create_logtail_config.html)了解如何创建各种格式的Logtail配置.
- update_logtail_config
- delete_logtail_config
- get_logtail_config
- list_logtail_config


<h3 id="6-机器组与客户端配置关联">6. 机器组与Logtail配置关联</h3>

- apply_config_to_machine_group
- remove_config_to_machine_group
- get_machine_group_applied_configs
- get_config_applied_machine_groups


<h3 id="7-索引管理">7. 索引管理</h3>

- create_index
   - 部分参数格式:

```json
{
 "keys": {
   "f1": {
     "caseSensitive": false,
     "token": [
       ",",
       " ",
       "\"",
       "\"",
       ";",
       "=",
       "(",
       ")",
       "[",
       "]",
       "{",
       "}",
       "?",
       "@",
       "&",
       "<",
       ">",
       "/",
       ":",
       "\n",
       "\t"
     ],
     "type": "text",
     "doc_value": true
   },
   "f2": {
     "doc_value": true,
     "type": "long"
   }
 },
 "storage": "pg",
 "ttl": 2,
 "index_mode": "v2",
 "line": {
   "caseSensitive": false,
   "token": [
     ",",
     " ",
     "\"",
     "\"",
     ";",
     "=",
     "(",
     ")",
     "[",
     "]",
     "{",
     "}",
     "?",
     "@",
     "&",
     "<",
     ">",
     "/",
     ":",
     "\n",
     "\t"
   ]
 }
}
```

- update_index
- delete_index
- get_index_config
- list_topics

<h3 id="8-游标操作">8. 游标操作</h3>

- get_cursor
- get_cursor_time
- get_previous_cursor_time
- get_begin_cursor
- get_end_cursor

<h3 id="9-日志读写与消费">9. 日志读写与消费</h3>

- put_logs
  - 参数格式:

```json
{
"project": "dlq-test-cli-35144",
"logstore": "logstore1",
"topic": "topic1",
"source": "source1",
"logtags": [
  [
    "tag1",
    "v1"
  ],
  [
    "tag2",
    "v2"
  ]
],
"hashKey": "1231231234",
"logitems": [
  {
    "timestamp": 1510579341,
    "contents": [
      [
        "key1",
        "v1"
      ],
      [
        "key2",
        "v2"
      ]
    ]
  },
  {
    "timestamp": 1510579341,
    "contents": [
      [
        "key3",
        "v3"
      ],
      [
        "key4",
        "v4"
      ]
    ]
  }
]
}
```

- get_logs
  - 参数格式:

```json
{
"topic": "",
"logstore": "logstore1",
"project": "dlq-test-cli-35144",
"toTime": "1510582941",
"offset": "0",
"query": "*",
"line": "10",
"fromTime": "1510579341",
"reverse": "true"
}
```

- get_histograms
- pull_logs

<h3 id="10-投递管理">10. 投递管理</h3>

- create_shipper
  - 部分参数格式:

```json
{
"oss_bucket": "dlq-oss-test1",
"oss_prefix": "sls",
"oss_role_arn": "acs:ram::1234:role/aliyunlogdefaultrole",
"buffer_interval": 300,
"buffer_mb": 128,
"compress_type": "snappy"
}
```

- update_shipper
- delete_shipper
- get_shipper_config
- list_shipper
- get_shipper_tasks
- retry_shipper_tasks

<h3 id="11-消费组管理">11. 消费组管理</h3>

- create_consumer_group
- update_consumer_group
- delete_consumer_group
- list_consumer_group
- update_check_point
- get_check_point


<h1 id="错误诊断">错误诊断</h1>

CLI默认把执行过程中的警告和错误存储在`~/aliyunlogcli.log`中, 也可以配置~/.aliyunlogcli中`__loggging__`来调整错误存储位置和格式:

```ini
[__logging__]
filename=  # 默认是: ~/aliyunlogcli.log
filemode=  # 默认是: a, 可以是: w, a
format=    # 默认是: %(asctime)s %(levelname)s %(filename)s:%(lineno)d %(funcName)s %(message)s
datefmt=   # 默认是: "%Y-%m-%d %H:%M:%S", 可以是strftime()兼容的日期/时间格式化字符串
level=     # 默认是: warn, 可以是info, error, fatal, critical, debug
```

<h1 id="其他资源">其他资源</h1>

1. 日志服务产品介绍：http://www.aliyun.com/product/sls/
2. 日志服务产品文档：https://help.aliyun.com/product/28958.html
3. 日志服务Python SDK文档: http://aliyun-log-python-sdk.readthedocs.io/
4. 其他问题请提工单
