from aliyunlogcli.cli_core import _parse_cmd_pattern_param, parse_method_types_optdoc_from_class
from aliyun.log import LogException, LogClient
 
 
def test_cmd_format():
    method_types, method_param_usage, optdoc, usage = parse_method_types_optdoc_from_class(LogClient)
    cmds = []
    for line in optdoc.split('\n'):
        line = line.strip()
        if line.startswith('aliyunlog log '):
            cmds.append(line)
    assert len(cmds) > 10, cmds
    
    for cmd in cmds:
        required, optional = _parse_cmd_pattern_param(cmd)
        assert len(required) + len(optional) > 0, _parse_cmd_pattern_param(cmd)
        args = cmd.split(' ')
        assert len(args) == len(required) + len(optional) + 3