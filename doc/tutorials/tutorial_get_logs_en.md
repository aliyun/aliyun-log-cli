# Get logs

## Introduction

Get Log (GetLog) means searching out logs on certain conditions among specific time range basing on indexed data.

It has below characters:

1. Just for index data.
2. Against index and cross partition. Support get logs cross multiple logstores.
3. Support search against topic, fulltext or fields etc.
4. The time range is checking the logs' time rather than the log rececieved time by server.

Refer to [Query logs](https://www.alibabacloud.com/help/doc-detail/43772.htm) to learn how to turn on index and more syntax of searching.

## Get log
Using CLI, it's very easy to query logs basing on prepared search statements. Below is an example, it all slow access logs on a specific server among a specific time range.

```shell
aliyunlog log get_log_all --project="p1" --logstore="l1" --query="host:test.com and response_time>5000" --from_time="2018-01-24 16:00:00+8:00" --to_time="2018-01-24 17:00:00 +8:00"
```

It get all logs that his the conditions (`host:test.com and response_time>5000`) from time range (from `2018-01-24 16:00:00+8:00` to `2018-01-24 17:00:00+8:00`) like:

```shell
[{"k1":"a1", "k2":"a2"}, {"k1":"b1", "k2":"b2"}, ... ]
```

**Note:** 
- We could also use another sub-command `get_log(s)` passing parameter `size=-1` to get all logs hitting the condition. But it's recommended to use the sub-command `get_log_all` when the data volume is large (e.g. total logs count exceeds 1 million).


## Transform the format and store to file
The example above shows the format of get log is a big JSON formatted data, if we want to store the logs per row per log,  we need to pass parameter `jmes-filter` to process and use redirection `>>` to output to disk. 

Examples:

```shell
aliyunlog log get_log_all --project="p1" --logstore="l1" --query="host:test.com and response_time>5000" --from_time="2018-01-24 16:00:00+8:00" --to_time="2018-01-24 17:00:00 +8:00" --jmes-filter="join('\n', map(&to_string(@), @))" >> ~/Desktop/test.data
``` 

It will store the results to file `test.data` in below format:

```shell
{"k1":"a1", "k2":"a2"}
{"k1":"b1", "k2":"b2"}
...
```

## Time format
The time format passed to the CLI is recommend as `%Y-%m-%d %H:%M:%S %Z`, like `2018-01-24 17:00:00+8:00`. But the CLI also support popular format like `Jan 01 2018 10:10:10+8:00`

**Note：** `+8:00` is the timezone info.

Actually, it's also supported to use relative format like `2 day ago`, `now`, `yesterday 0:0`, `-1week` etc.

## Time range
When passing time range parameters to `get_log(s)` or `get_log_all`, please note:

1. The time here points to log time parsed from raw logs when logs are uploaded (If not being specified, time received by server is used).  

2. The time range is closed for both left and right as `[]`, it means it will get logs at `16:00:00` and `17:00:00` in above example.


## Query cross logstores

To get logs cross logstores, use sub-command `get_project_logs`, example:


```shell
aliyunlog log get_project_logs --request="{\"project\":\"p1\", \"query\":\"select count(1) from logstore1, logstore2, logstore3 where __date__ >'2017-11-10 00:00:00' and __date__ < '2017-11-13 00:00:00'\"}"
```

For more detail, please refer to document [Query cross logstore](https://www.alibabacloud.com/help/product/62650.htm).
