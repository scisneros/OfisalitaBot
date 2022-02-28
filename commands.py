import os
from datetime import datetime
from enum import Enum
from typing import Text

import data
from config.logger import log_command
from config.logger import logger
from telegram import Update
from telegram.ext import CallbackContext
from utils import generate_acronym, get_arg, reverse_acronym, try_msg
from utils import generate_acronym, get_arg, try_msg


class Commands(str, Enum):
    """This enumeration represents all the commands accepted by the bot."""
    TUP = "tup"
    START = "start"
    DESIGLAR = "desiglar"
    SIGLAR = "siglar"
    SLASHEAR = "slashear"
    UWUSPEECH = "uwuspeech"
    GET_LOG = "get_log"
