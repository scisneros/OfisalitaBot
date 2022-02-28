import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from root import ROOT_DIR

LOG_PATH = Path(ROOT_DIR) / 'log' / 'bot.log'

os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
LOG_PATH.touch(exist_ok=True)
# 3 MB max files, up to 2 backup files.
logging.basicConfig(format=(
    '%(asctime)s %(levelname)s - %(message)s'
    ' - [%(funcName)s:%(lineno)d]'
),
    level=logging.INFO,
    handlers=[RotatingFileHandler(LOG_PATH,
                                  mode='a',
                                  maxBytes=3 * 1024 * 1024,
                                  backupCount=2,
                                  encoding=None,
                                  delay=False),
              logging.StreamHandler()])

logger = logging.getLogger('pasoapasobot')
