# 用户手册

[![Documentation Status](https://readthedocs.org/projects/aliyun-log-cli/badge/?version=latest)](http://aliyun-log-cli.readthedocs.io/?badge=latest)
[![Pypi Version](https://badge.fury.io/py/aliyun-log-cli.svg)](https://badge.fury.io/py/aliyun-log-cli)
[![Travis CI](https://travis-ci.org/aliyun/aliyun-log-cli.svg?branch=master)](https://travis-ci.org/aliyun/aliyun-log-cli)
[![Development Status](https://img.shields.io/pypi/status/aliyun-log-cli.svg)](https://pypi.python.org/pypi/aliyun-log-cli/)
[![Python version](https://img.shields.io/pypi/pyversions/aliyun-log-cli.svg)](https://pypi.python.org/pypi/aliyun-log-cli/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/aliyun/aliyun-log-python-sdk/blob/master/LICENSE)

[README in English](https://github.com/aliyun/aliyun-log-cli/blob/master/README.md)

## 内容

* [简介](#简介)
    * [基本介绍](#基本介绍)
    * [主要功能](#主要功能)
* [安装](#安装)
    * [操作系统](#操作系统)
    * [支持版本](#支持版本)
    * [安装方式](#安装方式)
    * [离线安装](#离线安装)
    * [安装常见问题](#安装常见问题)
    * [完整参数列表](#完整参数列表)
* [配置说明](#配置说明)
* [输入输出](#输入输出)
    * [输入](#输入)
    * [参数校验](#参数校验)
    * [输出](#输出)
    * [输出过滤](#输出过滤)
    * [进一步处理](#进一步处理)
* [命令参考](#命令参考)
    * [命令规范](#命令规范)
    * [命令别名](#命令别名)
    * [子命令与参数](#子命令与参数)
    * [全局选项](#全局选项)
    * [命令类别](#命令类别)
        * 资源管理相关
            * [项目组管理](#1-项目组管理)
            * [日志库管理](#2-日志库管理)
            * [分区管理](#3-分区管理)
            * [机器组管理](#4-机器组管理)
            * [Logtail配置管理](#5-客户端配置管理)
            * [机器组与Logtail配置关联](#6-机器组与客户端配置关联)
            * [索引管理](#7-索引管理)
            * [投递管理](#10-投递管理)
            * [其他配置管理](#13-其他配置管理)
        * 数据读写消费
            * [日志读写与消费](#9-日志读写与消费)
            * [游标操作](#8-游标操作)
            * [消费组管理](#11-消费组管理)
        * [Elasticsearch数据迁移](#12-Elasticsearch数据迁移)
        * [ETL数据转换](#14-ETL)
        * [高级实用命令]
            * [跨域复制项目配置](http://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_manage_cross_region_copy.html)
            * [拉取日志](http://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_pull_logs.html)
            * [查询日志](http://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_get_logs.html)
            * [支持的灵活时间格式](https://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_human_readable_datetime.html)
            * [高速跨域日志复制、历史数据重新索引与数仓投递](https://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_copy_data.html)
* [最佳实践](#最佳实践)
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

支持以下Python版本：
Python 2.6、2.7、3.3、3.4、3.5、3.6、3.7，PyPy和PyPy3。

**安装Python与pip**
系统需要安装`Python`以及`pip`，这里可以[下载Python](https://www.python.org/downloads/)。默认`pip`会附带，如果没有配套的`pip`（通过命令行`pip`或者`<python路径> -m pip`来判断是否部署了），可以这里获取：https://github.com/pypa/get-pip/blob/master/get-pip.py
下载后运行：`<python程序路径> get-pip.py`后即可安装`pip`。

**注意** Windows下安装Python时，需要将Python的路径加入到PATH中（默认安装程序可以支持这点）。

<h2 id="安装方式">安装方式</h2>

执行以下命令安装日志服务CLI。

```shell
# pypy3
> pypy3 -m pip install aliyun-log-python-sdk aliyun-log-cli -U --no-cache

# pip3
> pip3 install aliyun-log-python-sdk aliyun-log-cli -U --no-cache
```

**pypy/pypy3与配置的pip安装**

如果使用`copy_data`、`pull_log_dump`等需要大量下载、传输数据的命令，**为了获得更好的性能**，推荐使用`pypy`或`pypy3`来安装。
这里[下载](https://www.pypy.org/download.html)和安装。如果是Mac可以使用`brew install pypy3`来安装。
默认pip会附带，如果没有配套的pip，可以这里获取：https://github.com/pypa/get-pip/blob/master/get-pip.py
下载后运行：`pypy3 get-pip.py`后即可安装`pip`，但后续在pypy3上安装时，需要将`pip/pip3`修改为：`pypy3 -m pip instal ....`
也可以查看现有pip的路径: `which pip`，修改第一行命令行指向pypy3的绝对路径即可。

**Mac相关**

Mac上推荐使用pip3安装CLI，首选需要安装Python3或pypy3：
 
```shell
# Pypy3
> brew install pypy3
> pypy3 -m pip install aliyun-log-python-sdk aliyun-log-cli -U --no-cache

# Python3
> brew install python3
> pip/pip3 install -U aliyun-log-cli --no-cache

```

Mac上如果你安装时遇到了权限相关的错误，如：`OSError: [Errno 1] Operation not permitted`，尝试使用如下命令安装：

```shell
> pip/pip3 install -U aliyun-log-cli --user
``` 


**外网访问受限的阿里云ECS**

因为安全策略等原因，某些云服务器可能无法访问Pypi服务器，可以尝试使用本地Pypi镜像，例如阿里云服务器可以尝试:

```shell
pip/pip3 install -U aliyun-log-cli --index http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
```

Note：也可以使用清华的索引`-i https://pypi.tuna.tsinghua.edu.cn/simple`

<h2 id="离线安装">离线安装</h2>

从 [0.1.12](https://github.com/aliyun/aliyun-log-cli/releases)开始, 我们为Linux x64和MacOS x64提供离线的安装包. 

如下步骤安装:

1. 从[release页面](https://github.com/aliyun/aliyun-log-cli/releases)下载对应离线安装包.
2. 解压到本地目录, 例如`cli_packages`, 可以看到许多whl文件在里面.
3. 如果还没有`pip`, 可以如下安装:

```shell
python pip-10.0.1-py2.py3-none-any.whl/pip install --no-index cli_packages/pip-10.0.1-py2.py3-none-any.whl
```

4. 安装CLI:

```shell
pip/pip3 install aliyun-log-cli --no-index --find-links=cli_packages
```

5. 验证:
```shell
> aliyunlog --version
```

<h2 id="安装常见问题">常见安装问题</h2>

1. 安装时报TLSV1_ALERT_PROTOCOL_VERSION错误

```shell
> pip/pip3 install aliyun-log-cli

Collecting aliyun-log-cli
  Could not fetch URL https://pypi.python.org/simple/aliyun-log-cli/: There was a problem confirming the ssl certificate: [SSL: TLSV1_ALERT_PROTOCOL_VERSION] tlsv1 alert protocol version (_ssl.c:590) - skipping
  Could not find a version that satisfies the requirement aliyun-log-cli (from versions: )
No matching distribution found for aliyun-log-cli
```

**解答**： 请先升级pip：

```shell
pip/pypy3 install pip -U
```


2. 找不到命令`aliyunlog`?

因为某种原因创建脚本`aliyunlog`链接时未成功, 可以手工创建一个, 如下:


2.1. 找到Python路径:

在linux或mac, 执行命令可以看到:

```shell
which python
```

Windows上，很可能位于`c:\PythonXX` (XX指版本27或37等）


2.2. Mac/Linux下，创建一个叫做`aliyunlog`文件, 赋予执行权限；Windows下，创建一个`aliyunlog.py`文件；

文件内容如下, 并放到PATH目录下 ：


```python
#!<python路径放这里,注意有一个感叹号!>
import re
import sys

from aliyunlogcli.cli import main

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
```


对于linux或mac, 可以考虑放到`/usr/bin/`目录下
Windows下可以考虑放到`c:/windows`目录下等

2.3. 验证, 执行如试下命令看一下是否成功.
```shell
# linux/mac
> aliyunlog --version
# windows
> aliyunlog.py --version
```

3. Regex模块安装失败?
如果存在安装Regex失败的错误, 可以参考使用`yun`/`apt-get`或者手动安装一下python-devel
https://rpmfind.net/linux/rpm2html/search.php?query=python-devel



<h2 id="完整参数列表">完整参数列表</h2>

执行以下命令查看日志服务CLI参数列表。
```shell
> aliyunlog --help
```

注意: 命令`aliyun`已经废弃(为了避免与通用阿里云CLI冲突).

会显示[完整命令](https://github.com/aliyun/aliyun-log-cli/blob/master/options.txt)。

**Note** `aliyunlog`和`aliyun`都可以，推荐使用`aliyunlog`以防冲突。 


<h1 id="配置说明">配置说明</h1>

参考[配置CLI](http://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_configure_cli_cn.html)

<h1 id="输入输出">输入输出</h1>

<h2 id="输入">输入</h2>

1. 一般输入

```shell
> aliyunlog log get_logs --request="{\"topic\": \"\", \"logstore\": \"logstore1\", \"project\": \"dlq-test-cli-123\", \"toTime\": \"2018-01-01 11:11:11\", \"offset\": \"0\", \"query\": \"*\", \"line\": \"10\", \"fromTime\": \"2018-01-01 10:10:10\", \"reverse\":\"false\"}"
```

2. 文件输入

也可以将上面参数放到一个文件里面, 简化命令行, 需要义`file://`开头+文件路径即可:

```shell
> aliyunlog log get_logs --request="file://./get_logs.json"
```


文件`get_logs.json`内容如下, 注意: 文件中不需要反斜杠`\`来转义.

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
> aliyunlog log get_logs ...
```

以上命令的输出是:

```json
[ {"__source__": "ip1", "key": "log1"}, {"__source__": "ip2", "key": "log2"} ]
```

通过以下命令将日志分隔为每一行: 

```shell
> aliyunlog log get_logs ... --jmes-filter="join('\n', map(&to_string(@), @))"
```

输出:

```shell
{"__source__": "ip1", "key": "log1"}
{"__source__": "ip2", "key": "log2"}
```


<h2 id="进一步处理">进一步处理</h2>
你可以使用`>>`来讲输出存储到一个文件. 某些时候, 你需要使用其他命令进行处理, 例如, 这里介绍另一个把json格式的日志分行打印的方法. 在Linux/Unix下, 你可以在命令后通过添加一个`|`来进一步处理.  

```shell
| python2 -c "from __future__ import print_function;import json;map(lambda x: print(json.dumps(x).encode('utf8')), json.loads(raw_input()));"
or 
| python3 -c "import json;list(map(lambda x: print(json.dumps(x)), json.loads(input())));"
```

例如: 

```shell
aliyunlog log get_log .... |  python2 -c "from __future__ import print_function;import json;map(lambda x: print(json.dumps(x).encode('utf8')), json.loads(raw_input()));" >> data.txt
```


<h1 id="命令参考">命令参考</h1>

<h2 id="命令规范">命令规范</h2>

```shell
1. aliyunlog log <subcommand> [parameters | global options]
2. aliyunlog configure <access_id> <access-key> <endpoint> [<client-name>]
3. aliyunlog [--help | --version]
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
> aliyunlog log create_logstore
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
 12. [Elasticsearch 数据迁移](#12-Elasticsearch数据迁移)

<h3 id="1-项目组管理">1. 项目组管理</h3>

- list_project
- create_project
- get_project
- delete_project
- **copy_project**
  - 复制所有源project的logstore, logtail, machine group和index配置等到目标project中.

```shell
> aliyunlog log copy_project --from_project="p1" --to_project="p1" --to_client="account2"
```

  - 注意: `to_client`是通过aliyunlog configure配置的其他账户, 也可以不传或传`main`同域复制.
  - 参考[跨域复制项目组配置](http://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_manage_cross_region_copy.html)了解如何跨域复制项目组配置.

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
 "group_type": "",
 "group_attribute": {
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
   - 参考[创建Logtail配置](http://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_create_logtail_config.html)了解如何创建各种格式的Logtail配置.
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
"toTime": "2018-01-01 11:11:11",
"offset": "0",
"query": "*",
"line": "10",
"fromTime": "2018-01-01 10:10:10",
"reverse": "true"
}
```
  - 但参数`line`传入-1时, 就回获取所有. 但是当数据量很大, 超过1GB时, 最好使用`get_log_all`

- get_log_all
  - 和`get_logs`一样, 但是迭代式获取数据并输出, 适合大容量的数据获取. 

- get_histograms
- pull_logs
- pull_log
  - 和`pull_logs`类似, 但是迭代式获取数据并输出, 适合大容量的数据获取. 
- pull_log_dump
  - 并发下载大量日志直接到本地文件，并一行一个日志。

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

<h3 id="12-Elasticsearch数据迁移">12. Elasticsearch 数据迁移</h3>

- es_migrate
  - 参考[Elasticsearch 数据迁移](https://github.com/aliyun/aliyun-log-cli/tree/master/doc/tutorials/tutorial_es_migration_cn.md)了解如何将 Elasticsearch 中的数据导入日志服务。

<h3 id="13-其他配置管理">13. 其他配置管理</h3>

- 报警管理

- 快速查询管理

- 报表管理

复制仪表盘举例: 

```text
1. 下载到本地
aliyunlog log get_dashboard --project=项目名 --entity=仪表盘名 >> dashboard.json
https://aliyun-log-cli.readthedocs.io/en/latest/api.html#aliyun.log.LogClient.get_dashboard

2. 修改本地的dahboard.json, 主要调整里面的dashboard name, title以及logstore
如果是跨project复制, 目前不存在同name的仪表盘, 且关联logstore名字一样, 可以跳过

3. 创建到目标项目中
aliyunlog log create_dashboard --project=新项目名 --detail=file://./dashboard.json
```

- 外部存储管理


参考命令行帮助


<h3 id="14-ETL">14. ETL数据转换</h3>
- [背景与介绍](http://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_etl_intro_scenario.html)
- [部署与管理](http://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_etl_deployment_management.html)
- [编排与转换](http://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_etl_orchestration_transform.html)
- [扩展UDF](http://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_etl_extension_udf.html)

<h1 id="最佳实践">最佳实践</h1>

- [配置CLI](http://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_configure_cli_cn.html)
- [创建Logtail配置](http://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_create_logtail_config.html)
- [跨域复制项目配置](http://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_manage_cross_region_copy.html)
- [拉取日志](http://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_pull_logs.html)
- [查询日志](http://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_get_logs.html)
- [Elasticsearch 数据迁移](https://github.com/aliyun/aliyun-log-cli/tree/master/doc/tutorials/tutorial_es_migration_cn.md)
- [支持的灵活时间格式](https://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_human_readable_datetime.html)
- [高速跨域日志复制、历史数据重新索引与数仓投递](https://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_copy_data.html)


<h1 id="错误诊断">错误诊断</h1>

CLI默认把执行过程中的警告和错误存储在`~/aliyunlogcli.log`中, 也可以配置~/.aliyunlogcli中`__loggging__`来调整错误存储位置和格式:

```ini
[__logging__]
filename=  # 默认是: ~/aliyunlogcli.log, 进行轮转
filebytes=   # 默认是104857600 (100MB), 单个文件大小, 单位Byte
backupcount= # 默认是5个, 轮转文件的个数
#filemode=  # 废弃
format=    # 默认是: %(asctime)s %(threadName)s:%(levelname)s %(filename)s:%(lineno)d %(funcName)s %(message)s
datefmt=   # 默认是: "%Y-%m-%d %H:%M:%S", 可以是strftime()兼容的日期/时间格式化字符串
level=     # 默认是: warn, 可以是info, error, fatal, critical, debug
```

<h1 id="其他资源">其他资源</h1>

1. 日志服务产品介绍：http://www.aliyun.com/product/sls/
2. 日志服务产品文档：https://help.aliyun.com/product/28958.html
3. 日志服务Python SDK文档: http://aliyun-log-python-sdk.readthedocs.io/
4. 其他问题请提工单
