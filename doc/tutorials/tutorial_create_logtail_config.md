# 创建Logtail配置

## 介绍
Logtail是日志服务提供的高性能低耗的日志收集客户端, 参考[这里](https://help.aliyun.com/document_detail/28979.html?spm=5176.doc28967.6.580.TiIpdf)了解更多背景.
目前Logtail的配置有多种, 本节介绍如何快速有效的通过CLI创建各种Logtail的配置项.

### 有哪些Logtail的配置项

Logtail配置项目包含如下内容:

- 基于文本文件的:
  - 极简模式
  - JSON模式
  - 分隔符模式
  - 完整正则表达式模式
- syslog
- 自建产品
  - NGNIX, 本节通过完整正则表达式来完成
  - 飞天日志等

## 准备

这里假设已经完成了CLI的[安装](http://aliyun-log-cli.readthedocs.io/en/latest/README_CN.html#id1).

### 配置域账户

首先CLI中配置默认区域和账户, 以便后续操作, 这一步也是一次性的. 如果之前已经做过, 这里可以跳过.

这里配置一个杭州公有云的账户

```shell
> aliyunlog configure AKID****123 AKKEY****123 cn-hangzhou.log.aliyuncs.com
```

**参考:**

- 关于秘钥的配置, 可以参考[配置](https://help.aliyun.com/document_detail/29064.html?spm=5176.doc29063.2.5.6Jz1cJ)
- 关于日志服务在各个域的Endpoint地址, 可以参考[入口服务](https://help.aliyun.com/document_detail/29008.html?spm=5176.doc29064.2.4.0tdmB5)


## 配置
### 1. 创建极简模式的logtail配置

极简模式是对文件进行单行分隔, 放入到名为`content`的域中的最简单模式. 适用于简单存储处理的情况.

这里我们在项目组`project1`中创建一个极简模式的logtail配置:

```shell
> aliyunlog log create_logtail_config --project_name="project1" --config_detail="file://simple_1.json"
```

文件`simple_1.json`的内容如下: 

```json
{
  "configName": "simple_1",
  "inputDetail": {
    "logType": "common_reg_log",
    "logPath": "/user",
    "filePattern": "*.log"
  },
  "inputType": "file",
  "outputDetail": {
    "logstoreName": "logstore1"
  }
}
```

这里创建了一个属于日志库`logstore1`的名叫`simple_1`的logtail的配置. 主要的配置项就是日志的路径`logPath`以及文件名模式`filePattern`. 这里扫描`/user`下包含深度子目录的所有`.log`文件.

**注意:** 除了以上项目, 还需要如上所示填入相关信息: 其中`inputType`是`file`, `inputDetail.logType`是`common_reg_log`.


#### 时间配置
简单模式的日志时间采用的是系统收集的时间, 也就是抓取到这条日志的时间. 


### 2. 创建JSON模式的logtail配置

JSON模式适用于文件本身就是JSON的情况.

这里我们在项目组`project1`中创建一个JSON模式的logtail配置:

```shell
> aliyunlog log create_logtail_config --project_name="project1" --config_detail="file://json_1.json"
```

文件`json_1.json`的内容如下:
 
```json
{
  "configName": "json_1",
  "inputDetail": {
    "logType": "json_log",
    "filePattern": "*.json",
    "logPath": "/json_1"
  },
  "inputType": "file",
  "outputDetail": {
    "logstoreName": "logstore1"
  }
}
```

这里创建了一个属于日志库`logstore1`的名叫`json_1`的logtail的配置. 主要的配置项就是日志的路径`logPath`以及文件名模式`filePattern`. 这里扫描`/user`下包含深度子目录的所有`.json`文件.

**注意:** 

1. 这里需要按照如上的模板填入相关信息. 其中`inputType`必须是`file`, `inputDetail.logType`是`json_log`.
2. Logtail会根据json的格式自动提取对应的域信息. 例如一个旅行日志的内容如下:

```json
{
  "from": "nanjing",
  "to": "shanghai",
  "people": "xiaoming",
  "travel_time": "2018-1-1 10:10:10"
}
```

会自动配置域`from`, `to`和`people`和`travel_time`.

#### 时间配置
默认情况下, 日志的时间会使用系统时间, 也就是抓取到这条日志的时间. 如果日志本身包含了更加准确的时间, 例如上面旅行日志的例子, 可以在logtail的配置中指定`travel_time`为日志时间如下:
```json
{
  "inputDetail": {
    "timeFormat": "%Y-%M-%D %h:%m:s",
    "timeKey": "travel_time"     
  }
}
```

这里通过`inputDetail.timeKey`指定`travel_time`为时间关键字, 通过`inputDetail.timeFormat`配置其格式为`%Y-%M-%D %h:%m:s`, 针对时间格式, 可以进一步参考[这里](https://help.aliyun.com/document_detail/28980.html?spm=5176.doc28972.6.593.tQYyhr)


### 3. 创建分隔符模式的logtail配置

分隔符模式适用于文件本身基于某个分隔符分隔的文件, 例如CSV, TSV等等. 

日志服务支持最多3个字符组合的分隔, 例如一个旅行日志的文件内如是:

```text
2017-1-1 10:10:00&#&nanjing&#&shanghai&#&xiao ming
2017-1-1 20:10:00&#&beijing&#&hangzhou&#&xiao wang
```

分隔符就是`&#&`可以分隔出`时间`, `出发城市`, `达到城市`, `旅客`. 

这里我们在项目组`project1`中创建一个分隔符模式的logtail配置:

```shell
> aliyunlog log create_logtail_config --project_name="project1" --config_detail="file://sep_1.json"
```

文件`sep_1.json`的内容如下:
 
```json
{
  "configName": "sep_1",
  "logSample": "2017-1-1 10:10:00&#&nanjing&#&shanghai&#&xiao ming",
  "inputDetail": {
    "logType": "delimiter_log",
    "logPath": "/user",
    "filePattern": "travel.log",
    "separator": "&#&",
    "key": [
      "travel_time",
      "from_city",
      "to_city",
      "people"
    ]
  },
  "inputType": "file",
  "outputDetail": {
    "logstoreName": "logstore1"
  }
}
```

这里创建了一个属于日志库`logstore1`的名叫`json_1`的logtail的配置. 主要的配置包括: 

- 日志的路径以及文件名模式. 这里扫描`/user`下包含深度子目录的所有`travel.json`文件.
- 分隔符为`&#&`, 以及对应的域名, 这里是`travel_time`, `from_city`, `to_city`和`people`.
- 值得注意的是, 也需要在域`logSample`中填写一个例子. 
- 其他需要按照如上的模板填入相关信息. 其中`inputType`必须是`file`, `inputDetail.logType`是`delimiter_log`.


注意, 多个域的分隔符必须是一致的, 例如下面的文件,期望配置分隔符`&|`, 并不会起作用. 

```text
2017-1-1 10:10:00&nanjing|&shanghai|xiao ming
2017-1-1 20:10:00|beijing&hangzhou|xiao wang
```

因为这里的文件分隔符并不是一致的, 这种情况就需要用到完整正则表达式的方式了. 

#### 时间配置
默认情况下, 日志的时间会使用系统时间, 也就是抓取到这条日志的时间. 如果日志本身包含了更加准确的时间, 例如上面旅行日志的例子, 可以在logtail的配置中指定`travel_time`为日志时间如下:
```json
{
  "inputDetail": {
    "timeFormat": "%Y-%M-%D %h:%m:s",
    "timeKey": "travel_time"     
  }
}
```

这里指定`travel_time`为时间关键字, 配置其格式为`%Y-%M-%D %h:%m:s`, 针对时间格式, 可以进一步参考[这里](https://help.aliyun.com/document_detail/28980.html?spm=5176.doc28972.6.593.tQYyhr)

### 4. 创建不可见字符的分隔的logtail配置

对于一些不可见字符, 可以在`separator`域中使用转义: 

| 特殊字符 | 字符 |
| ---- | --- |
| 双引号 | \\" |
| 反斜杠 | \\ \\ |
| 斜杠   | \\/ |
| 回退符 | \\b |
| 换页符 | \\f |
| 换行符 | \\n |
| 回车符 | \\r |
| 横向制表符 | \\t |
| 纵向制表符 | \\v |
| \\u 0000 | 任意字符 |


例如，这里我们在项目组`project1`中创建一个分隔符为`\u0001`的的logtail配置:

```shell
> aliyunlog log create_logtail_config --project_name="project1" --config_detail="file://sep_2.json"
```

文件`sep_2.json`的内容如下:
 
```json
{
  "configName": "sep_1",
  "logSample": "2017-1-1 10:10:00\u0001nanjing\u0001shanghai\u0001xiao ming",
  "inputDetail": {
    "logType": "delimiter_log",
    "logPath": "/user",
    "filePattern": "travel.log",
    "separator": "\u0001",
    "key": [
      "travel_time",
      "from_city",
      "to_city",
      "people"
    ]
  },
  "inputType": "file",
  "outputDetail": {
    "logstoreName": "logstore1"
  }
}
```

**注意:** 通过CLI配置了不可见字符作为分隔符后，再进入Web控制台编辑这个Logtail配置页面是看不到这些字符，但点击按钮`下一步`继续其他的配置是不受影响的。


### 5. 创建正则表达式模式的logtail配置


正则表达式模式利用了强大的正则表达式的解析能力, 提取非结构化文本中的特定模式的域. 适用于文件本身结构较为特殊的情况.
完整的正则表达式可以参考[这里](https://en.wikipedia.org/wiki/Regular_expression)  

一个典型的例子是NGNIX日志:

```text
10.1.1.1 - - [2018-1-1 10:10:10] "GET / HTTP/1.1" 0.011 180 404 570 "-" "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; 360se)"
10.1.1.1 - - [2018-1-1 10:10:20] "GET / HTTP/1.1" 0.011 180 404 570 "-" "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; 360se)"
```

可以看到模式是: `IP - - [时间] "HTTP请求" 响应时间 请求大小 HTTP状态号 响应大小 "-" "客户端"`
这里用对应的正则表达式是: `(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[([^\]+])\] "([\w\s\/\.]+) ([\d\.]+) ([\d\.]+) ([\d\.]+) ([\d\.]+) "-" "[^\"]+"`  

这里我们在项目组`project1`中创建一个正则表达式模式的logtail配置:

```shell
> aliyunlog log create_logtail_config --project_name="project1" --config_detail="file://reg_1.json"
```

文件`reg_1.json`的内容如下:
 
```json
{
  "configName": "ngnix_1",
  "logSample": "10.1.1.1 - - [13/Mar/2016:10:00:10 +0800] \"GET / HTTP/1.1\" 0.011 180 404 570 \"-\" \"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; 360se)\"",
  "inputDetail": {
    "logType": "common_reg_log",
    "logPath": "/ngnix",
    "filePattern": "*.log",
    "regex": "(\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}) - - \\[([^\\]+])\\] \"([\\w\\s\/\\.]+) ([\\d\\.]+) ([\\d\\.]+) ([\\d\\.]+) ([\\d\\.]+) \"-\" \"[^\\\"]+\"",
    "key": [
      "client_ip",
      "request_time",
      "method_type",
      "process_period",
      "request_bytes",
      "http_status",
      "response_bytes",
      "client_agent"
    ],
    "timeFormat": "%Y-%M-%D %h:%m:%s"
  },
  "inputType": "file",
  "outputDetail": {
    "logstoreName": "logstore1"
  }
}
```

这里创建了一个属于日志库`logstore1`的名叫`ngnix_1`的logtail的配置. 主要的配置包括:

- 日志的路径以及文件名模式. 这里扫描`/ngnix`下包含深度子目录的所有`*.log`文件.
- 正则表达式写在`regex`中, 以及对应的域名放在`key`中. 
- 这里也需要在域`logSample`中填写一个例子.
- 其他需要按照如上的模板填入相关信息. 其中`inputType`必须是`file`, `inputDetail.logType`是`delimiter_log`.


#### 时间配置
默认情况下, 日志的时间会使用系统时间, 也就是抓取到这条日志的时间. 如果日志本身包含了更加准确的时间, 例如上面NGNIX日志的例子, 可以在logtail的配置中指定`request_time`为日志时间如下:
```json
{
  "inputDetail": {
    "timeKey": "request_time",
    "timeFormat": "%Y-%M-%D %h:%m:s"
  }
}
```

这里通过`inputDetail.timeFormat`配置其格式为`%Y-%M-%D %h:%m:s`, 针对时间格式, 可以进一步参考[这里](https://help.aliyun.com/document_detail/28980.html?spm=5176.doc28972.6.593.tQYyhr)

**注意:** 如果只配置了`inputDetail.timeFormat`而没有配置`inputDetail.timeKey`, 默认使用域`time`. 


### 6. 创建syslog的logtail配置


syslog与文件方式互补, 收集部署上更方便. 除了通过CLI进行配置外, 还需要在logtail客户端通过本地配置文件的方式进行进一步配置. 具体参考[这里](https://help.aliyun.com/document_detail/48932.html?spm=5176.doc43759.6.588.2Hwrdk).


这里我们在项目组`project1`中创建一个syslog模式的logtail配置:

```shell
> aliyunlog log create_logtail_config --project_name="project1" --config_detail="file://syslog_1.json"
```

文件`syslog_1.json`的内容如下:
 
```json
{
  "configName": "syslog_1",
  "inputDetail": {
    "tag": "tag1"
  },
  "inputType": "syslog",
  "outputDetail": {
    "logstoreName": "logstore1"
  }
}
```

这里创建了一个属于日志库`logstore1`的名叫`syslog_1`的logtail的配置. 主要的配置包括: 

- 标签`tag`.
- 其他需要按照如上的模板填入相关信息. 其中`inputType`必须是`syslog`, 注意这里没有域`inputDetail.logType`.


#### 时间配置
要想让syslog配置其作用, 除了通过CLI进行配置外, 还需要在logtail客户端通过本地配置文件的方式进行进一步配置. 具体参考[这里](https://help.aliyun.com/document_detail/48932.html?spm=5176.doc43759.6.588.2Hwrdk).
对于时间的配置, 目前syslog使用系统时间来作为日志的时间. 

## 高级配置项


### 配置多行日志

很多应用的日志可能偶尔会出现多行的情况, 例如Java的日志会打印一些堆栈信息. 这种情况就需要多行配置. 
**注意:** 目前仅`正则表达式模式`支持多行配置.

例如: 
```text
com.journaldev.log.LoggingExample::main::2017-1-1 01:42:43::Msg977
com.journaldev.log.LoggingExample::main::2017-1-1 03:42:43::Break at
  File "/Applications/PyCharm CE.app/Contents/helpers/pydev/pydevd.py", line 1599, in <module>
    globals = debugger.run(setup['file'], None, None, is_module)
  File "/Applications/PyCharm CE.app/Contents/helpers/pydev/pydevd.py", line 1026, in run
    pydev_imports.execfile(file, globals, locals)  # execute the script
  File "/Users/wjo1212/GithubProjects/aliyun-log-cli/aliyunlogcli/cli.py", line 5, in <module>
    main()
com.journaldev.log.LoggingExample::main::2017-1-1 05:42:43::Msg978
``` 

这种情况就需要配置`logBeginRegex`来指定每一条日志的首行模式:
```json
{
  "inputDetail": {
    "logBeginRegex": "com.journaldev.log.LoggingExample::main::.*"
  }
}
```

这里配置了`inputDetail.logBeginRegex`指定了每行新的日志都是以`com.journaldev.log.LoggingExample::main::.*`作为第一行的. 

**注意:** 这里的正则表达式最后使用了`.*`对首行进行**完整**匹配. 这一点是必须的, 例如如下的配置将不起作用:

```json
{
  "inputDetail": {
    "logBeginRegex": "com.journaldev.log.LoggingExample::main::"
  }
}
```


### Logtail客户端的解析配置
Logtail也支持针对特定目标文件, 定义一些高级行为, 所有基于文本的收集方式都支持如下配置:


- 本地缓存 (localStorage): 
    - 当日志服务不可用时，日志缓存在机器本地目录，服务恢复后进行续传，默认最大缓存值1GB
    - 默认打开(true)
- 上传原始日志 (enableRawLog)：
    - 开启该功能后默认会新增字段将原始日志内容一并上传
    - 默认关闭 (false)
- Topic生成方式 (topicFormat)：
    - 支持: 
        - 空(`none`): 不配置主题.
        - 机器组(`group_topic`): 基于所引用的机器组的Topic属性来配置. 
        - 基于文件名的正则表达式: 用正则式从路径里提取一部分内容作为Topic。可以用于区分具体用户或实例产生的日志数据。
    - 关于主题, 查考[这里](https://help.aliyun.com/document_detail/60069.html?spm=5176.2020520112.113.2.33495429pAo4ru)
    - 默认是空-不生成主题(none)
- 日志文件编码 (fileEncoding)：
    - 目前支持`utf8`和`gbk`
    - 默认是`utf8`
- 最大监控目录深度 (maxDepth)：
    - 指定从日志源采集日志时，监控目录的最大深度，即最多监控几层日志。最大目录监控深度范围0-1000，0代表只监控本层目录。
    - 默认是100
- 超时属性 (preserve)
    - 如果一个日志文件在指定时间内没有任何更新，则认为该文件已超时。您可以对超时属性指定以下配置。
        - `永不超时`(true): 指定持续监控所有日志文件，永不超时。
        - `超时30分钟超时`(false): 如日志文件在30分钟内没有更新，则认为已超时，并不再监控该文件。
    - 默认`永不超时`(true)
- 最大超时目录深度 (preserveDepth)：
    - 当配置为`30分钟超时`时, 需要配置深度, 范围1-3
- 过滤器配置：
    - 日志只有完全符合过滤器中的条件才会被收集。
    - 分别配置过滤关键字`filterKey`和对应内容正则表达式`filterRegex`. 

如下示例, 这里关闭了`本地存储`, 打开了`原始文件上传`, 配置了一个自定义的`基于正则表达式的Topic方式`, 文件编码为`gbk`, 最大目录深度`200`, `检测文件变化`30分钟, 对应深度为3. 同时配置了只抓取关键字`from_city`和`to_city`满足特定正则的日志.. 

```json
{
  "inputDetail": {
    "localStorage": false,
    "enableRawLog": true,
    "topicFormat": "/user.+/(\\w+).log",
    "fileEncoding": "gbk",
    "maxDepth": 200,
    "preserve": false,
    "preserveDepth": 3,
    "filterKey": [
      "from_city",
      "to_city"
    ],
    "filterRegex": [
      "nanjing|shanghai",
      "beijing|hangzhou"
    ]
  }
}
```

## 后续操作
完成Logtail的配置后, 还需要应用配置到机器组, 可以通过操作[apply_config_to_machine_group]([http://aliyun-log-cli.readthedocs.io/en/latest/api.html#apply-logtail-config)来完成.
