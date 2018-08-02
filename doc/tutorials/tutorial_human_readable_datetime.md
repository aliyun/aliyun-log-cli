# 使用CLI的灵活时间格式来执行查询、报警和下载等

## 介绍
在查询、统计、拉取时需要传入时间范围，但是经常我们需要传入更灵活的参数，如："今天凌晨"，"昨天"，"3天前"，"现在"等参数时，大脑需要费力的换算成对应的时间格式，如"2018-8-1 10:10:00"等。
另一方面，用脚本定期跑的时候，需要相对这样的相对值，例如，每5分钟查询，过去60分钟的范围的数据是否有异常等。每次执行希望有一个时间范围是：过去60分钟到现在。

现在这样的方式CLI支持了!

## 支持的方法
以下方法的参数，如`from_time`、`to_time`等目前也接受相对时间了。

| 方法 | 作用 |
| ---- | ---- |
| get_log | 查询统计数据（参数放在文件中），未完成时自动重试。 |
| get_logs | 查询统计数据（参数放在命令行中），未完成时自动重试。   |
| get_log_all | 迭代式查询更大量的数据，未完成时自动重试。   |
| pull_log | 基于服务器接受时间范围，批量拉取特定shard的数据。   |
| pull_log_dump | 并发批量下载logstore所有shard的数据到本地。    |
| get_cursor |  获取特定服务器时间特定shard的游标（以便基于游标拉取数据）  |
| get_histograms | 获取查询范围内的日志分布。 |

## 支持的时间格式
除了常规的格式，例如："%Y-%m-%d %H:%M:%S CST"的例子"2018-01-02 12:12:10 CST"；
也支持"1 hour ago", "now", "yesterday 0:0:0"等格式了。更多格式也可以参考https://dateparser.readthedocs.io/en/latest/

**相对1分钟:** -1min ~ now， 或 1 min ago ~ now

**相对4小时:** -4h ~ now，或 4 hours ago ~ now 或 4 hour ago 

**相对4天（24小时）:** -1d ~ now，或 1 day ago ~ now  

**相对1周(7x24小时):** -1week ~ now, 或 1 week ago ~ now 

**今天:** today 0:0:0 ~ now  

**昨天:** yesterday 0:0:0 ~ yesterday 23:59:59，或 1 day ago 0:0:0 ~ -1d 23:59:59  

**前天:** the day before yesterday 0:0:0 ~ 2 day ago 23:59:59 



## 例子

### 实时显示当前网站UV

如下命令
```shell
aliyunlog log get_log --project=pdata1 --logstore=log1 --from_time="today 00:00:00" --to_time="now" --query="host: www.dcd.mock-domain.com | select count(distinct remote_addr) as uv" --jmes-filter="join('\n', map(&to_string(uv), @))"
```

每次运行时都会显示今天的独立访问客户的数量


### 定期导出客户端IP列表

```shell
aliyunlog log get_log --project=pdata1 --logstore=log1 --from_time="yesterday 00:00:00" --to_time="yesterday 23:59:59" --query="host: www.dcd.mock-domain.com | select distinct remote_addr" --jmes-filter="join('\n', map(&to_string(remote_addr), @))"
```

以上命令可以在每天0:0:1运行，导出昨天的独立访问客户的列表
