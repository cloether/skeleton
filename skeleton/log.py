#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""log.py

Logging Utilities
"""
import json
import logging
import re
import types
from os import getenv

from six import iteritems

LOGGER = logging.getLogger(__name__)

# LOGGING OPTIONS
LOGGING_DATEFMT = "%Y-%m-%d %H:%M:%S"
LOGGING_FILEMODE = "a+"
LOGGING_FILENAME = None
# noinspection LongLine
LOGGING_FORMAT = "%(asctime)s:[%(levelname)s]:%(name)s:%(filename)s:%(funcName)s(%(lineno)d):%(message)s"  # noqa
LOGGING_LEVEL = "WARNING"
LOGGING_STYLE = "%"

# LOGGING ENV VARS
LOGGING_JSON_SORT_KEYS = 1
LOGGING_JSON_INDENT = 1

CONTENT_DISPOSITION_RE = re.compile(r"attachment; ?filename=[\"\w.]+", re.I)


# noinspection PyUnusedLocal
def log_request(request, *args, **kwargs):
  """Log HTTP Request
  """
  try:
    LOGGER.debug("Request:")
    LOGGER.debug(" - URL: %r", request.url)
    LOGGER.debug(" - Method: %r", request.method)
    LOGGER.debug(" - Headers:")
    for header, value in iteritems(request.headers):
      if header.lower() == "authorization":
        value = "*" * len(value)
      LOGGER.debug(" -- %r: %r", header, value)
    LOGGER.debug(" - Body:")
    if isinstance(request.body, types.GeneratorType):
      LOGGER.debug(" -- (FILE-UPLOAD)")
    else:
      LOGGER.debug(" -- %s", str(request.body))
  except Exception as err:
    LOGGER.error("Failed to log request %r", err)


# noinspection PyUnusedLocal
def log_response(response, *args, **kwargs):
  """Log HTTP Response
  """
  try:
    LOGGER.debug("Response:")
    LOGGER.debug(" - Status: %r", response.status_code)
    LOGGER.debug(" - Headers:")
    for header, value in iteritems(response.headers):
      LOGGER.debug(" --  %r: %r", header, value)
    LOGGER.debug(" - Content:")
    header = response.headers.get("content-disposition")
    if header and CONTENT_DISPOSITION_RE.match(header):
      filename = header.partition("=")[2]
      LOGGER.debug(" -- (FILE-ATTACHMENT: %s)", filename)
    elif response.headers.get("content-type", "").endswith("octet-stream"):
      LOGGER.debug(" -- (BINARY-DATA)")
    elif response.headers.get("content-type", "").endswith("image"):
      LOGGER.debug(" -- (IMAGE-DATA)")
    else:
      if kwargs.get("stream", False):
        LOGGER.debug(" -- (STREAM-DATA)")
      else:
        LOGGER.debug(" -- %s", json.dumps(
            response.json(),
            indent=getenv("LOGGING_JSON_INDENT", LOGGING_JSON_INDENT),
            sort_keys=getenv("LOGGING_JSON_SORT_KEYS", LOGGING_JSON_SORT_KEYS)
        ))
  except Exception as err:
    LOGGER.debug("Failed to log response %r", err)
