# 在配置文件中简单配置多个账户

## 介绍
这里详细介绍一种通过配置文件，简单的配置多个账户的方式。

## 背景

在[配置CLI](https://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_configure_cli_cn.html)里介绍了详细的CLI配置方法。如果要配置多个账户，可以通过CLI的`configure`命令配置多个账户：


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

如果我们有好多个域都需要配置，并且还存在多个权限的账户（如管理员和只读权限的秘钥），那么配置就有些复杂了。


## 方案

配置文件中，可以在`DEFAULT`中集中配置多个权限的秘钥，再在其他区中引用它即可，这样可以手动编辑`~/.aliyunlogcli`来实现：

```ini
[DEFAULT]
admin_ak_id = id
admin_ak_key = key
user_ak_id = id
user_ak_key = key

[hz_admin]
access-id = %(admin_ak_id)
access-key =  %(admin_ak_key)
region-endpoint = cn-hangzhou.sls.aliyuncs.com

[hz_user]
access-id = %(user_ak_id)
access-key =  %(user_ak_key)
region-endpoint = cn-hangzhou.sls.aliyuncs.com

[bj_admin]
access-id = %(admin_ak_id)
access-key =  %(admin_ak_key)
region-endpoint = cn-beijing.sls.aliyuncs.com

[bj_user]
access-id = %(user_ak_id)
access-key =  %(user_ak_key)
region-endpoint = cn-beijing.sls.aliyuncs.com

```

## 使用

可以自由切换默认的账户, 更多参考[配置CLI](https://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_configure_cli_cn.html)
```shell
aliyunlog configure --default-client=bj_admin
```

