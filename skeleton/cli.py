#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""cli.py

Command Line Interface.
"""
from __future__ import unicode_literals, print_function, absolute_import

import logging
import os
import signal
import sys

from six import text_type

from .__version__ import __description__, __name__, __version__
from .log import (
  LOGGING_DATEFMT,
  LOGGING_FILENAME,
  LOGGING_FORMAT,
  LOGGING_LEVEL
)

LOGGER = logging.getLogger(__name__)

_IS_PY2 = sys.version_info[0]
_IS_WIN32 = sys.platform == "Win32"

if _IS_WIN32:
  # Binary mode is required for persistent mode on windows.
  # sys.stdout in Python is by default opened in text mode,
  # and writes to this stdout produce corrupted binary data
  # on Windows.
  #
  #   python -c "import sys; sys.stdout.write('_\n_')" > file
  #   python -c "print(repr(open('file', 'rb').read()))"

  # noinspection PyUnresolvedReferences
  import msvcrt

  # noinspection PyUnresolvedReferences
  msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
  # noinspection PyUnresolvedReferences
  msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
  # noinspection PyUnresolvedReferences
  msvcrt.setmode(sys.stderr.fileno(), os.O_BINARY)

_DEFAULT_FILE_WRITE_MODE = 'wb' if _IS_PY2 else "w"


def _handle_teardown_signals(callback):
  """Register handler for SIGTERM/SIGINT/SIGBREAK signal.

  Catch SIGTERM/SIGINT/SIGBREAK signals, and invoke callback

  Notes:
    this should be called in main thread since Python only
    catches signals in main thread.

  Args:
    callback (function): Callback for tear down signals.
  """
  signal.signal(signal.SIGTERM, callback)
  signal.signal(signal.SIGINT, callback)
  if os.name == 'nt':
    signal.signal(signal.SIGBREAK, callback)


def _shutdown_handler(signum, _):
  """Handle Shutdown
  """
  LOGGER.debug("signal received: %d", signum)
  sys.exit(0)


def _arg_parser(**kwargs):
  """Build Argument Parser

  Keyword Args:
    prog (str): Program Name
    usage (str): Program Usage
    description (str): Program Description
    formatter_class (argparse.HelpFormatter): Help Formatter

  Returns:
    (argparse.ArgumentParser): ArgumentParser Instance
  """
  from argparse import (
    ArgumentDefaultsHelpFormatter,
    ArgumentParser,
    FileType,
    SUPPRESS
  )

  parser = ArgumentParser(**kwargs)
  parser.set_defaults(
      argument_default=SUPPRESS,
      conflict_handler="resolve",
      description=__description__,
      formatter_class=ArgumentDefaultsHelpFormatter,
      prog=__name__,
      usage=__doc__
  )
  parser.add_argument(
      "-d", "--debug",
      action="store_true",
      help="Enable DEBUG logging"
  )
  parser.add_argument(
      "-v", "--version",
      action="version",
      version=__version__
  )
  parser.add_argument(
      '-o', '--output',
      default="-",
      dest='output',
      help='Program output file or buffer.',
      metavar='OUT',
      type=FileType(_DEFAULT_FILE_WRITE_MODE)
  )
  parser.add_argument(
      '--log-datefmt',
      dest='log_datefmt',
      type=text_type,
      help='Log Date Format. (default: %(default)s)',
      metavar='LOG_DATEFMT',
      default=LOGGING_DATEFMT
  )
  parser.add_argument(
      '--log-file',
      dest='log_file',
      type=text_type,
      help='Log File. (default: %(default)s)',
      metavar='LOG_FILE',
      default=LOGGING_FILENAME
  )
  parser.add_argument(
      '--log-format',
      dest='log_format',
      type=text_type,
      help='Log Format. (default: %(default)s)',
      metavar='LOG_FORMAT',
      default=LOGGING_FORMAT
  )
  parser.add_argument(
      '--log-level',
      dest='log_level',
      type=text_type,
      help='log level',
      metavar='LOG_LEVEL',
      default=LOGGING_LEVEL
  )
  return parser


def main():
  """Module CLI Entry Point
  """
  _handle_teardown_signals(_shutdown_handler)
  _parser = _arg_parser()
  _options = vars(_parser.parse_args())
  _logging_format = _options.get("log_format", LOGGING_FORMAT)
  _logging_datefmt = _options.get("log_datefmt", LOGGING_DATEFMT)
  _logging_filename = _options.get("log_filename", LOGGING_FILENAME)
  _logging_level = _options.get("log_level", LOGGING_LEVEL)
  logging.basicConfig(
      format=_logging_format,
      filename=_logging_filename,
      level=_logging_level,
      datefmt=_logging_datefmt
  )
  LOGGER.setLevel(_logging_level)
  _logging_stream_handler = logging.StreamHandler()
  _logging_stream_handler.setFormatter(
      logging.Formatter(_logging_format, datefmt=_logging_datefmt)
  )
  LOGGER.addHandler(_logging_stream_handler)
  LOGGER.debug("Created logger: %s" % LOGGER)
  LOGGER.error("%s command line interface not implemented." % __name__)
  return 0
