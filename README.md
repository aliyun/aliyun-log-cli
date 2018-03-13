# User Guide

[![Documentation Status](https://readthedocs.org/projects/aliyun-log-cli/badge/?version=latest)](http://aliyun-log-cli.readthedocs.io/?badge=latest)
[![Pypi Version](https://badge.fury.io/py/aliyun-log-cli.svg)](https://badge.fury.io/py/aliyun-log-cli)
[![Travis CI](https://travis-ci.org/aliyun/aliyun-log-cli.svg?branch=master)](https://travis-ci.org/aliyun/aliyun-log-cli)
[![Development Status](https://img.shields.io/pypi/status/aliyun-log-cli.svg)](https://pypi.python.org/pypi/aliyun-log-cli/)
[![Python version](https://img.shields.io/pypi/pyversions/aliyun-log-cli.svg)](https://pypi.python.org/pypi/aliyun-log-cli/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/aliyun/aliyun-log-python-sdk/blob/master/LICENSE)

[中文版README](https://github.com/aliyun/aliyun-log-cli/blob/master/README_CN.md)

## Content

  * [Introduction](#introduction)
     * [Brief](#brief)
     * [Major Features](#major-features)
  * [Installation](#installation)
     * [Operation System](#operation-system)
     * [Supported Version](#supported-version)
     * [Installation Method](#installation-method)
     * [Full Usage list](#full-usage-list)
  * [Configure CLI](#configure-cli)
  * [Input and Output](#input-and-output)
     * [Inputs](#inputs)
     * [Parameter Validation](#parameter-validation)
     * [Output](#output)
     * [Filter output](#filter-output)
     * [Further Process](#further-process)
  * [Command Reference](#command-reference)
     * [Command Specification](#command-specification)
     * [Alias](#alias)
     * [Subcommand and parameters](#subcommand-and-parameters)
     * [Global options](#global-options)
     * [Command categories](#command-categories)
        * [Project management](#1-project-management)
        * [Logstore management](#2-logstore-management)
        * [Shard management](#3-shard-management)
        * [Machine group management](#4-machine-group-management)
        * [Logtail config management](#5-logtail-config-management)
        * [Machine group and Logtail Config Mapping](#6-machine-group-and-logtail-config-mapping)
        * [Index management](#7-index-management)
        * [Cursor management](#8-cursor-management)
        * [Logs write and consume](#9-logs-write-and-consume)
        * [Shipper management](#10-shipper-management)
        * [Consumer group management](#11-consumer-group-management)
  * [Best Practice](#best-practice)
  * [Troubleshooting](#troubleshooting)
  * [Other resources](#other-resources)


## Introduction

The Alicloud log service provides with Web and SDK flavor to operate log service and analyzie logs. To make it more convinient to do automation, we release this command line interface (CLI).

### Brief

Alicloud log service command line console, support almost all operations as web. It also supports incomplete log query check and query cross multiple pages. It could even do project settings copy cross multiple regions.

### Major Features

- Support almost all 50+ REST API of log service. 
- Multiple account support to support cross region operation.
- Log query incomplete check and automatically query cross pagination. 
- Multiple confidential storage types, from file, commandline to env variables.
- Support command line based or file based inputs, complete formation validations.
- Support JMES filter to do further process on results, e.g. select specific fields from json. 
- Cross platforms support (Windows, Linux and Mac), Python based and friendly to Py2 and Py3 even Pypy. Support Pip installation.


## Installation

### Operation System

The CLI supports below operation system:

- Windows
- Mac
- Linux

### Supported Version

Python 2.6, 2.7, 3.3, 3.4, 3.5, 3.6, PyPy, PyPy3

### Installation Method

Run below command to install the CLI: 

```shell
> pip install -U aliyun-log-cli
```

**Note** 

On mac it's recommended to use pip3 to install the CLI. 

```shell
> brew install python3
> pip3 install -U aliyun-log-cli
```

if you encounter errors like `OSError: [Errno 1] Operation not permitted`, try to use option `--user` to install:

```shell
> pip3 install -U aliyun-log-cli --user
``` 

**Alicloud ECS which may have limited internet access**

You could try the mirrors of local network provider, for Alicloud ECS, you can try below noe:

```shell
pip/pip3 install -U aliyun-log-cli --index http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
```


### Full Usage list

Run below command to get the full usage list: 

```shell
> aliyunlog --help
> aliyun --help
```

it will show the [full usage](https://github.com/aliyun/aliyun-log-cli/blob/master/options.txt).


**Note** `aliyunlog` is recommended in case the `aliyun` conflict with others. 

## Configure CLI

Refer to [Configure CLI](http://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_configure_cli_en.html).


## Input and Output


### Inputs

1. Normally case:

```shell
> aliyunlog log get_logs --request="{\"topic\": \"\", \"logstore\": \"logstore1\", \"project\": \"dlq-test-cli-123\", \"toTime\": \"2018-01-01 10:10:10\", \"offset\": \"0\", \"query\": \"*\", \"line\": \"10\", \"fromTime\": \"2018-01-01 08:08:08\", \"reverse\":\"false\"}"
```

2. Input via file:
You could store the content of one parameter into a file and pass it via the command line with prefix `file://`:

```shell
> aliyunlog log get_logs --request="file://./get_logs.json"
```


the content in file `get_logs.json` as below. Note: the `\` is unnecessary to escape the ".
```json
{
  "topic": "",
  "logstore": "logstore1",
  "project": "project1",
  "toTime": "2018-01-01 11:11:11",
  "offset": "0",
  "query": "*",
  "line": "10",
  "fromTime": "2018-01-01 10:10:10",
  "reverse": "true"
}
```

### Parameter Validation

- Mandatory check: if one mandatory parameter is missed, it will report error with usage info.

- Format of parameter's value will be validated. e.g. int, bool, string list, special data structure.

- for boolean, it support:

  - true (case insensitive), T, 1
  - false (case insensitive), F, 0
  
- String list support as ["s1", "s2"]

### Output

1. For operations like Create, Update and Delete, there's no output except the exit code is 0 which means success.

2. For operations like Get and List, it will output in **json** format.

3. For errors, it will report in json format as below:


```json
{
  "errorCode":"...",
  "errorMessage":"..."
}
```

### Filter output

It's supported to filter output via [JMES](http://jmespath.org/):

Examples:

```shell
> aliyunlog log get_logs ...
```
which outputs:

```json
[ {"__source__": "ip1", "key": "log1"}, {"__source__": "ip2", "key": "log2"} ]
```

You could use below `--jmes-filter` to break log into each line:

```shell
> aliyunlog log get_logs ... --jmes-filter="join('\n', map(&to_string(@), @))"
```

output:

```shell
{"__source__": "ip1", "key": "log1"}
{"__source__": "ip2", "key": "log2"}
```

### Further Process
You could use `>>` to store the output to a file. or you may want to process the output using your own cmd. 
For example, there's another way to if you may want to break the logs into each line. you could append thd command with a `|` on linux/unix: 

```shell
| python2 -c "from __future__ import print_function;import json;map(lambda x: print(json.dumps(x).encode('utf8')), json.loads(raw_input()));"
or 
| python3 -c "import json;list(map(lambda x: print(json.dumps(x)), json.loads(input())));"
```

e.g. 
```shell
aliyunlog log get_log .... | | python2 -c "from __future__ import print_function;import json;map(lambda x: print(json.dumps(x).encode('utf8')), json.loads(raw_input()));" >> data.txt
```



## Command Reference

### Command Specification

```shell
1. aliyunlog log <subcommand> [parameters | global options]
2. aliyunlog configure <access_id> <access-key> <endpoint>
3. aliyunlog [--help | --version]
```

### Alias
There's also an alias `aliyunlog` for the CLI in case the command `aliyun` conflicts with others.

```shell
1. aliyunlog log <subcommand> [parameters | global options]
2. aliyunlog configure <access_id> <access-key> <endpoint>
3. aliyunlog [--help | --version]
```

### Subcommand and parameters

Actually, the CLI leverage `aliyun-log-python-sdk`, which maps the command into the methods of `aliyun.log.LogClient`. The parameters of command line is mapped to the parameters of methods.
For the detail spec of parameters, please refer to the [Mapped Python SDK API Spec](http://aliyun-log-cli.readthedocs.io/en/latest/api.html)

**Examples:**

```python
def create_logstore(self, project_name, logstore_name, ttl=2, shard_count=30):
```

Mapped to CLI:

```shell
> aliyunlog log create_logstore
  --project_name=<value>
  --logstore_name=<value>
  [--ttl=<value>]
  [--shard_count=<value>]
```

### Global options

All the commands support below optional global options:

```
    [--access-id=<value>]
    [--access-key=<value>]
    [--region-endpoint=<value>]
    [--client-name=<value>]
    [--jmes-filter=<value>]
```

### Command categories

1. [Project management](#1-project-management)
2. [Logstore management](#2-logstore-management)
3. [Shard management](#3-shard-management)
4. [Machine group management](#4-machine-group-management)
5. [Logtail config management](#5-logtail-config-management)
6. [Machine group and Logtail Config Mapping](#6-machine-group-and-logtail-config-mapping)
7. [Index management](#7-index-management)
8. [Cursor management](#8-cursor-management)
9. [Logs write and consume](#9-logs-write-and-consume)
10. [Shipper management](#10-shipper-management)
11. [Consumer group management](#11-consumer-group-management)


<h3 id="1-project-management">1. Project management</h3>

- list_project
- create_project
- get_project
- delete_project
- **copy_project**

  - copy all configurations including logstore, logtail, and index config from project to another project which could be in different region. 

```shell
> aliyun log copy_project --from_project="p1" --to_project="p1" --to_client="account2"
```

  - Note: `to_client` is another account configured via `aliyun configure`, it's OK to pass `main` or not to copy inside the same region.
  - Refer to [Copy project settings cross regions](http://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_manage_cross_region_copy.html) to learn more. 


<h3 id="2-logstore-management">2. Logstore management</h3>

- create_logstore
- delete_logstore
- get_logstore
- update_logstore
- list_logstore


<h3 id="3-shard-management">3. Shard management</h3>

- list_shards
- split_shard
- merge_shard


<h3 id="4-machine-group-management">4. Machine group management</h3>

- create_machine_group
   - Format of partial parameter:

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


<h3 id="5-logtail-config-management">5. Logtail config management</h3>

- create_logtail_config
   - 参考[Create Logtail Configuration](http://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_create_logtail_config.html)了解如何创建各种格式的Logtail配置.
- update_logtail_config
- delete_logtail_config
- get_logtail_config
- list_logtail_config

<h3 id="6-machine-group-and-logtail-config-mapping">6. Machine group and Logtail Config Mapping</h3>

- apply_config_to_machine_group
- remove_config_to_machine_group
- get_machine_group_applied_configs
- get_config_applied_machine_groups

<h3 id="7-index-management">7. Index management</h3>

- create_index
   - Format of partial parameter:

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

<h3 id="8-cursor-management">8. Cursor management</h3>

- get_cursor
- get_cursor_time
- get_previous_cursor_time
- get_begin_cursor
- get_end_cursor


<h3 id="9-logs-write-and-consume">9. Logs write and consume</h3>

- put_logs
  - Format of parameter:

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
  - Format of parameter: 

```json
{
"topic": "",
"logstore": "logstore1",
"project": "dlq-test-cli-35144",
"toTime": "2018-01-01 11:11:11",
"offset": "0",
"query": "*",
"line": "10",
"fromTime": "2018-01-01 10:10:10",
"reverse": "true"
}
```
  - It will fetch all data when `line` is passed as -1. But if have large volume of data exceeding 1GB, better to use `get_log_all`

- get_log_all
  - this API is similar as `get_logs`, but it will fetch data iteratively and output them by chunk. It's used for large volume of data fetching. 

- get_histograms
- pull_logs
- pull_log
  - this API is similar as `pull_logs`, but it allow readable parameter and allow to fetch data iteratively and output them by chunk. It's used for large volume of data fetching. 
- pull_log_dump
  - this API will dump data from all shards to local files concurrently.

<h3 id="10-shipper-management">10. Shipper management</h3>
- create_shipper

  - Format of partial parameter:

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

<h3 id="11-consumer-group-management">11. Consumer group management</h3>

- create_consumer_group
- update_consumer_group
- delete_consumer_group
- list_consumer_group
- update_check_point
- get_check_point

### Best Practice

- [Configure CLI](http://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_configure_cli_en.html)
- [Create Logtail Config](http://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_create_logtail_config.html)
- [Duplicate project settings cross region](http://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_manage_cross_region_copy.html)
- [Pull Logs](http://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_pull_logs.html)
- [Get Logs](http://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_get_logs.html)


### Troubleshooting

By default, CLI store erros or warnings at `~/aliyunlogcli.log`, it's also configurable via file ~/.aliyunlogcli, section `__loggging__` to adjust the logging level and location: 

```ini
[__logging__]
filename=  # default: ~/aliyunlogcli.log
filemode=  # default: a, could also be: w, a
format=    # default: %(asctime)s %(levelname)s %(filename)s:%(lineno)d %(funcName)s %(message)s
datefmt=   # default: "%Y-%m-%d %H:%M:%S", could be strftime() compitable date/time formatting string
level=     # default: warn, could be: info, error, fatal, critical, debug
```


## Other resources

1. Alicloud Log Service homepage：https://www.alibabacloud.com/product/log-service
2. Alicloud Log Service doc：https://www.alibabacloud.com/help/product/28958.htm
3. Alicloud Log Python SDK doc: http://aliyun-log-python-sdk.readthedocs.io/
4. for any issues, please submit support tickets
