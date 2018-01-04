# User Guide (中文)

[![Documentation Status](https://readthedocs.org/projects/aliyun-log-cli/badge/?version=latest)](http://aliyun-log-cli.readthedocs.io/?badge=latest)
[![Pypi Version](https://badge.fury.io/py/aliyun-log-cli.svg)](https://badge.fury.io/py/aliyun-log-cli)
[![Travis CI](https://travis-ci.org/aliyun/aliyun-log-cli.svg?branch=master)](https://travis-ci.org/aliyun/aliyun-log-cli)
[![Development Status](https://img.shields.io/pypi/status/aliyun-log-cli.svg)](https://pypi.python.org/pypi/aliyun-log-cli/)
[![Python version](https://img.shields.io/pypi/pyversions/aliyun-log-cli.svg)](https://pypi.python.org/pypi/aliyun-log-cli/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/aliyun/aliyun-log-python-sdk/blob/master/LICENSE)

[README in English](https://github.com/aliyun/aliyun-log-cli/blob/master/README.md)


## 背景
一直以来日志服务(SLS)提供了Web和SDK的方式进行日志采集, 管理, 查询和分析. 为了方便用户越来越多的的自动化日志配置查询分析的需求, 我们重磅发布了SLS的命令行控制台(Command Line Interface - CLI).

### 基本介绍
SLS命令行控制台, 支持几乎所有操作, 日志查询支持完整性检查与自动分页, 支持多账户与跨域复制.

### 主要功能

- 支持几乎所有50多个日志服务的REST接口.
- 支持多账号, 方便测试与跨域操作.
- 日志查询完整性查询与自动分页.
- 支持多种方式存储和配置秘钥, 适用于各种情况.
- 支持通过命令行或者文件的形式输入复杂参数, 并校验参数内容格式.
- 支持JMES过滤器对结果进行进一步处理, 方便选择特定信息.
- 跨平台(Windows/Linux和Mac)支持, 基于Python(Py2.6+和Py3.3+平台友好)，支持Pip安装。


### 安装

```shell
> pip install -U aliyun-log-cli
```

**支持平台**:

- windows
- mac
- linux



#### 支持平台
- Python 2.6, 2.7, 3.3, 3.4, 3.5, 3.6, PyPy, PyPy3


#### 完整参数列表

```shell
> aliyun --help
```


### CLI规范

```shell
1. aliyun log <subcommand> [parameters | global options]
2. aliyun configure <access_id> <access-key> <endpoint> [<client-name>]
3. aliyun [--help | --version]
```

### CLI错误诊断

CLI默认把执行过程中的警告和错误存储在`~/aliyunlogcli.log`中, 也可以配置~/.aliyunlogcli中`__loggging__`来调整错误存储位置和格式:

```ini
[__logging__]
filename=  # 默认是: ~/aliyunlogcli.log
filemode=  # 默认是: a, 可以是: w, a
format=    # 默认是: %(asctime)s %(levelname)s %(filename)s:%(lineno)d %(funcName)s %(message)s
datefmt=   # 默认是: "%Y-%m-%d %H:%M:%S", 可以是strftime()兼容的日期/时间格式化字符串
level=     # 默认是: warn, 可以是info, error, fatal, critical, debug
```


### 访问秘钥与入口存储与使用

参考[SDK配置](https://help.aliyun.com/document_detail/29064.html?spm=5176.doc29068.2.8.SWJhYZ)
获得访问秘钥的ID和Key以及访问入口Endpoint, 构建一个LogClient的客户端.

有三种方式配置访问秘钥与入口, 优先级如下:

**优先级**

1. 参数

```shell
> aliyun log create_project ..... --access-id=<value> --access-key=<value> --endpoint=<value>
```

  **注意:**
  - 任意 log子命令都支持以上方式定义特定的AK与Endpoint(覆盖后面的方式)


2. 环境变量
  - ALIYUN_LOG_CLI_ACCESSID
  - ALIYUN_LOG_CLI_ACCESSKEY
  - ALIYUN_LOG_CLI_ENDPOINT

3. 本地配置文件

  将存储AK与Endpoint在~/.aliyunlogcli, 默认使用的块名是`main`

```ini
[main]
access-id=
access-key=
endpoint=
```

  **Configure命令可以修改配置文件内容**

```shell
> aliyun configure access_id access_key cn-beijing.log.aliyun.com
```


**多账户**

1. 存储与多个账户, 以便在特定情况下使用(例如测试):

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

某些情况下也需要跨账户操作, 例如:

```shell
> aliyun log copy_project --from_project="p1" --to_project="p1" --to_client=test
```

将`main`账户下对应的项目`p1`复制到账户`test`下的`p1`




### 参数输入
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

**参数校验**

- 必填的参数没有填写时会报错, 输出参数列表
- 参数格式本身会进行校验, 例如int, bool, string list, 特定数据结构等
- bool支持的形式有:
  - true (大小写不敏感), T, 1
  - false (大小写不敏感), F, 0

- 字符串列表支持的形式是:

  - ["s1", "s2"]

### 输出
1. 对于Create, Update, Delete操作, 一般脚本无输出, exit code=0表示成功.
2. 对于Get/List操作, 以json格式输出内容
3. 错误情况下, 以如下格式返回错误:

```json
{
  "errorCode":"...",
  "errorMessage":"..."
}
```

### 输出过滤
支持通过[JMES](http://jmespath.org/)过滤输出的结果.

例如:

```shell
> aliyun log get_logs ...
```

的输出是:

```json
{
  "count": 3,
   "logstores": ["logstore3", "logstore1", "logstore2"],
   "total": 3
}
```

通过命令:

```shell
> aliyun log get_logs ... --jmes-filter="logstores[2:]"
```

可以获取第二以及后面的logstore的名字, 输出:

```shell
["logstore1", "logstore2"]
```

### 支持的命令:

**一般情况**

实际上CLI实现依赖于阿里云日志服务的Python SDK, 子命令对应于`aliyun.log.LogClient`的方法, 参数和可选参数也一一对应.
具体支持的API参数, 请参考[映射的Python SDK API](http://aliyun-log-cli.readthedocs.io/en/latest/api.html)

**例子:**

```python
def create_logstore(self, project_name, logstore_name, ttl=2, shard_count=30):
```

对应CLI:

```shell
> aliyun log create_logstore
  --project_name=<value>
  --logstore_name=<value>
  [--ttl=<value>]
  [--shard_count=<value>]
```

##### 全局选项

所有命令都支持如下的全局选项:

```
    [--access-id=<value>]
    [--access-key=<value>]
    [--region-endpoint=<value>]
    [--client-name=<value>]
    [--jmes-filter=<value>]
```


#### 完整命令列表:

**项目组**

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

**日志库**

- create_logstore
- delete_logstore
- get_logstore
- update_logstore
- list_logstore


**分区**

- list_shards
- split_shard
- merge_shard



**机器组**

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

**Logtail配置**

- create_logtail_config
   - 参考[创建Logtail配置](./tutorials/tutorial_create_logtail_config.html)了解如何创建各种格式的Logtail配置.
- update_logtail_config
- delete_logtail_config
- get_logtail_config
- list_logtail_config


**机器组与Logtail配置关联**

- apply_config_to_machine_group
- remove_config_to_machine_group
- get_machine_group_applied_configs
- get_config_applied_machine_groups


**索引**

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

**游标**

- get_cursor
- get_cursor_time
- get_previous_cursor_time
- get_begin_cursor
- get_end_cursor

**日志**

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

**投递**

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

**消费组**

- create_consumer_group
- update_consumer_group
- delete_consumer_group
- list_consumer_group
- update_check_point
- get_check_point


## 其他资源：

1. 日志服务产品介绍：http://www.aliyun.com/product/sls/
2. 日志服务产品文档：https://help.aliyun.com/product/28958.html
3. 日志服务Python SDK文档: http://aliyun-log-python-sdk.readthedocs.io/
4. 其他问题请提工单
