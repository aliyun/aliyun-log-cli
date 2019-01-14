## 使用CLI进行高速跨域日志复制、历史数据重新索引与数仓投递

## 背景
使用日志服务是不是常常遇到如下烦恼？
1. 开启了字段索引却无法对历史日志起作用，而手动重建索引又很困难怎么办？
2. 需要迁移数据，复制数据到其他区域logstore，写代码实现大并发复制又很复杂怎么办？
3. 投递日志到OSS/ODPS仅仅对新数据起作用，又想投递历史日志怎么办？

现在使用CLI就可以帮你轻松实现这些操作。

## 介绍
复制数据(CopyData)支持将特定时间范围内的logstore的数据复制到特定logstore中去。其具备如下一些特点:

1. 没有索引的数据也可以同步.
2. 速度快, 易并发, 且支持传输压缩.
3. 拉取的数据按照服务器接受的时间排序.
4. 支持跨域、跨项目库复制。
5. 支持复制数据到同一个logstore（重新索引）。

## 前提
这里假设已经完成了CLI的[安装](http://aliyun-log-cli.readthedocs.io/en/latest/README_CN.html#id1).

### 配置多区域账户

首先CLI中配置多个区域账户, 以便后续操作, 这一步也是一次性的. 如果之前已经做过, 这里可以跳过.

这里配置2个域的账户, 一个杭州公有云, 一个北京公有云.

```shell
> aliyunlog configure AKID****123 AKKEY****123 cn-hangzhou.log.aliyuncs.com
> aliyunlog configure AKID****123 AKKEY****123 cn-beijing.log.aliyuncs.com bj
```

**注意:** 这里的最后一个参数, 仅仅用于表明这个账户的名字, 以便后续使用. 不传入默认是`main`, 也是默认使用的账户, 这里使用杭州的账户作为默认账户.

**参考:**

- 关于秘钥的配置, 可以参考[配置](https://help.aliyun.com/document_detail/29064.html?spm=5176.doc29063.2.5.6Jz1cJ)
- 关于日志服务在各个域的Endpoint地址, 可以参考[入口服务](https://help.aliyun.com/document_detail/29008.html?spm=5176.doc29064.2.4.0tdmB5)

## 重新索引
如果因为某些特定原因，某个时间范围内的日志没有建立索引，无法被查询和统计。可以如下操作将日志重新写入，就可以实现重新索引的效果。

例如：

```shell
aliyunlog log copy_data --project="源project" --logstore="源logstore" --from_time="2018-09-05 0:0:0+8:00" --to_time="2018-09-06 0:0:0+8:00"
```

这里将杭州区域的`源project`的`源logstore`中服务器在时间范围["2018-09-05 0:0:0+8:00","2018-09-06 0:0:0+8:00")内接收到的数据，重新写入到`源logstore`中去。

**注意：**
这里仅仅是复制一份数据进入目标logstore，并在写入时自动对其索引，原来的没有被索引的日志依然存在。

## 跨区域复制数据
有时需要将某一个logstore的日志迁移到另外一个logstore中去时，可以如下操作：

### 准备好目标logstore
假设目标logstore已经创建好了，并且配置好了索引。这一步操作可以在Web控制台完成，也可以通过CLI的[复制logstore配置](https://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_manage_cross_region_copy.html)来完成，或者使用CLI的[create_logstore](https://aliyun-log-cli.readthedocs.io/en/latest/api.html#aliyun.log.LogClient.copy_logstore)创建日志库，再配置索引，通过命令[get_index_config](https://aliyun-log-cli.readthedocs.io/en/latest/api.html#aliyun.log.LogClient.get_index_config)获取索引，调用命令[create_index](https://aliyun-log-cli.readthedocs.io/en/latest/api.html#aliyun.log.LogClient.create_index)来实现。


### 复制数据

例如：

```shell
aliyunlog log copy_data --project="源项目" --logstore="源logstore" --from_time="2018-09-05 0:0:0+8:00" --to_time="2018-09-06 0:0:0+8:00" --to_project="目标project" --to_logstore="目标logstore" --to_client="bj"
```

这里将杭州区域的`源project`的`源logstore`中服务器在时间范围["2018-09-05 0:0:0+8:00","2018-09-06 0:0:0+8:00")内接收到的数据，写入到`北京`区域的`目标project`的`目标logstore`中去。

**注意:**
这里用`--to_client`指定操作目标project的账户为`bj`，是前面前提中配置的账户名。


### 投递历史日志到OSS/ODPS
日志服务的投递任务配置好后，仅仅对新接受数据产生作用。这里也可以借助复制数据来实现投递历史日志的效果：

1. 创建一个临时的logstore（不需要配置索引）
2. 在临时logstore上配置投递OSS/ODPS的任务
3. 复制需要投递的日志到目标logstore
4. 投递结束后，删除临时logstore


## 时间格式
时间格式推荐是`%Y-%m-%d %H:%M:%S %Z`, 如`2018-01-24 17:00:00+8:00`, 但也支持其他合法的时间格式, 例如:`Jan 01 2018 10:10:10+8:00`

**注意：** `+8:00`是时区信息.

CLI还支持更多其他格式的时间格式，例如`2 day ago`等，参考[这里](https://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_human_readable_datetime.html).


## 时间范围
传入的时间范围, 需要注意几点:

1. 这里的时间指的是服务器接受日志的时间

2. 时间的范围是左闭右开`[)`, 上面例子中`16:00:00`服务器接受到的日志会被拉取到, 但是`17:00:00`服务器所接受到的日志不会.


## 特殊的时间范围
有时我们不关心数据的某一边界, 例如期望获得所有存储的数据到某一天日期位置. 或者获取从某一天开始到目前存储的数据为止的话, 就可以使用特殊游标. 

特殊游标包括`begin`和`end`. 例如:

```shell
aliyunlog log copy_data --project="p1" --logstore="l1" --from_time="begin" --to_time="2018-01-24 17:00:00+8:00" --to_logstore="l2"
```

这里复制所有`2018-01-24 17:00:00+8:00`之前服务器接收到的日志到logstore`l2`。


又例如:

```shell
aliyunlog log copy_data --project="p1" --logstore="l1" --from_time="2018-01-24 17:00:00+8:00" --to_time="end" --to_logstore="l2"
```

这里复制所有`2018-01-24 17:00:00+8:00`开始及之后服务器接收到的日志到logstore`l2`。