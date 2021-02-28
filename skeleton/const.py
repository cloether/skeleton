# coding=utf8
"""const.py
"""
from __future__ import absolute_import, print_function, unicode_literals

import logging
import sys
from datetime import datetime

# DATETIME CONSTANTS

EPOCH = datetime(1970, 1, 1)
ISO_DATETIME_STRING = "1970-01-01 00:00:00.000"
ISO_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

# CONNECTION DEFAULTS

DEFAULT_MAX_POOL_CONNECTIONS = 10
DEFAULT_RETRIES = 0
DEFAULT_POOL_TIMEOUT = None
DEFAULT_POOLBLOCK = False
DEFAULT_POOLSIZE = 10
DEFAULT_TIMEOUT = 60

# FILE DEFAULTS

DEFAULT_CHUNK_SIZE = 64 * 2**10
DEFAULT_FILE_MODE_SUFFIX = "b" if sys.version_info[0] == 2 else ""
DEFAULT_FILE_WRITE_MODE = "w{0}".format(DEFAULT_FILE_MODE_SUFFIX)
DEFAULT_FILE_READ_MODE = "r{0}".format(DEFAULT_FILE_MODE_SUFFIX)

# LOGGING DEFAULTS

DEFAULT_LOGGER_NAME = ""

# LOGGING OPTIONS

LOGGING_DATEFMT = "%Y-%m-%d %H:%M:%S"
LOGGING_FILEMODE = "a+"
LOGGING_FILENAME = None
LOGGING_FORMAT = (
    "(%(asctime)s)[%(levelname)s]%(name)s.%(funcName)s(%(lineno)d):%(message)s"
)
LOGGING_LEVEL = "ERROR"
LOGGING_STYLE = "%"
LOGGING_LEVELS = {
    logging.NOTSET: "sample",
    logging.DEBUG: "debug",
    logging.INFO: "info",
    logging.WARNING: "warning",
    logging.ERROR: "error",
    logging.FATAL: "fatal",
}  # type: dict[int,str]
LOGGING_LEVELS_MAP = {LOGGING_LEVELS[level]: level for level in LOGGING_LEVELS}
