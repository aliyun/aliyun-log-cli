import json
import re

try:
    from collections import OrderedDict
except ImportError:
    # for py2.6 case
    from ordereddict import OrderedDict
from random import randint
import subprocess
from subprocess import CalledProcessError, STDOUT

try:
    from subprocess import check_output
except ImportError:
    # for py2.6 case
    def check_output(*popenargs, **kwargs):
        if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, it will be overridden.')
        process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            ex = subprocess.CalledProcessError(retcode, cmd)
            ex.output = output
            raise ex
        return output

from time import time
import sys
import os


def run_cmd(cmd):
    print(cmd)
    try:
        output = check_output(
            cmd, stderr=STDOUT, shell=True, universal_newlines=True)
        print(output)
        return output, 0
    except CalledProcessError as exc:
        print("Status : FAIL", exc.returncode)
        print(exc.output)
        return exc.output, exc.returncode


def _generate_json(s):
    p = r"""(\w+)(?:\s*=\s*['"]?\w+['"])?,"""
    d = {}
    for k in (re.findall(p, s)):
        d[k] = k
    return str(json.dumps(d)).replace('"', r'\"')


TOKEN_LIST = {
    "${RANDOM_NUMBER}": randint(1, 1000000),
    "${TIME-ONE-HOUR-AGO}": int(time() - 3600),
    "${TIME-NOW}": int(time()),
}


def process_token(txt):
    for token, value in TOKEN_LIST.items():
        txt = txt.replace(token, str(value))

    return txt


def run_test(cmd_file):
    cli_path = os.path.sep.join([os.path.dirname(__file__), '../aliyunlogcli/cli.py'])
    cli = sys.executable + ' "' + cli_path + '"'
    cmd_list = process_token(open(cmd_file).read()).split('\n')
    cmd_dict = OrderedDict()
    pre_cmd = ''
    for i, cmd in enumerate(cmd_list):
        cmd = cmd.strip()
        if not cmd or cmd.startswith('#'):
            continue

        if cmd.startswith('>'):
            cmd_dict[pre_cmd].append(cmd[1:].strip())
        else:
            cmd_dict[cmd] = cmd_dict.get(cmd, [])
            pre_cmd = cmd

    for cmd, check_items in cmd_dict.items():
        if cmd.startswith("aliyun "):
            cmd = cli + " " + cmd[len("aliyun "):]

        output, return_code = run_cmd(cmd)
        for check_item in check_items:
            assert check_item in output, ValueError('check item "{0}" is not in output "{1}"'
                                                    .format(check_item, output))

        if not check_items:
            # no check, need to ensure return code is 0
            assert return_code == 0, ValueError('cmd return code "{0}" is as expected "0"'.format(return_code))
