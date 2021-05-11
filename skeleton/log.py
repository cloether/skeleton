# coding=utf8
"""log.py

Logging Utilities.
"""
from __future__ import absolute_import, print_function, unicode_literals

import json
import logging
import re
import types
from functools import partial
from logging import _checkLevel as check_level  # noqa
from os import getenv

from six import ensure_str, iteritems, string_types, text_type

from .utils import as_number

__all__ = (
    "log_level",
    "log_request",
    "log_response",
    "log_request_response",
    "apply_session_hook"
)

LOGGER = logging.getLogger(__name__)

_CONTENT_DISPOSITION_RE = re.compile(r"attachment;\s?filename=[\"\w.]+", re.I)
_LOGGING_JSON_SORT_KEYS = 1
_LOGGING_JSON_INDENT = 1


# public functions

def _getenv(name, default=None):
  value = getenv(name, default)
  if not value or value is None:
    return value
  if not isinstance(value, string_types):
    return value
  value = value.strip()
  if value.isdecimal():
    value = int(float(value))
  elif value.isdigit():
    value = int(value)
  elif value.lower() == ("true", "1"):
    value = True
  elif value.lower() == ("false", "0"):
    value = False
  return value


def _log_items(data, name, ignore_empty=True, prefix=" - "):
  if not (ignore_empty and not data):
    LOGGER.debug("%s%s:", prefix, name.upper())
    for key, value in iteritems(data):
      LOGGER.debug("   -  %s: %s", key, value)


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
    _indent = _getenv("_LOGGING_JSON_INDENT", _LOGGING_JSON_INDENT)
    _sort_keys = _getenv("LOGGING_JSON_SORT_KEYS", _LOGGING_JSON_SORT_KEYS)
    _lines = json.dumps(data, indent=_indent, sort_keys=_sort_keys).splitlines()
    _log_list(_lines, name, prefix=prefix, ignore_empty=ignore_empty)


# pylint: disable=too-many-return-statements
def _response_content_str(response, **kwargs):
  """Get Response Content String

  Args:
    response (requests.models.Response): Response Object.

  Returns:
    str: Content type string
  """
  response_headers = response.headers
  if "content-disposition" not in response_headers:
    return None

  if kwargs.get("stream", False):
    return "(STREAM-DATA)"

  content_disposition = response_headers["content-disposition"]
  if content_disposition and _CONTENT_DISPOSITION_RE.match(content_disposition):
    filename = content_disposition.partition("=")[2]
    return "(FILE-ATTACHMENT: {0})".format(filename)

  content_type = response_headers.get("content-type", "")
  if not content_type:
    return None

  if content_type.endswith("octet-stream"):
    return "(BINARY-DATA)"

  if content_type.endswith("image"):
    return "(IMAGE-DATA)"

  return None


# public functions

def log_level(level):
  """Return valid integer log level

  Args:
    level (str or int): Log level

  Returns:
    int: Normalized log level.
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
    log_content (bool): Log Response Body Content if True otherwise
      the response body content will not be logged.
  """
  if not LOGGER.isEnabledFor(logging.DEBUG):
    return
  log_content = kwargs.setdefault("log_content", False)
  try:
    LOGGER.debug("REQUEST:")  # start
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
  except Exception as e:  # pylint: disable=broad-except
    LOGGER.error("FAILED to log request: %r", e)
  LOGGER.debug("--")  # end


def log_response(response, **kwargs):
  """Log HTTP Response

  Args:
    response (requests.models.Response): Response Instance.

  Keyword Args:
    log_content (bool): Log Response Body Content if True otherwise the
      response body content will not be logged.
  """
  if not LOGGER.isEnabledFor(logging.DEBUG):
    return
  log_content = kwargs.setdefault("log_content", False)
  try:
    _log_one("", "RESPONSE", ignore_empty=False, prefix="")  # start
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
  except Exception as e:  # pylint: disable=broad-except
    LOGGER.debug("FAILED to log response: %r", e)
  LOGGER.debug("--")  # end


def log_request_response(response, **kwargs):
  """Log both the request and response.
  """
  log_request(response.request, **kwargs)
  log_response(response, **kwargs)


def apply_session_hook(session, **kwargs):
  """Add a hook to a requests.Session which logs
  requests and responses.

  Args:
    session (requests.Session): Session instance.
  """
  func = partial(log_request_response, **kwargs)
  session.hooks.setdefault("response", []).append(func)


def add_stderr_logger(level=logging.INFO, fmt=None, datefmt=None, style=None):
  """Helper for quickly adding a StreamHandler to the logger.

  Args:
    level (str): Logging Level.
    fmt (str): Logging Format.
    datefmt (str): Logging Date Format.
    style (str): Logging Style.

  Returns:
    logging.Handler: the handler after adding it.
  """
  # pylint: disable=import-outside-toplevel
  from logging import StreamHandler, Formatter

  logger = logging.getLogger(__name__)
  handler = StreamHandler()
  handler.setFormatter(Formatter(fmt, datefmt=datefmt, style=style))
  logger.addHandler(handler)
  logger.setLevel(level)
  logger.debug("Added stderr logging handle to logger: %s", __name__)
  return handler
