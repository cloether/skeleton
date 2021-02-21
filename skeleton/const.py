# coding=utf8
"""const.py
"""
from __future__ import absolute_import, print_function, unicode_literals

# DEFAULT OPTIONS
DEFAULT_MAX_POOL_CONNECTIONS = 10
DEFAULT_RETRIES = 0
DEFAULT_POOL_TIMEOUT = None
DEFAULT_POOLBLOCK = False
DEFAULT_POOLSIZE = 10
DEFAULT_TIMEOUT = 60

# LOGGING OPTIONS
LOGGING_DATEFMT = "%Y-%m-%d %H:%M:%S"
LOGGING_FILEMODE = "a+"
LOGGING_FILENAME = None
LOGGING_FORMAT = (
    "(%(asctime)s)[%(levelname)s]%(name)s.%(funcName)s(%(lineno)d):%(message)s"
)
LOGGING_LEVEL = "WARNING"
LOGGING_STYLE = "%"
