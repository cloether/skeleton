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


def _log_items(data, name, ignore_empty=True, prefix=" - "):
  if not (ignore_empty and not data):
    LOGGER.debug("%s%s:", prefix, name.upper())
    for k, v in iteritems(data):
      LOGGER.debug("   -  %s: %s", k, v)


def _log_list(data, name, ignore_empty=True, prefix=" - "):
  if not (ignore_empty and not data):
    LOGGER.debug("%s%s:", prefix, name.upper())
    for item in data:
      LOGGER.debug("   -  %s", item)


def _log_one(data, name, prefix=" - ", ignore_empty=True):
  if not (ignore_empty and not data):
    LOGGER.debug("%s%s: %s", prefix, name.upper(), data)


def _log_json(data, name, prefix=" - ", ignore_empty=True):
  if not (ignore_empty and not data):
    _log_list(json.dumps(
        data,
        indent=_getenv_json_indent(),
        sort_keys=_getenv_json_sort_keys()
    ).splitlines(), name, prefix=prefix, ignore_empty=ignore_empty)


def _response_content_str(response, **kwargs):
  """Get Response Content String

  Args:
    response (requests.models.Response): Response Object.

  Returns:
    str: Content type string
  """
  header = response.headers.get("content-disposition")
  if not header:
    return None
  if kwargs.get("stream", False):
    return "(STREAM-DATA)"
  if _CONTENT_DISPOSITION_RE.match(header):
    filename = header.partition("=")[2]
    return "(FILE-ATTACHMENT: {0})".format(filename)

  content_type = response.headers.get("content-type", "")
  if not content_type:
    return None
  if content_type.endswith("octet-stream"):
    return "(BINARY-DATA)"
  if content_type.endswith("image"):
    return "(IMAGE-DATA)"
  return None


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
    LOGGER.debug(" - METHOD: %s", request.method.upper())
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
  LOGGER.debug("--")


def log_response(response, **kwargs):
  """Log HTTP Response

  Args:
    response (requests.models.Response): Response Instance.

  Keyword Args:
    log_content (bool): Log Response Body Content if True otherwise the
      response body content will not be logged.
  """
  log_content = kwargs.setdefault("log_content", False)
  try:
    _log_one("", "RESPONSE", ignore_empty=False, prefix="")
    _log_items(response.cookies, "COOKIES")
    _log_one(response.encoding, "ENCODING")
    _log_items(response.headers, "HEADERS")
    _log_one(response.reason, "REASON")
    _log_one(response.status_code, "STATUS CODE")
    content_str = _response_content_str(response)
    if content_str:
      _log_list((content_str,), "CONTENT")
    elif log_content:
      try:
        _log_json(response.json(), "CONTENT")
      except ValueError:
        _log_list((ensure_str(response.content or b"(NONE)"),), "CONTENT")
  except Exception as err:
    LOGGER.debug("FAILED to log response: %r", err)
  LOGGER.debug("--")
