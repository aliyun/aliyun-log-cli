
import subprocess



def run_cmd(cmd):
    process = subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    process.wait()
    return_code = process.returncode
    return out.decode(), err.decode(), return_code

def test_unknown_command():
    out, err, code = run_cmd('aliyunlog invalid')
    assert code != 0
    first_line_error = out.split('\n')[0]
    assert 'unknown command' in first_line_error.lower(), first_line_error
    
def test_missing_log_subcommand():
    out, err, code = run_cmd('aliyunlog log ')
    first_line_error = out.split('\n')[0]
    assert code != 0
    assert 'missing aliyunlog log subcommand' in first_line_error.lower(), first_line_error

def test_unknown_log_subcommand():
    out, err, code = run_cmd('aliyunlog log _invalid_subcommand')
    first_line_error = out.split('\n')[0]
    assert code != 0
    assert 'unknown aliyunlog log subcommand' in first_line_error.lower(), first_line_error
    assert '_invalid_subcommand' in first_line_error.lower(), first_line_error
    
def test_missing_log_param():
    out, err, code = run_cmd('aliyunlog log get_project')
    first_line_error = out.split('\n')[0]
    assert code != 0
    assert 'missing required parameter' in first_line_error.lower(), first_line_error
    assert 'project_name' in first_line_error.lower(), first_line_error
    
    out, err, code = run_cmd('aliyunlog log get_logstore --project_name=test --access_id=xxx')
    first_line_error = out.split('\n')[0]
    assert code != 0
    assert 'missing required parameter' in first_line_error.lower(), first_line_error
    assert 'logstore_name' in first_line_error.lower(), first_line_error

    out, err, code = run_cmd(r'aliyunlog log get_log_all --project="xxxx" --logstore="yyyy" --query="" --to_time="2024-08-06 19:15:57+08:00" --region-endpoint="http://cn-hangzhou.log.aliyuncs.com" --format-output=no_escape  --access-id="xxxxxx" --access-key="xxxxxxxx"')
    first_line_error = out.split('\n')[0]
    assert code != 0
    assert 'missing required parameter' in first_line_error.lower(), first_line_error
    assert 'from_time' in first_line_error.lower(), first_line_error
    
def test_unknown_log_param():
    out, err, code = run_cmd('aliyunlog log get_project --project_name=aaa --project_id=123')
    first_line_error = out.split('\n')[0]
    assert code != 0
    assert 'unknown parameter' in first_line_error.lower(), first_line_error
    assert 'project_id' in first_line_error.lower(), first_line_error