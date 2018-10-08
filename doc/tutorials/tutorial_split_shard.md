## 使用CLI配置更多的shard

## 背景
我们知道，日志服务的每个Project有一定的[资源限制](https://help.aliyun.com/document_detail/86660.html)，你是否遇到如下情况呢？
1. 创建Shard时，最多配置10个Shard，但是预期Logstore会有更大数据量写入尤其是查询读取需求？
2. 手工在Web控制台进行分裂，因为无法把握均匀分布，且点击较多，比较低效？

现在使用CLI一行命令即可配置Logstore到期望的数量了！

## 介绍
CLI通过命令`arrange_shard`来自动将目标logstore的shard数量均匀分裂为期望的数量（最多到100个甚至更多）。

## 前提
这里假设已经完成了CLI的[安装](http://aliyun-log-cli.readthedocs.io/en/latest/README_CN.html#id1)和[配置](https://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_configure_cli_cn.html).

## 配置shard数量
例如：

```shell
aliyunlog log arrange_shard --project=my_project1 --logstore=my_logstore1 --count=50
```

这里配置目标logstore的shard数量为50个。

## 原理与注意事项
命令`arrange_shard`根据期望shard的数量，以及目前shard分区范围，自动均匀的将目前分裂。

**注意：**
1. 这个命令也是通过`split_shard`进行分裂，因此分裂过程中会制造出多个只读的shard。在一个Project最多有200个shard的情况下，如果一个Project只包含一个logstore，这个logstore可以配置为最多100个读写shard。
2. 因为服务器同步的原因，分裂命令完成后，在Web控制台一般需要1分钟左右可以看到最新shard数量。


