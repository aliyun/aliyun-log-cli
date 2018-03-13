# 配置CLI

## 介绍
和大多数CLI一样，CLI安装好后，需要适当配置一下才可以高效方便的使用。

## 有哪些CLI的配置项

CLI的配置项目包含如下内容:

- [服务入口和访问秘钥](#配置秘钥与服务入口)
    - 关于服务入口和访问秘钥的定义，可以参考[这里](https://help.aliyun.com/document_detail/29064.html)
- [多账户与默认账户](#多账户)
    - 配置多个账户，以便访问特定区域，用于测试或者跨域操作等。
- [输出格式](#输出格式)
    - 修改输出json的格式化方式，默认是在一行打印。


<h2 id="配置秘钥与服务入口">配置秘钥与服务入口</h2>

日志服务CLI支持通过以下三种方式配置访问秘钥与入口，如果同时配置多种方式, 优先顺序是: 参数, 环境变量, 最后是本地配置文件. 

- 参数

```shell
> aliyunlog log create_project ..... --access-id=<value> --access-key=<value> --region-endpoint=<value>
```

  **注意:** 任意log子命令都支持以上方式定义特定的AK与Endpoint(覆盖后面的方式)


- 环境变量

  - ALIYUN_LOG_CLI_ACCESSID
  - ALIYUN_LOG_CLI_ACCESSKEY
  - ALIYUN_LOG_CLI_ENDPOINT

- 本地配置文件

  将存储AK与Endpoint在~/.aliyunlogcli, 默认使用的块名是`main`

```ini
[main]
access-id=
access-key=
region-endpoint=
```

<h2 id="使用HTTPS连接">使用HTTPS连接</h2>

当给服务入口地址加上`https://`前缀时, CLI会使用`https`连接, 否则默认使用`https`. 


<h2 id="修改配置文件">修改配置文件</h2>

Configure命令可以修改配置文件内容.

```shell
> aliyunlog configure access_id access_key cn-beijing.log.aliyuncs.com
```

<h1 id="多账户">多账户</h1>

### 存储于多个账户

CLI支持以便在特定情况下使用(例如不同域操作、测试等):

```shell
> aliyunlog configure access_id1 access_key1 cn-beijing.log.aliyuncs.com
> aliyunlog configure access_id2 access_key2 cn-hangzhou.log.aliyuncs.com test
```

  AK将存储为:

```ini
[main]
access-id=access_id1
access-key=access_key1
region-endpoint=cn-beijing.log.aliyuncs.com

[test]
access-id=access_id2
access-key=access_key2
region-endpoint=cn-hangzhou.log.aliyuncs.com
```

### 使用特定账户

任意命令都可以通过选项`--client-name=<value>`来使用特定配置的账户, 例如:

```shell
> aliyunlog log create_project ..... --client-name=test
```

将使用`test`的AK来进行操作.

### 其他情况

某些情况下也需要跨账户操作, 例如:

```shell
> aliyunlog log copy_project --from_project="p1" --to_project="p1" --to_client=test
```

将`main`账户下对应的项目`p1`复制到账户`test`下的`p1`

### 默认账户

如前面所属，默认账户是`main`，在多用户情况下，切换默认账户也是很有用。通过选项`--default-client`可以修改。

```shell
aliyunlog configure --default-client=beijing
```

这样其他命令默认会使用`beijing`账户下的访问密码和服务入口地址。

<h1 id="输出格式">输出格式</h1>

输出格式一般是以json形式输出，并且是打印在一行上面，某些情况下需要格式化输出方便查看，可以在特定命令上配置`--format-output=json`，这样CLI会将输出进行格式化。
```shell
aliyunlog log get_log....  --format-output=json
```

如果期望所有输出都是这样，可以修改配置项来完成：

```shell
aliyun log configure --format-output=json
```
