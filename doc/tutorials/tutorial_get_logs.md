# 查询日志

## 介绍
查询数据(GetLog)指的是针对索引数据, 在特定时间范围内搜索特定的日志.

查询日志的特点是:

1. 针对获取索引的数据
2. 按照索引获取, 跨分区, 支持跨多个logstore查询
3. 可以按照主题, 全文分词, 特定索引域等查询条件获取.
4. 按照日志自身时间查询, 而不是服务器接收.

参考[查询语法](https://help.aliyun.com/document_detail/29060.html?spm=5176.doc53608.6.661.ckIxaY)以了解如何打开索引以及查询的相关语法.

## 查询日志
根据设定好的查询语句查询数据, 即可通过CLI轻松查询数据. 下面例子查询某个时间范围, 某台服务器响应速度大于5秒的访问日志.

```shell
aliyun log get_log_all --project="p1" --logstore="l1" --query="host:test.com and response_time>5000" --from_time="2018-01-24 16:00:00 CST" --to_time="2018-01-24 17:00:00  CST"
```

这里拉取从时间`2018-01-24 16:00:00 CST`到`2018-01-24 17:00:00 CST`在内满足条件`host:test.com and response_time>5000`的日志, 例如:
```shell
[{"k1":"a1", "k2":"a2"}, {"k1":"b1", "k2":"b2"}, ... ]
```

**注意:** 

- 这里也可以使用子命令`get_log(s)`并传入`size=-1`, 但如果数据量特别多时, 例如总行数100万行的时候, 推荐使用`get_log_all`.


## 转换格式并存储到文件
如果期望将数据按照一行一条的形式存储下来, 一般需要加入`jmes-filter`进行处理. 如果期望存储到文件, 这直接使用`>>`重定向到文件即可. 

例如:

```shell
aliyun log get_log_all --project="p1" --logstore="l1" --query="host:test.com and response_time>5000" --from_time="2018-01-24 16:00:00 CST" --to_time="2018-01-24 17:00:00  CST" --jmes-filter="join('\n', map(&to_string(@), @))" >> ~/Desktop/test.data
``` 

输出将被存储在文件`test.data`中, 格式为:

```shell
{"k1":"a1", "k2":"a2"}
{"k1":"b1", "k2":"b2"}
...
```

## 时间格式
时间格式推荐是`%Y-%m-%d %H:%M:%S %Z`, 如`2018-01-24 17:00:00 CST`, 但也支持其他合法的时间格式, 例如:`Jan 01 2018 10:10:10 CST`

**注意：** 时区不仅可以是CST，如果发现拿不到数据，可以改成特定时区例如 UTC-8 或者 UTC+8 

CLI还支持更多其他格式的时间格式，例如`2 day ago`等，参考[这里](https://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_human_readable_datetime.html).

## 时间范围
命令`get_log(s)`或`get_log_all`传入的时间范围, 需要注意几点:

1. 这里的时间指的是解析出的日志时间(日志配置没有指定的情况下, 服务器接收日志的时间会设为这个时间).

2. 时间的范围是左闭右闭`[]`, 上面例子中`16:00:00`和`17:00:00`时间的日志都会获得.

## 跨库查询

使用接口`get_project_logs`可以跨库查询日志. 例如:

```shell
aliyun log get_project_logs --request="{\"project\":\"p1\", \"query\":\"select count(1) from logstore1, logstore2, logstore3 where __date__ >'2017-11-10 00:00:00' and __date__ < '2017-11-13 00:00:00'\"}"
```

具体细节可以参考[跨库查询](https://help.aliyun.com/document_detail/62650.html?spm=5176.11065259.1996646101.searchclickresult.1fd2173brsQAo5).
