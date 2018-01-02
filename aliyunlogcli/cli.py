from __future__ import print_function
from aliyunlogcli.config import load_debug_from_config_file
import logging
import sys

logging_opt = load_debug_from_config_file()

try:
    logging.basicConfig(**logging_opt)
except Exception as ex:
    print("**fail to init logging module: ", ex, file=sys.stderr)

from aliyunlogcli.cli_core import main
if __name__ == '__main__':
    main()

