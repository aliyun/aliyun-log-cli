# Elasticsearch 数据迁移

## 概述
使用日志服务 CLI 可以方便您快速将 Elasticsearch 中的数据导入日志服务。

## 配置

| 参数 | 必选 | 说明 | 样例 |
| -------- | -------- | -------- | -------- |
| hosts | yes | elasticsearch 数据源地址列表，多个 host 之间用逗号分隔。 | 127.0.0.1:9200<br>localhost:9200,other_host:9200<br>user:secret@localhost:9200 |
| project_name | yes | 日志服务中用于存储迁移数据的 project。<br>需要您提前创建好。 | your_project |
| indexes | no | elasticsearch index 列表，多个 index 之间用逗号分隔，支持通配符(*)。<br>默认抓取目标 es 中所有 index 的数据。 | index1<br>my_index*,other_index |
| query | no | 用于过滤文档，使用该参数您可以指定需要迁移的文档。<br>默认不会对文档进行过滤。 | '{"query": {"match": {"title": "python"}}}' |
| scroll | no | 用于告诉 elasticsearch 需要将查询上下文信息保留多长时间。<br>默认值为 5m。 | 5m |
| logstore_index_mappings | no | 用于配置日志服务中的 logstore 和 elasticsearch 中的 index 间的映射关系。支持使用通配符指定 index，多个 index 之间用逗号分隔。<br>可选参数，默认情况下 logstore 和 index 是一一映射，这里允许用户将多个index 上的数据发往一个 logstore。 | '{"logstore1": "my_index\*", "logstore2": "index1,index2", "logstore3": "index3"}'<br>'{"your_logstore": "\*"}'  |
| pool_size | no | 指定用于执行迁移任务的进程池大小。<br>CLI 会针对每个 shard 创建一个数据迁移任务，任务会被提交到进程池中执行。<br>默认为 min(10, shard_count)。 | 10 |
| time_reference | no | 将 elasticsearch 文档中指定的字段映射成日志的 time 字段。<br>默认使用当前时间戳作为日志 time 字段的值。 | field1 |
| source | no | 指定日志的 source 字段的值。<br>默认值为参数 hosts 的值。 | your_source |
| topic | no | 指定日志的 topic 字段的值。<br>默认值为空。 | your_topic |
| wait_time_in_secs | no | 指定 logstore、索引创建好后，CLI 执行数据迁移任务前需要等待的时间。<br>默认值为 60，表示等待 60s。 | 60 |
| auto_creation | no | 指定是否让 MigrationManager 为您自动创建好 logstore 和 索引。<br>默认值为 True，表示自动创建。 | True<br>False |

> aliyun-log-cli.readthedocs.io 无法正常显示表格，请参阅[tutorial_es_migration_cn.md](https://github.com/aliyun/aliyun-log-cli/blob/master/doc/tutorials/tutorial_es_migration_cn.md)

## 数据映射
### logstore - index
CLI 默认会将 Elasticsearch index 中的数据迁移至同名的 logstore 中，当然您也可以通过参数 logstore_index_mappings 指定将多个 index 中的数据迁移至一个 logstore。

logstore 不必事先创建，如果 CLI 发现目标 logstore 未创建，会为您在指定的 project 下创建好。

### 数据类型映射
CLI 会根据 Elasticsearch 的[数据类型](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-types.html) 在index 对应的 logstore 中创建好索引。

- Core datatypes

| Elasticsearch | 日志服务 |
| -------- | -------- |
| text | text |
| keyword | text，不分词 |
| long | long |
| integer | long |
| short | long |
| byte | long |
| double | double |
| float | double |
| half_float | double |
| scaled_float | double |
| date | text |
| boolean | text，不分词 |
| binary | n/a |
| integer_range | json |
| float_range | json |
| long_range | json |
| double_range | json |
| date_range | json |
| ip_range | text，不分词 |

- Complex datatypes

| Elasticsearch | 日志服务 |
| -------- | -------- |
| Array datatype | n/a |
| Object datatype | json |
| Nested datatype | n/a |

- Geo datatypes

| Elasticsearch | 日志服务 |
| -------- | -------- |
| Geo-point datatype | text |
| Geo-Shape datatype | text |

- Specialised datatypes

| Elasticsearch | 日志服务 |
| -------- | -------- |
| IP datatype | text，不分词 |
| Completion datatype | n/a |
| Token count datatype | n/a |
| mapper-murmur3 | n/a |
| Percolator type | n/a |
| join datatype | n/a |

## 抓取模式
- 为了提高吞吐量，CLI 会为每个 index 的每个 shard 创建一个数据迁移任务，并提交到内部进程池中执行。
- 当全部任务执行完成后，CLI 才会退出。

## 任务执行情况展示
CLI 默认把任务执行情况存储在~/aliyunlogcli.log中, 也可以配置~/.aliyunlogcli中__loggging__来调整信息存储位置和格式:

```
[__logging__]
filename=~/es_migration.log
level=info
```

- 单个迁移任务执行结果展示。

```
========Tasks Info========
...
task_id=1, slice_id=1, slice_max=10, hosts=localhost:9200, indexes=None, query=None, project=test-project, time_cost_in_seconds=128.71100688, status=CollectionTaskStatus.SUCCESS, count=129330, message=None
...

编号为 1 的迁移任务执行成功，耗时 128.7s，迁移文档数量 129330。
```

- 迁移任务执行结果汇总信息。

```
========Summary========
Total started task count: 10
Successful task count: 10
Failed task count: 0
Total collected documentation count: 1000000

MigrationManager 总共启动了 10 个数据数据迁移任务，全部执行成功。迁移文档总数 1000000。
```

## 使用样例

- 将 hosts 为 `localhost:9200` 的 Elasticsearch 中的所有文档导入日志服务的项目 `project1` 中。

```
aliyunlog log es_migration --hosts=localhost:9200 --project_name=project1
```

- 指定将 Elasticsearch 中索引名以 `myindex_` 开头的数据写入日志库 `logstore1`，将索引 `index1,index2` 中的数据写入日志库 `logstore2` 中。

```
aliyunlog log es_migration --hosts=localhost:9200,other_host:9200 --project_name=project1 --logstore_index_mappings='{"logstore1": "myindex_*", "logstore2": "index1,index2"}}'
```

- 使用参数 query 指定从 Elasticsearch 中抓取 `title` 字段等于 `python` 的文档，并使用文档中的字段 `date1` 作为日志的 time 字段。

```
aliyunlog log es_migration --hosts=localhost:9200 --project_name=project1 --query='{"query": {"match": {"title": "python"}}}'
```

- 使用 HTTP 基本认证`user:secret@localhost:9200`，从 Elasticserch 中迁移数据。
```
aliyunlog log es_migration --hosts=user:secret@localhost:9200 --project_name=project1
```


## 常见问题
**Q**：是否支持抓取特定时间范围内的 ES 数据？

**A**：ES 本身并没有内置 time 字段，如果文档中某个字段代表时间，可以使用参数 query 进行过滤。


