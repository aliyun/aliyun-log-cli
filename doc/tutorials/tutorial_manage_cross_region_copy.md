# 跨域复制项目配置

## 介绍
日志服务是在域(Region)范围内以项目(Project)为边界进行操作的, 典型场景下客户会在多个域部署同一套日志项目和日志库来接受日志和查询日志的服务.
因此常常需要跨域复制多个项目的配置. 使用日志服务的CLI可以比较容易的达到这点.

## 哪些数据需要复制

通常一个日志服务的配置包含以下部分:

- 多个日志库(logstore), 以及其下面的
  - 索引配置
  - logtail配置

日志库也包含以下配置, 但是一般多个区域内的配置会有所不同, 一般不需要复制.

  - 机器组
  - 机器组和logtail配置的关联

**注意:** CLI也支持机器组相关复制, 但需要额外参数打开.

## 复制项目配置到其他域

这里假设已经完成了CLI的[安装](http://aliyun-log-cli.readthedocs.io/en/latest/README_CN.html#id1).

### 1. 配置多区域账户

首先CLI中配置多个区域账户, 以便后续操作, 这一步也是一次性的. 如果之前已经做过, 这里可以跳过.

这里配置2个域的账户, 一个杭州公有云, 一个北京公有云.

```shell
> aliyunlog configure AKID****123 AKKEY****123 cn-hangzhou.log.aliyuncs.com hz
> aliyunlog configure AKID****123 AKKEY****123 cn-beijing.log.aliyuncs.com bj
```

**注意:** 这里的最后一个参数, 用于表明这个账户的名字, 以便后续使用. 不传入默认是`main`, 也是默认使用的账户.

**参考:**

- 关于秘钥的配置, 可以参考[配置](https://help.aliyun.com/document_detail/29064.html?spm=5176.doc29063.2.5.6Jz1cJ)
- 关于日志服务在各个域的Endpoint地址, 可以参考[入口服务](https://help.aliyun.com/document_detail/29008.html?spm=5176.doc29064.2.4.0tdmB5)

### 2. 复制项目组配置到目标域

假设我们需要将杭州公有云的项目组`project1`复制到北京公有云, 这可以这样操作:

```shell
> aliyunlog log copy_project --from_project="project1" --to_project="project1" --client-name=hz --to_client=bj
```

这里CLI就会使用账户`hz`来读取源项目组`project1`的相关配置, 并使用账户`bj`来构建一个新的项目组`project1`.
如果使用默认账户读取读取源项目组, 可以省略参数`--client-name`

### 3. 同域项目组配置复制

某些特殊情况, 我们需要在同一个域内复制项目组并保留所有配置项. 

这里我们复制账户`bj`下的`project1`为`project2`: 

```shell
> aliyunlog log copy_project --from_project="project1" --to_project="project2" --copy_machine_group=true --client-name=bj
```


**提示:** 传入`copy_machine_group`为`true`可以复制机器组的配置以及Logtail配置的管理信息. 


