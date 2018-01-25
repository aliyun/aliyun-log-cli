# 拉取日志

## 介绍
拉取数据(PullLog)指的是针对特定分区, 按照游标来消费日志, 游标指的是服务器接收到日志的时间.
拉取数据的特点是:

1. 没有索引的数据也可以拉取.
2. 按照分区粒度拉取, 每个分区游标互相无关.
3. 速度快, 易并发, 且支持传输压缩.
4. 拉取的数据按照服务器接受的时间排序.


## 获取分区
拉取数据需要传入对应的分区的ID, 通过命令`list_shards`可以获取分区ID的列表. 例如:

```shell
aliyun log list_shards --project_name="p1" --logstore_name="l1" --jmes-filter="map(&shardID, @)"
```

输出:

```shell
[13, 14, 15, 3, 4, 5, 6, 7, 8, 9]
```

**注意**: 这里使用`jmes-filter`对结果做了一下过滤, 只展示其中的`shardID`属性.

也可以使用如下`jmes-filter`只展示数字:

```shell
aliyun log list_shards --project_name="p1" --logstore_name="l1" --jmes-filter="join(',', map(&to_string(shardID), @))"
```

输出:
```shell
13, 14, 15, 3, 4, 5, 6, 7, 8, 9
```


## 拉取数据
根据游标获取数据, 需要传入分区. 下面例子消费分区`3`某个时间范围收集到的数据.

```shell
aliyun log pull_log --project_name="p1" --logstore_name="l1" --shard_id=3 --from_time="2018-01-24 16:00:00 CST" --to_time="2018-01-24 17:00:00  CST"
```

这里拉取从时间`2018-01-24 16:00:00 CST`到`2018-01-24 17:00:00 CST`在分区`3`中的所有数据, 例如:
```shell
{"count": 101, "logs": [{"k1":"a1", "k2":"a2"}, {"k1":"b1", "k2":"b2"}, ... ]}
```

## 转换格式并存储到文件
如果期望将数据按照一行一条的形式存储下来, 一般需要加入`jmes-filter`进行处理. 如果期望存储到文件, 这直接使用`>>`重定向到文件即可. 

例如:

```shell
aliyun log pull_log --project_name="p1" --logstore_name="l1" --shard_id=3 --from_time="2018-01-24 16:00:00 CST" --to_time="2018-01-24 17:00:00 CST" --jmes-filter="join('\n', map(&to_string(@), @))" >> ~/Desktop/test.data
``` 

输出将被存储在文件`test.data`中, 格式为:

```shell
{"k1":"a1", "k2":"a2"}
{"k1":"b1", "k2":"b2"}
...
```

## 时间格式
时间格式推荐是`%Y-%m-%d %H:%M:%S %Z`, 如`2018-01-24 17:00:00 CST`, 但也支持其他合法的时间格式, 例如:`Jan 01 2018 10:10:10 CST`


## 时间范围
命令`pull_log`传入的时间范围, 需要注意几点:

1. 这里的时间指的是服务器接受日志的时间

2. 时间的范围是左闭右开`[)`, 上面例子中`16:00:00`服务器接受到的日志会被拉取到, 但是`17:00:00`服务器所接受到的日志不会.



## 特殊的时间范围
有时我们不关心数据的某一边界, 例如期望获得所有存储的数据到某一天日期位置. 或者获取从某一天开始到目前存储的数据为止的话, 就可以使用特殊游标. 

特殊游标包括`begin`和`end`. 例如:

```shell
aliyun log pull_log --project_name="p1" --logstore_name="l1" --shard_id=3 --from_time="begin" --to_time="2018-01-24 17:00:00 CST"
```

这里拉取所有`2018-01-24 17:00:00 CST`之前服务器接收到的日志.


又例如:

```shell
aliyun log pull_log --project_name="p1" --logstore_name="l1" --shard_id=3 --from_time="2018-01-24 17:00:00 CST" --to_time="end"
```

这里拉取所有`2018-01-24 17:00:00 CST`开始及之后服务器接收到的日志.


## 大数据量
日志服务默认每次拉取数据的限制是传输10MB左右的日志, 大概1000~9000条左右(根据是否压缩, 以及每条日志大小而定). 命令行工具会自动开启压缩, 并自动处理分页的问题, 也就是说当传入的时间范围的数据一次拉取拿不完时, 命令行工具会自动持续拉取. 
这种情况下, 每次拉取到的数据会并列输出如下:

```shell
{"count": 8000, "logs": [{"k1":"a1", "k2":"a2"}, {"k1":"b1", "k2":"b2"}, ... ]}
{"count": 8000, "logs": [{"k1":"a8001", "k2":"a8001"}, {"k1":"b8001", "k2":"b8002"}, ... ]}
....
```

这种情况下, 使用`jmes-filter`的话会针对每一块的输出内容. 也就是上面2块内容分别应用`jmes-filter`来处理. 例如:
```shell
aliyun log pull_log --project_name="p1" --logstore_name="l1" --shard_id=3 --from_time="2018-01-24 16:00:00 CST" --to_time="2018-01-24 17:00:00 CST" --jmes-filter="join('\n', map(&to_string(@), @))"
```

输出:
```shell
{"k1":"a1", "k2":"a2"}
{"k1":"b1", "k2":"b2"}
...
{"k1":"a8001", "k2":"a8002"}
{"k1":"b8001", "k2":"b8002"}
...
```

## 并发下载
命令`pull_log`只能针对一个分区进行下载, 如果需要对所有的shard下载数据, 可以开多个脚本或者使用xargs/shell并行去跑.






