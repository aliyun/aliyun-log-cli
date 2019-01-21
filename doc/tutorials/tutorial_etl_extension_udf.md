# 日志服务CLI ETL - 扩展UDF

# 背景
CLI的命令中，可以看到有一个重要的参数`config`进行ETL的规则配置。这其实是一个Python模块，通过import其他Python模块，或者直接编写符合协议的UDF来扩展ETL的规则。本篇介绍CLI ETL规则的扩展协议与机制。

# 扩展与UDF

## 条件式事件转换UDF

在转换列表中支持UDF扩展：

```python
UDF (Python):
@support_event_list_simple     # 自动支持多事件处理
def update_fields(e):
    e["some_field_x"] = "100"
    del e["some_feild_y"]
    return e   # 也可以返回None(表示丢弃), 返回列表(表示分裂)

TRANSFORM_LIST_data = [  ({"data": "^LTE_Information "},update_fields), "..."]
```

## 字段提取&转换UDF

在转换列表中，支持基于`("字段名", UDF)`方式扩展：

```python
@support_event_list_simple         # 自动支持多事件处理
def remove_fields(e, filed_input):
    del e[filed]
    return e

TRANSFORM_LIST_data = [
  	   ({"data": "^LTE_Information "}, ("internal",remove_fields)  ),
       ({"data": "^Status,"}, ("field_x", V("field_y")  ),
	    "…"]
```

内置方法: **V, CSV, TSV, LOOKUP, KV, JSON**等，都是通过这种方式构建的。

## 全局UDF
基于全局的UDF以及协议

**注意：**
- sls_en_xxx 表示返回一个新的事件（替换），后续日志将使用这个处理
- sls_eu_xxx 表示返回事件部分信息（更新），日志会和这个部分内容合并成给一个新的日志后处理。

1. 事件丢弃: 返回None

```python
def sls_en_xxx(event):
    return None if event.get("error") else event
```

2. 事件替换: 返回一个新的事件 (返回None表示丢弃)
```python
def sls_en_xxx(event):
    event["hello"] = "world"
    return event
```

3. 事件更新: 返回一个字段集合进行补充
```python
def sls_eu_xxx(event):
    return { "field_x": "my value"}
```

4. 事件分裂: 返回一个事件列表

```python
def sls_en_xxx(event):
    return [event, event]
```

## 基于条件的全局UDF

支持基于特定条件的转换，UDF必须以`sls_en_`或者`sls_eu_`开头。

```python
@condition(条件列表 查考#10)
def sls_eu_/sls_en_xxx(event):
	return "…"
```

样例:

```python
@condition({"http_user_agent": r".+\bLinux\b.+"})
def sls_en_windows(event):
    event["is_linux"] = "1"
    return event
```

```python
@condition(NO_EMPTY("real_client_ip"))
def sls_eu_anoymouse_ip(event):
    return {"real_client_ip":
    event["real_client_ip"][:3] + "*****" + event["real_client_ip"][-3:]}
```

## 函数变量式UDF

也可以直接构造以`sls_eu_`或者`sls_en_`开头的变量函数，如下：

```python
from aliyun.log.etl_core import *
sls_en_ke1 = keep_event({"__topic__": "ddos_access_log","cc_phase": r".+"})
sls_en_de1 = drop_event([EMPTY("status"),EMPTY("http_user_agent"),{"http_user_agent": "-"},{"status": r"2\d+"}])
sls_en_kf1 = KEEP_F(["http_user_agent","real_client_ip","remote_addr","status","cc_phase"])
sls_en_kv1 = KV_F([”request_uri",” cookies"])
sls_en_dse1 = dispatch_event([
({"status": lambda x: int(x) // 100 == 3},{"error_type": "challenge"}),
({"status": lambda x: int(x) // 100 == 4},{"error_type": "auth"}),
 ({"status": lambda x: int(x) // 100 == 5},{"error_type": "internal"}),
 (True,DROP)
 ])
sls_en_df1 = DROP_F(["remote_addr"])
sls_en_df2 = DROP_F("http_user_agent")
```

## UDF输入参数说明
以上UDF都有一个event参数，其格式是`Python dict`格式,所有值都是`Unicode`字符串(包括时间)

部分特殊关键字:
**TAG:** `__tag__:host,__tag__:source`,等
**时间:** `__time__`
**主题:** `__topic__`

# 进一步资料
- [日志服务CLI ETL - 介绍与场景](https://yq.aliyun.com/articles/688130)
- [日志服务CLI ETL - 部署与管理](https://yq.aliyun.com/articles/688131)
- [日志服务CLI ETL - 编排与转换](https://yq.aliyun.com/articles/688132)
- [日志服务CLI ETL - 扩展UDF](https://yq.aliyun.com/articles/688133)

# 相关链接
- [日志服务SLS命令行工具（CLI）](https://github.com/aliyun/aliyun-log-cli)
- [依赖的模块Python SDK](https://github.com/aliyun/aliyun-log-python-sdk)
- [Github上的ETL的配置代码案例](https://github.com/aliyun/aliyun-log-python-sdk/tree/master/tests/etl_test)