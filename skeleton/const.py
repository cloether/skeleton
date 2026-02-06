# coding=utf8
"""const.py

Module Constants.
"""
from __future__ import absolute_import, print_function, unicode_literals

import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional

from .__version__ import __title__

# DATETIME CONSTANTS
EPOCH: datetime = datetime(1970, 1, 1)
ISO_DATETIME_STRING: str = "1970-01-01 00:00:00.000"
ISO_DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S.%f"

# CONNECTION DEFAULTS
DEFAULT_MAX_POOL_CONNECTIONS: int = 10
DEFAULT_RETRIES: int = 0
DEFAULT_POOL_TIMEOUT: Optional[int] = None
DEFAULT_POOLBLOCK: bool = False
DEFAULT_POOLSIZE: int = 10
DEFAULT_TIMEOUT: int = 60

# FILE DEFAULTS
DEFAULT_CHUNK_SIZE: int = 64 * 2 ** 10
DEFAULT_FILE_MODE_SUFFIX: str = "b" if sys.version_info[0] == 2 else ""
DEFAULT_FILE_WRITE_MODE: str = "w{0}".format(DEFAULT_FILE_MODE_SUFFIX)
DEFAULT_FILE_READ_MODE: str = "r{0}".format(DEFAULT_FILE_MODE_SUFFIX)

# LOGGING DEFAULTS
DEFAULT_LOGGER_NAME: str = __title__

# LOGGING OPTIONS
LOGGING_DATEFMT: str = "%Y-%m-%d %H:%M:%S"
LOGGING_FILEMODE: str = "a+"
LOGGING_FILENAME: Optional[str] = None
LOGGING_FORMAT: str = (
  "(%(asctime)s) [%(levelname)s] "
  "%(name)s.%(funcName)s(%(lineno)d): %(message)s"
)
LOGGING_LEVEL: int = logging.ERROR
LOGGING_STYLE: str = "%"

LOGGING_LEVELS: Dict[int, str] = {
  logging.NOTSET: "sample",
  logging.DEBUG: "debug",
  logging.INFO: "info",
  logging.WARNING: "warning",
  logging.ERROR: "error",
  logging.FATAL: "fatal",
}

LOGGING_LEVELS_MAP: Dict[str, int] = {
  LOGGING_LEVELS[lvl]: lvl
  for lvl in LOGGING_LEVELS
}

LOGGING_DICT: Dict[str, Any] = {
  "version": 1,
  "disable_existing_loggers": False,
  "formatters": {
    "standard": {
      "format": LOGGING_FORMAT,
      "style": LOGGING_STYLE,
      "datefmt": LOGGING_DATEFMT
    }
  },
  "handlers": {
    "console": {
      "level": "INFO",
      "class": "logging.StreamHandler",
      "formatter": "standard",
    },
    "file": {
      "class": "logging.FileHandler",
      "level": "INFO",
      "formatter": "standard",
      "filename": "{0}.log".format(DEFAULT_LOGGER_NAME),
      "mode": LOGGING_FILEMODE,
    },
  },
  "loggers": {
    DEFAULT_LOGGER_NAME: {
      "handlers": ["console"],
      "level": "INFO",
      "propagate": False
    }
  }
}
