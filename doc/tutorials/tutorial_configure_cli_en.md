# Configure CLI

## Introduction

There're ceratin options need to configure to make it more convenient to use CLI.

### CLI options

CLI options include:

- [Access Key and Endpoint](#configure-ak-and-endpoint)
    - About the definition of access key and endpoint，Refer to [here](https://www.alibabacloud.com/help/doc-detail/29064.htm)
- [Multiple account](#multiple-account)
    - Configure multiple accounts for operation in specific region, cross region or testing purpose.
- [Output format](#format-output)
    - format the json output.

## Configure AK and Endpoint

There're three ways to configure the access key and endpoint and they're prioritized as below:


- Parameters

```shell
> aliyunlog log create_project ..... --access-id=<value> --access-key=<value> --region-endpoint=<value> --sts-token=<value>
```

  **Note:** Any sub command support such way to overwrite the AK setings in later ways (env or config file) for the specific operations.
  **Note:** sts-token is used in STS mode

- Environment Variables

  - ALIYUN_LOG_CLI_ACCESSID
  - ALIYUN_LOG_CLI_ACCESSKEY
  - ALIYUN_LOG_CLI_ENDPOINT
  - ALIYUN_LOG_CLI_STS_TOKEN

- Local configuration file

  You could store them at `~/.aliyunlogcli`, the default section name is `main`

```ini
[main]
access-id=
access-key=
region-endpoint=
sts-token=
```

### Enable Https Connection

When configuring endpoint with prefix `https://`, the connection between CLI and Log service will be secured. Or else, it will use http by default. 


### Modify the configuration file

Use the command "configure" to modify the configuration file: 

```shell
> aliyunlog configure access_id access_key cn-beijing.log.aliyuncs.com
> aliyunlog configure access_id access_key cn-beijing.log.aliyuncs.com main sts_token

```


## Multiple Account

1. Store multiple accounts for some use cases (e.g. test, multiple region operations)

```shell
> aliyunlog configure access_id1 access_key1 cn-beijing.log.aliyuncs.com
> aliyunlog configure access_id2 access_key2 cn-hangzhou.log.aliyuncs.com test
```

  AK is stored as:

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

Refer to [here](https://aliyun-log-cli.readthedocs.io/en/latest/tutorials/tutorial_configure_accounts_in_file_cn.html) to know a simpler way to configure multiple accounts in config file.


2. Use specific account

Any subcommand could use global opton `--client-name=<value>` to use specific configured account. e.g:
```shell
> aliyunlog log create_project ..... --client-name=test
```
It will use `test` to create the project.

3. Other Case

In some case, we need to operate cross regions, e.g.

```shell
> aliyunlog log copy_project --from_project="p1" --to_project="p1" --to_client=test
```

It will use account `main` to copy project `p1` in its region to another region under account `test`


### Default account

As mentions previously, the name of default account is `main`, in specific case, it's necessary to swith to another account (in different region). This could be archvied by using option `--default-client`:

```shell
aliyunlog configure --default-client=beijing
```

This command will switch default account to the one `beijing`.


## Format output

**JSON Format**

Output is in json format normally, which is printed in one line in console. In some cases, it's useful to show them in pretty format. You could use option `--format-output=json` in each command for this:
```shell
aliyunlog log get_log....  --format-output=json
```

But if you want to make it a default behavior, configure it directly: 

```shell
aliyunlog log configure --format-output=json
```

**Not escape Non-ANSI**

By default, for non-ANSI characters, it will escape it. If you want to view the raw string, you could add a `no_escape` to format of output:
```shell
aliyunlog log get_log....  --format-output=json,no_escape
```
It could be `no_escape` or combine with other value in `format-output` with `,`

And if you want to make it a default behavior, configure it directly:

```shell
aliyunlog log configure --format-output=json,no_escape
```

