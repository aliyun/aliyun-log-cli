# User Guide

[![Documentation Status](https://readthedocs.org/projects/aliyun-log-cli/badge/?version=latest)](http://aliyun-log-cli.readthedocs.io/?badge=latest)
[![Pypi Version](https://badge.fury.io/py/aliyun-log-cli.svg)](https://badge.fury.io/py/aliyun-log-cli)
[![Travis CI](https://travis-ci.org/aliyun/aliyun-log-cli.svg?branch=master)](https://travis-ci.org/aliyun/aliyun-log-cli)
[![Development Status](https://img.shields.io/pypi/status/aliyun-log-cli.svg)](https://pypi.python.org/pypi/aliyun-log-cli/)
[![Python version](https://img.shields.io/pypi/pyversions/aliyun-log-cli.svg)](https://pypi.python.org/pypi/aliyun-log-cli/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/aliyun/aliyun-log-python-sdk/blob/master/LICENSE)

[中文版README](https://github.com/aliyun/aliyun-log-cli/blob/master/README_CN.md)


### Installation

```shell
> pip install -U aliyun-log-cli
```

**supported platforms**:

- windows
- mac
- linux

#### Supported Python:
- Python 2.6, 2.7, 3.3, 3.4, 3.5, 3.6, PyPy, PyPy3


#### Full Usage list:

```shell
> aliyun --help
```


### CLI

```shell
1. aliyun log <subcommand> [parameters | global options]
2. aliyun configure <access_id> <access-key> <endpoint>
3. aliyun [--help | --version]
```

### Access Key and Endpoint

Refer to [Configuration](https://www.alibabacloud.com/help/doc-detail/29064.htm?spm=a3c0i.o29008en.b99.182.7724d4ddaTGHgf)
to get the access ID/key and endpoints.

There're three ways to configure the access key and endpoint and they're prioritized as below:


**Priority**

1. Parameters

```shell
> aliyun log create_project ..... --access-id=<value> --access-key=<value> --endpoint=<value>
```

  **Note:** Any sub command support such way to overwrite the AK setings in later ways (env or config file) for the specific operations.

2. Environment Variables
  - ALIYUN_LOG_CLI_ACCESSID
  - ALIYUN_LOG_CLI_ACCESSKEY
  - ALIYUN_LOG_CLI_ENDPOINT

3. Local configuration file

  You could store them at `~/.aliyunlogcli`, the default section name is `main`

```ini
[main]
access-id=
access-key=
endpoint=
```

  **You could use the command "configure" to store them directly.**

```shell
> aliyun configure access_id access_key cn-beijing.log.aliyun.com
```


**Multiple Account**

1. You could store multiple accounts for some use cases (e.g. test, multiple region operations)

```shell
> aliyun configure access_id1 access_key1 cn-beijing.log.aliyun.com
> aliyun configure access_id2 access_key2 cn-hangzhou.log.aliyun.com test
```

  AK is stored as:

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

2. Use specific account:

Any subcommand could use global opton `--client-name=<value>` to use specific configured account. e.g:
```shell
> aliyun log create_project ..... --client-name=test
```
It will use `test` to create the project.

In some case, we need to operate cross regions, e.g.

```shell
> aliyun log copy_project --from_project="p1" --to_project="p1" --to_client=test
```

It will use account `main` to copy project `p1` in its region to another region under account `test`


### Inputs
1. Normally case:

```shell
> aliyun log get_logs --request="{\"topic\": \"\", \"logstore\": \"logstore1\", \"project\": \"dlq-test-cli-123\", \"toTime\": \"123\", \"offset\": \"0\", \"query\": \"*\", \"line\": \"10\", \"fromTime\": \"123\", \"reverse\":\"false\"}"
```

2. Input via file:
You could store the content of one parameter into a file and pass it via the command line with prefix `file://`:

```shell
> aliyun log get_logs --request="file://./get_logs.json"
```


the content in file `get_logs.json` as below. Note: the `\` is unnecessary to escape the ".
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

**Parameter Validation**

- Mandatory check: if one mandatory parameter is missed, it will report error with usage info.
- Format of parameter's value will be validated. e.g. 例如int, bool, string list, special data structure.
- for boolean, it support:
  - true (case insensitive), T, 1
  - false (case insensitive), F, 0
- String list support as:
  - ["s1", "s2"]

### Output
1. For operations like Create, Update and Delete, there's no output except the exit code is 0 which means success.
2. For operations like Get and List, it will output in json format.
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
> aliyun log get_logs ...
```
which outputs:

```json
{
  "count": 3,
   "logstores": ["logstore3", "logstore1", "logstore2"],
   "total": 3
}
```

You could use below `--jmse-filter` to filter it:

```shell
> aliyun log get_logs ... --jmse-filter="logstores[2:]"
```

Then you will be the name list of second logstore and later ones as below:

```shell
["logstore1", "logstore2"]
```

### Supported commands:

**Normal Case**

Actually, the CLI leverage `aliyun-log-python-sdk`, which maps the command into the methods of `aliyun.log.LogClient`. The parameters of command line is mapped to the parameters of methods.
For the detail spec of parameters, please refer to the [Python SDK API Spec](http://aliyun-log-python-sdk.readthedocs.io/api.html#aliyun.log.LogClient)

**Examples:**

```python
def create_logstore(self, project_name, logstore_name, ttl=2, shard_count=30):
```

Mapped to CLI:

```shell
> aliyun log create_logstore
  --project_name=<value>
  --logstore_name=<value>
  [--ttl=<value>]
  [--shard_count=<value>]
```

##### Global options:
All the commands support below optional global options:
```
    [--access-id=<value>]
    [--access-key=<value>]
    [--region-endpoint=<value>]
    [--client-name=<value>]
    [--jmes-filter=<value>]
```

#### Full command list:

**project**

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

**logstore**

- create_logstore
- delete_logstore
- get_logstore
- update_logstore
- list_logstore
- list_topics


**shard**

- list_shards
- split_shard
- merge_shard


**machine group**

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

**logtail config**

- create_logtail_config
   - Format of partial parameter:

```json
{
 "config_name": "config_name2",
 "logstore_name": "logstore2",
 "file_pattern": "file_pattern",
 "time_format": "time_format",
 "log_path": "/log_path",
 "endpoint": "endpoint",
 "log_parse_regex": "xxx ([\\w\\-]+\\s[\\d\\:]+)\\s+(.*)",
 "log_begin_regex": "xxx.*",
 "reg_keys": [
   "time",
   "value"
 ],
 "topic_format": "none",
 "filter_keys": [
   "time",
   "value"
 ],
 "filter_keys_reg": [
   "time",
   "value"
 ],
 "logSample": "xxx 2017-11-11 11:11:11 hello alicloud."
}
```

- update_logtail_config
- delete_logtail_config
- get_logtail_config
- list_logtail_config


**Machine group and Logtail Config Mapping**

- apply_config_to_machine_group
- remove_config_to_machine_group
- get_machine_group_applied_configs
- get_config_applied_machine_groups


**index**

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

**cursor**

- get_cursor
- get_cursor_time
- get_previous_cursor_time
- get_begin_cursor
- get_end_cursor

**logs**

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

**shipper**

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

**consumer group**

- create_consumer_group
- update_consumer_group
- delete_consumer_group
- list_consumer_group
- update_check_point
- get_check_point


## Other resources

1. Alicloud Log Service homepage：https://www.alibabacloud.com/product/log-service
2. Alicloud Log Service doc：https://www.alibabacloud.com/help/product/28958.htm
3. Alicloud Log Python SDK doc: http://aliyun-log-python-sdk.readthedocs.io/
4. for any issues, please submit support tickets
