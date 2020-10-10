# coding=utf8
"""log.py

Logging Utilities
"""
from __future__ import absolute_import, print_function, unicode_literals

import json
import logging
import re
import types
from logging import _checkLevel as check_level  # noqa
from os import getenv

from six import ensure_str, iteritems, string_types, text_type

__all__ = (
    "LOGGING_DATEFMT",
    "LOGGING_FILEMODE",
    "LOGGING_FILENAME",
    "LOGGING_FORMAT",
    "LOGGING_LEVEL",
    "LOGGING_STYLE",
    "log_level",
    "log_request",
    "log_response"
)

from skeleton.utils import as_number

LOGGER = logging.getLogger(__name__)

_CONTENT_DISPOSITION_RE = re.compile(r"attachment;\s?filename=[\"\w.]+", re.I)

# LOGGING OPTIONS
LOGGING_DATEFMT = "%Y-%m-%d %H:%M:%S"
LOGGING_FILEMODE = "a+"
LOGGING_FILENAME = None
LOGGING_FORMAT = (
    "%(asctime)s:[%(levelname)s]:%(name)s:%(funcName)s(%(lineno)d):%(message)s"
)
LOGGING_LEVEL = "WARNING"
LOGGING_STYLE = "%"

_LOGGING_JSON_SORT_KEYS = 1
_LOGGING_JSON_INDENT = 1


def _getenv(name, default=None):
  value = getenv(name, default)
  if not value or value is None:
    return value
  if isinstance(value, string_types):
    value = value.strip()
    if value.isdecimal():
      value = int(float(value))
    elif value.isdigit():
      value = int(value)
    elif value.lower() == ("true", "1"):
      value = True
    elif value.lower() == ("false", "0"):
      value = False
  return bool(value)


def _getenv_json_sort_keys(default=_LOGGING_JSON_SORT_KEYS):
  return _getenv("LOGGING_JSON_SORT_KEYS", default)


def _getenv_json_indent(default=_LOGGING_JSON_INDENT):
  return _getenv("LOGGING_JSON_SORT_KEYS", default)


def log_level(level):
  """Return valid integer log level

  Args:
    level (str or int): Log level

  Returns:
    int: Log level
  """
  level = as_number(level)
  if isinstance(level, string_types):
    level = text_type(level).upper()
  return check_level(level)


def log_request(request, **kwargs):
  """Log HTTP Request

  Args:
    request (requests.PreparedRequest): PreparedRequest Instance.

  Keyword Args:
    log_content (bool): Log Response Body Content if True otherwise the
      response body content will not be logged.
  """
  log_content = kwargs.setdefault("log_content", False)
  try:
    LOGGER.debug("REQUEST:")
    LOGGER.debug(" - URL: %s", request.url)
    LOGGER.debug(" - PATH: %s", request.path_url)
    LOGGER.debug(" - METHOD: %s", request.method)
    if request.headers:
      LOGGER.debug(" - HEADERS:")
      for header, value in iteritems(request.headers):
        if header.lower() == "authorization":
          value = "*" * len(value)
        LOGGER.debug("   - %s: %s", header, value)
    if request.body is None:
      LOGGER.debug(" - BODY:")
      LOGGER.debug("   - (NO-BODY)")
    elif isinstance(request.body, types.GeneratorType):
      LOGGER.debug(" - BODY:")
      LOGGER.debug("   - (FILE-UPLOAD)")
    else:
      if not log_content:
        return
      LOGGER.debug(" - BODY:")
      LOGGER.debug("   - %s", text_type(request.body))
  except Exception as err:
    LOGGER.error("FAILED to log request: %r", err)


def log_response(response, **kwargs):
  """Log HTTP Response

  Args:
    response (requests.Response): Response Instance.

  Keyword Args:
    log_content (bool): Log Response Body Content if True otherwise the
      response body content will not be logged.
  """
  log_content = kwargs.setdefault("log_content", False)
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
    header = response.headers.get("content-disposition")
    if header and _CONTENT_DISPOSITION_RE.match(header):
      filename = header.partition("=")[2]
      LOGGER.debug(" - CONTENT:")
      LOGGER.debug("   - (FILE-ATTACHMENT: %s)", filename)
    elif response.headers.get("content-type", "").endswith("octet-stream"):
      LOGGER.debug(" - CONTENT:")
      LOGGER.debug("   - (BINARY-DATA)")
    elif response.headers.get("content-type", "").endswith("image"):
      LOGGER.debug(" - CONTENT:")
      LOGGER.debug("   - (IMAGE-DATA)")
    else:
      if kwargs.get("stream", False):
        LOGGER.debug(" - CONTENT:")
        LOGGER.debug("   - (STREAM-DATA)")
      else:
        if not log_content:
          return
        try:
          response_json = json.dumps(
              response.json(),
              indent=_getenv_json_indent(),
              sort_keys=_getenv_json_sort_keys()
          )
          LOGGER.debug(" - CONTENT:")
          for line in response_json.splitlines():
            LOGGER.debug("   - %s", line)
        except ValueError:
          # Catch ValueError to handles simplejson.JSONDecoderError which
          # inherits from ValueError.
          LOGGER.debug(" - CONTENT:")
          LOGGER.debug("   - %s", ensure_str(response.content or b'(NONE)'))
  except Exception as err:
    LOGGER.debug("FAILED to log response: %r", err)
