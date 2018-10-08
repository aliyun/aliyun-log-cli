## 使用CLI了解基础资源使用状况

## 背景
我们知道，日志服务的每个Project有一定的[资源限制](https://help.aliyun.com/document_detail/86660.html)，你是否时常需要知道一些重要资源的使用状况？例如：
1. 一个Project的总shard数量是否已经超过了200个限制？
2. Logtail配置、机器组、报表数等是否快要满了？

现在使用CLI一行命令即可获得相关信息，以便及时提工单申请更大限额。

## 介绍
获取资源使用状况(get_resource_usage)检查传入的Project的所有基础资源，并以Json的形式列出，覆盖如下基础资源：

| 分类 | 限制说明 |
| --- | --- | 
| Logstore | 一个Project中最多可创建200个Logstore。 |
| Shard| 一个Project中最多可创建200个Shard。<br>一个Logstore最多可创建10个Shard。但可以通过分裂操作来增加Shard。|
| Logtail配置（LogtailConfig） | 每个Project最多可创建100个Logtail配置。|
| 机器组（MachineGroup）| 每个Project最多可创建100个机器组。|
| 协同消费组（ConsumerGroup）| 每个Project最多可创建10个协同消费组。|
| 快速查询（SavedSearch） | 每个Project最多可创建100个快速查询。|
| 仪表盘（Dashboard）| 每个Project最多可创建50个仪表盘。|


## 前提
这里假设已经完成了CLI的[安装](http://aliyun-log-cli.readthedocs.io/en/latest/README_CN.html#id1)和[配置](https://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_configure_cli_cn.html).

## 获取基础资源使用状况
一行命令即可获取：

例如：

```shell
aliyunlog log get_resource_usage  --project="my project name"  --format-output=json
```

返回的格式是一个json，例如：

```json
{
  "consumer_group": {
    "count": {
      "status": 8
    },
    "logstores": {
      "access-log": {
        "limitation": 10,
        "status": 7,
        "usage": "70.0%"
      },
      "billdata": {
        "limitation": 10,
        "status": 1,
        "usage": "10.0%"
      }
    }
  },
  "dashboard": {
    "count": {
      "limitation": 50,
      "status": 28,
      "usage": "56.0%"
    }
  },
  "logstore": {
    "count": {
      "limitation": 200,
      "status": 16,
      "usage": "8.0%"
    }
  },
  "logtail": {
    "count": {
      "limitation": 100,
      "status": 2,
      "usage": "2.0%"
    }
  },
  "machine_group": {
    "count": {
      "limitation": 100,
      "status": 1,
      "usage": "1.0%"
    }
  },
  "saved_search": {
    "count": {
      "limitation": 100,
      "status": 11,
      "usage": "11.0%"
    }
  },
  "shard": {
    "count": {
      "limitation": 200,
      "status": 30,
      "usage": "15%"
    },
    "logstores": {
      "access-log": {
        "status": 2
      },
      "billdata": {
        "status": 10
      },
      "test": {
        "status": 2
      },
      "testmax": {
        "status": 2
      },
      "tripdata": {
        "status": 10
      },
      "vedio1": {
        "status": 2
      },
      "web-1": {
        "status": 2
      }
    }
  }
}
```

**注意：**
1. 返回结构包含字段`limitation`与`usage`来表示限制与使用占比，但是这里的是**默认的限制**，如果通过工单增加过额度，这里并不会更新。
2. 这里传入了参数`format-output`来格式化json，如果已经[配置过整个CLI](https://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_configure_cli_cn.html#%E8%BE%93%E5%87%BA%E6%A0%BC%E5%BC%8F)，可以省略。

## 单看shard消耗
有时候我们主要关心一个两个核心指标，并可能仅仅想要一个数字，可以通过`jmes-filter`参数来进行处理，例如这里仅仅查看总的Shard使用情况，可以如下过滤：
```shell
aliyunlog log get_resource_usage  --project="my project name" --jmes-filter="shard.count.status"
> 30
```

这里通过`--jmes-filter="shard.count.status`直接获取输出结果中的shard的目前总数。

更多关于JMES过滤的信息，请参考[这里](http://jmespath.org/specification.html)。