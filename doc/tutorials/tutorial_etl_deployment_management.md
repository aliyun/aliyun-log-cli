# 日志服务CLI ETL - 部署与管理

# 背景
本文介绍日志服务CLI ETL功能的安装部署、性能扩展安全性、以及如何监控管理ETL的运行。

# 安装与配置

## 安装
推荐使用`Pypy3`来运行，具体参考[CLI安装](https://github.com/aliyun/aliyun-log-cli/blob/master/README_CN.md#%E5%AE%89%E8%A3%85)

注意：需要确保`Python SDK`保持最新：
`pypy3 -m pip install aliyun-log-python-sdk>=0.6.42`

## 配置：
需要配置相关的日志库的入口与账户信息，具体参考[CLI配置](https://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_configure_cli_cn.html)

# 运行

## 命令参数
通过命令行：
```shell
aliyunlog log transform_data
```

可以获得完整的命令行参数，如下：
```shell
Usage:
aliyunlog log transform_data --project=<value> --logstore=<value> --config=<value> --from_time=<value> [--to_time=<value>] [--to_client=<value>] [--to_project=<value>] [--to_logstore=<value>] [--shard_list=<value>] [--batch_size=<value>] [--compress=<value>] [--cg_name=<value>] [--c_name=<value>] [--cg_heartbeat_interval=<value>] [--cg_data_fetch_interval=<value>] [--cg_in_order=<value>] [--cg_worker_pool_size=<value>] [--access-id=<value>] [--access-key=<value>] [--region-endpoint=<value>] [--client-name=<value>] [--jmes-filter=<value>] [--format-output=<value>] [--decode-output=<value>]

Options:
--project=<value> 		: project name
--logstore=<value> 		: logstore name
--config=<value> 		: transform config imported or path of config (in python)
--from_time=<value> 		: curosr value, could be begin, timestamp or readable time in readable time like "%Y-%m-%d %H:%M:%S<time_zone>" e.g. "2018-01-02 12:12:10+8:00", also support human readable string, e.g. "1 hour ago", "now", "yesterday 0:0:0", refer to https://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_human_readable_datetime.html
[--to_time=<value>] 		: curosr value, leave it as None if consumer group is configured. could be begin, timestamp or readable time in readable time like "%Y-%m-%d %H:%M:%S<time_zone>" e.g. "2018-01-02 12:12:10+8:00", also support human readable string, e.g. "1 hour ago", "now", "yesterday 0:0:0", refer to https://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_human_readable_datetime.html
[--to_client=<value>] 		: logclient instance, if empty will use source client
[--to_project=<value>] 		: project name, if empty will use source project
[--to_logstore=<value>] 		: logstore name, if empty will use source logstore
[--shard_list=<value>] 		: shard number list. could be comma seperated list or range: 1,20,31-40
[--batch_size=<value>] 		: batch size to fetch the data in each iteration. by default it's 500
[--compress=<value>] 		: if use compression, by default it's True
[--cg_name=<value>] 		: consumer group name. must configure if it's consumer group mode.
[--c_name=<value>] 		: consumer group name for consumer group mode,  default:  CLI-transform-data-${process_id}
[--cg_heartbeat_interval=<value>] 		: cg_heartbeat_interval, default 20
[--cg_data_fetch_interval=<value>] 		: cg_data_fetch_interval, default 2
[--cg_in_order=<value>] 		: cg_in_order, default False
[--cg_worker_pool_size=<value>] 		: cg_worker_pool_size, default 2
```

## 批量运行
是否使用`cg_name`在批量运行与持续运行之间进行切换，当没有`cg_name`参数时，进行批量运行，在配置的数据范围内运行完后，命令行退出。
执行批量任务的区间可以通过如下参数配置：
- `from_time`与`to_time`配置处理此段时间内服务器接受到的日志，具体格式参考以上注释。
- `shard_list`用来配置上述时间内的那个分区，具体格式参考以上注释。

例如：这里仅仅针对`shard 0`做一个2分钟的数据ETL做一个检验：

```shell
aliyunlog log transform_data --config=./my_etl.py --project=p1 --logstore=abc --to_project=p2 --to_logstore=xyz --to_client=account1 --client-name=account2 --shard_list=0 --from_time="2019-1-15 12:59:00+8:00" --to_time="2019-1-15 13:01:00+8:00"
```

## 持续运行
当配置了`cg_name`参数时，将激活消费组模式，进行持续实时的消费。

例如这里，额外增加一个参数`cg_name`即可（表示消费组名称）：
```shell
aliyunlog log transform_data --config=./my_etl.py --project=p1 --logstore=abc --to_project=p2 --to_logstore=xyz --to_client=account1 --client-name=account2 --from_time="2019-1-15 12:59:00+8:00" --cg_name="elt1"
```

## 推荐方式
对于历史日志，可以使用批量方式运行，如果需要持续的ETL，建议使用消费组进行持续运行，无论从稳定性、可靠性和扩展性角度，消费组的持续运行模式都要简单和适合的多。


# 架构相关
## 性能
### 启动多个消费者
无论是批量运行、还是持续运行都可以并发跑多个，其中批量运行，需要手工通过配置参数来进行任务切分。而持续运行时，并不需要，消费组会自动切分，因此确保传入相同的参数，尤其是`cg_name`即可。

例如基于消费组的程序可以直接启动多次以便达到并发作用：

```shell
nohup aliyunlog log  transform_data .... cg_name="etl1"   &
nohup aliyunlog log  transform_data .... cg_name="etl1"   &
...
```

**注意:**
所有消费者使用了同一个消费组的名字和不同的消费者名字（因为消费者名以进程ID为后缀）。
因为一个分区（Shard）只能被一个消费者消费，假设一个日志库有10个分区，那么最多有10个消费者同时消费。

### 性能吞吐
基于测试，在没有带宽限制、接收端速率限制的情况下，以推进硬件用`pypy3`运行，单个消费者占用大约`10%的单核CPU`下可以消费达到`5 MB/s`原始日志的速率。因此，理论上可以达到`50 MB/s`原始日志`每个CPU核`，也就是`每个CPU核每天可以消费4TB原始日志`。


## 安全

推荐奖机器与源日志库或者目标日志库在一个Region中，并使用内网入口。具体参考：
https://help.aliyun.com/document_detail/29008.html

### Https
如果服务入口（endpoint）配置为`https://`前缀，如`https://cn-beijing.log.aliyuncs.com`，程序与SLS的连接将自动使用HTTPS加密。

服务器证书`*.aliyuncs.com`是GlobalSign签发，默认大多数Linux/Windows的机器会自动信任此证书。如果某些特殊情况，机器不信任此证书，可以参考[这里](https://success.outsystems.com/Support/Enterprise_Customers/Installation/Install_a_trusted_root_CA__or_self-signed_certificate)下载并安装此证书。


## 高可用性
消费组会将检测点（check-point）保存在服务器端，当一个消费者停止，另外一个消费者将自动接管并从断点继续消费。

可以在不同机器上启动消费者，这样当一台机器停止或者损坏的清下，其他机器上的消费者可以自动接管并从断点进行消费。

理论上，为了备用，也可以启动大于shard数量的消费者。


# 管理相关
## 检测
每一个日志库（logstore）最多可以配置10个消费组，如果遇到错误`ConsumerGroupQuotaExceed`则表示遇到限制，建议在控制台端删除一些不用的消费组。

其他相关议题：
- [在控制台查看消费组状态](https://help.aliyun.com/document_detail/43998.html)
- [通过云监控查看消费组延迟，并配置报警](https://help.aliyun.com/document_detail/55912.html)


# 进一步资料
- [日志服务CLI ETL - 介绍与场景](https://yq.aliyun.com/articles/688130)
- [日志服务CLI ETL - 部署与管理](https://yq.aliyun.com/articles/688131)
- [日志服务CLI ETL - 编排与转换](https://yq.aliyun.com/articles/688132)
- [日志服务CLI ETL - 扩展UDF](https://yq.aliyun.com/articles/688133)

# 相关链接
- [日志服务SLS命令行工具（CLI）](https://github.com/aliyun/aliyun-log-cli)
- [依赖的模块Python SDK](https://github.com/aliyun/aliyun-log-python-sdk)
- [Github上的ETL的配置代码案例](https://github.com/aliyun/aliyun-log-python-sdk/tree/master/tests/etl_test)
