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

from six import iteritems, text_type

LOGGER = logging.getLogger(__name__)

# LOGGING OPTIONS

LOGGING_DATEFMT = "%Y-%m-%d %H:%M:%S"
LOGGING_FILEMODE = "a+"
LOGGING_FILENAME = None
LOGGING_FORMAT = (
    "%(asctime)s:"
    "[%(levelname)s]:"
    "%(name)s:"
    "%(filename)s:"
    "%(funcName)s(%(lineno)d):"
    "%(message)s"
)
LOGGING_LEVEL = "WARNING"
LOGGING_STYLE = "%"

# LOGGING ENVIRONMENT VARIABLES

LOGGING_JSON_SORT_KEYS = 1
LOGGING_JSON_INDENT = 1

# MISCELLANEOUS CONSTANTS

CONTENT_DISPOSITION_RE = re.compile(r"attachment; ?filename=[\"\w.]+", re.I)


def log_request(request, **kwargs):
  """Log HTTP Request

  Args:
    request (requests.PreparedRequest): PreparedRequest Instance
  """
  try:
    LOGGER.debug("REQUEST:")
    LOGGER.debug(" - URL: %s", request.url)
    LOGGER.debug(" - PATH: %s", request.path_url)
    LOGGER.debug(" - METHOD: %s", request.method)
    LOGGER.debug(" - HEADERS:")
    if request.headers:
      for header, value in iteritems(request.headers):
        if header.lower() == "authorization":
          value = "*" * len(value)
        LOGGER.debug("   - %s: %s", header, value)
    LOGGER.debug(" - BODY:")
    if request.body is None:
      LOGGER.debug("   - (NO-BODY)")
    elif isinstance(request.body, types.GeneratorType):
      LOGGER.debug("   - (FILE-UPLOAD)")
    else:
      LOGGER.debug("   - %s", text_type(request.body))
  except Exception as err:
    LOGGER.error("FAILED to log request: %r", err)


def log_response(response, **kwargs):
  """Log HTTP Response

  Args:
    response (requests.Response): Response Instance
  """
  try:
    LOGGER.debug("RESPONSE:")
    LOGGER.debug(" - COOKIES: %s", response.cookies)
    LOGGER.debug(" - ENCODING: %s", response.encoding)
    if response.headers:
      LOGGER.debug(" - HEADERS:")
      for header, value in iteritems(response.headers):
        LOGGER.debug("   -  %s: %s", header, value)
    LOGGER.debug(" - REASON: %s", response.reason)
    LOGGER.debug(" - STATUS CODE: %s", response.status_code)
    LOGGER.debug(" - CONTENT:")
    header = response.headers.get("content-disposition")
    if header and CONTENT_DISPOSITION_RE.match(header):
      filename = header.partition("=")[2]
      LOGGER.debug("   - (FILE-ATTACHMENT: %s)", filename)
    elif response.headers.get("content-type", "").endswith("octet-stream"):
      LOGGER.debug("   - (BINARY-DATA)")
    elif response.headers.get("content-type", "").endswith("image"):
      LOGGER.debug("   - (IMAGE-DATA)")
    else:
      if kwargs.get("stream", False):
        LOGGER.debug("   - (STREAM-DATA)")
      else:
        try:
          response_json = json.dumps(
              response.json(),
              indent=getenv("LOGGING_JSON_INDENT", LOGGING_JSON_INDENT),
              sort_keys=getenv("LOGGING_JSON_SORT_KEYS", LOGGING_JSON_SORT_KEYS)
          )
          for line in response_json.splitlines():
            LOGGER.debug("   - %s", line)
        except ValueError as e:
          # Catch ValueError, which handles simplejson.JSONDecoderError,
          # because it inherits from ValueError.
          response_json = (response.content or b'(NO-CONTENT)').decode("utf8")
          LOGGER.debug("   - %s", response_json)
  except Exception as err:
    LOGGER.debug("FAILED to log response: %r", err)
