from aliyunlogcli.config import config_logging_from_config_file
config_logging_from_config_file()

import logging
logger = logging.getLogger(__name__)

logger.info("SLS CLI is started.")

from aliyunlogcli.cli_core import main
if __name__ == '__main__':
    main()

