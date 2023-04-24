# coding=utf8
"""log.py

Logging Utilities.
"""
from __future__ import absolute_import, print_function, unicode_literals

import json
import logging
import re
import sys
import types
from functools import partial
from logging import _checkLevel as check_level  # noqa
from logging.handlers import SysLogHandler
from os import getenv
from syslog import LOG_LOCAL7  # noqa

from six import ensure_binary, ensure_str, iteritems, string_types, text_type

from .const import LOGGING_LEVEL

__all__ = (
    "log_level",
    "log_request",
    "log_response",
    "log_request_response",
    "apply_session_hook",
    "add_stderr_logger"
)

LOGGER = logging.getLogger(__name__)

_CONTENT_DISPOSITION_PAT = r"attachment;\s?filename=[\"\w.]+"
_CONTENT_DISPOSITION_RE = re.compile(_CONTENT_DISPOSITION_PAT, re.I)

_URL_PAT = (
    r"http[s]?://"
    r"(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)

_WS_PAT = (
    r"ws[s]?://"
    r"(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)

HIDING_PATTERNS = [_URL_PAT, _WS_PAT]

_LOGGING_JSON_SORT_KEYS = 1
_LOGGING_JSON_INDENT = 1

# https://github.com/awslabs/aws-lambda-powertools-python/blob/develop/aws_lambda_powertools/logging/formatter.py
RESERVED_LOG_ATTRS = (
    "name",
    "msg",
    "args",
    "level",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    "asctime",
    "location",
    "timestamp",
)


# private

def _getenv(name, default=None):
  value = getenv(name, default)
  if not value or value is None or not isinstance(value, string_types):
    return value
  value = value.strip()
  if value.isdecimal():
    return int(float(value))
  if value.isdigit():
    return int(value)
  if value.lower() == ("true", "1", "yes", "on"):
    return True
  if value.lower() == ("false", "0", "no", "off"):
    return False
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


# public

def log_level(level):
  """Return valid log level.

  Args:
    level (str or int): Log level

  Returns:
    int: Normalized log level.
  """
  if isinstance(level, string_types):
    level = level.strip()
    if level.isnumeric() or level.isdigit():
      level = int(level)
    elif level.isdecimal():
      level = float(level)
    else:
      level = level.upper()
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


def add_syslog_handler(logger, address='localhost', port=514,
                       facility=LOG_LOCAL7, fmt=None, datefmt=None,
                       style='%', level=logging.INFO):
  """Add Syslog Handler.

  Args:
    logger (logging.Logger): Logger instance.
    address (str): Syslog address.
    port (int): Syslog port.
    facility (int): Syslog facility to log to.
    fmt (str): Logging format string.
    datefmt (str): Logging date format.
    style (str or Literal): Logging style.
    level (str or int): Logging level.

  Returns:
    SysLogHandler: Syslog handler which was added to logger.
  """
  formatter = logging.Formatter(fmt=fmt, datefmt=datefmt, style=style)
  handler = SysLogHandler(address=(address, port), facility=facility)
  handler.setLevel(level)
  handler.setFormatter(formatter)
  logger.addHandler(handler)
  return handler


def add_stderr_logger(level=logging.INFO, fmt=None, datefmt=None, style=None):
  """Helper for quickly adding a StreamHandler to the logger.

  Args:
    level (str): Logging Level.
    fmt (str): Logging Format.
    datefmt (str): Logging Date Format.
    style (str or Literal): Logging Style.

  Returns:
    logging.Handler: the handler after adding it.
  """
  logger = logging.getLogger(__name__)
  handler = logging.StreamHandler()
  handler.setFormatter(logging.Formatter(
      fmt=fmt,
      datefmt=datefmt,
      style=style
  ))
  logger.addHandler(handler)
  logger.setLevel(level)
  logger.debug("added stderr logging handle to logger: %s", logger.name)
  return handler


def init_default_logger(level=LOGGING_LEVEL, fmt=None, datefmt=None,
                        style=None):
  """Initialize the default logger.

  Args:
    level (str or int): Logging Level.
    fmt (str): Logging format string.
    datefmt (str): Logging date format.
    style (str or Literal): Logging style.

  Returns:
    StreamHandler: Handler which was attached to the logger.
  """
  handlers = []
  # formatter = HidingFormatter(base_formatter, HIDING_PATTERNS)
  formatter = logging.Formatter(fmt=fmt, datefmt=datefmt, style=style)
  stream_handler = logging.StreamHandler(sys.stderr)
  stream_handler.setFormatter(formatter)
  stream_handler.setLevel(log_level(level))
  handlers.append(stream_handler)
  logging.basicConfig(level=level, handlers=handlers)  # noqa
  return stream_handler


if sys.version_info >= (3, 6):
  # hashlib.sha3_256 was introduced in python 3.6
  #
  # References:
  #   https://docs.python.org/3/library/hashlib.html#hash-algorithms
  from hashlib import sha3_256


  class HidingFormatter:
    """Hiding Log Formatter.

    Args:
      base_formatter (logging.Formatter): Logging Formatter.
      patterns (list of str): List of hiding regex patterns.
    """

    def __init__(self, base_formatter, patterns):
      self.base_formatter = base_formatter
      self._patterns = patterns

    @classmethod
    def convert_match_to_sha3(cls, match):
      """Convert pattern match to SHA3 hash.

      Args:
        match (re.Match): Regex match.

      Returns:
        str: Hexadecimal string representation of the
          provided hashed (SHA3) match value.
      """
      value = ensure_binary(match.group(0), "utf8")
      return sha3_256(value).digest().hex()

    def format(self, record):
      """Format log record.

      Args:
        record (logging.LogRecord): Log record to format.

      Returns:
        str: Log record text.
      """
      msg = self.base_formatter.format(record)
      for pattern in self._patterns:
        pat = re.compile(pattern)
        msg = pat.sub(self.convert_match_to_sha3, msg)
      return msg

    def __getattr__(self, attr):
      return getattr(self.base_formatter, attr)


class SuppressFilter(logging.Filter):
  """Suppress Filter.
  """

  # noinspection PyMissingConstructor
  def __init__(self, logger):
    self.logger = logger

  def filter(self, record):  # noqa: A003
    """Suppress Log Records from registered logger.

    It rejects log records from registered logger
    e.g. a child logger otherwise it honours log
    propagation from any log record created by loggers
    who don't have a handler.

    Args:
      record (logging.LogRecord): Log Record.

    Returns:
      bool: True if record should be filtered, otherwise False.
    """
    logger = record.name
    return self.logger not in logger


class SyslogBOMFormatter(logging.Formatter):
  """Syslog BOM Formatter
  """

  def format(self, record):
    """Format Log Record.

    Args:
      record (logging.LogRecord): Log Record.

    Returns:
      str: Formatted Log Record.
    """
    result = super(SyslogBOMFormatter, self).format(record)
    return "ufeff{0}".format(result)
