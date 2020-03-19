#!/usr/bin/env python
# -*- coding: utf8 -*-
"""cli.py

Command Line Interface (CLI).
"""
from __future__ import absolute_import, print_function, unicode_literals

import errno
import logging
import os
import sys

from .__version__ import (
  __description__,
  __title__,
  __version__
)
from .log import LOGGING_FILENAME, LOGGING_LEVEL

_LOGGER = logging.getLogger(__name__)

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


def _shutdown_handler(signum, _):
  """Handle Shutdown.

  Args:
    signum (int): Signal Number,
    _ (types.FrameType): Interrupted Stack Frame.
  """
  sys.stderr.write("\b\b\b\b\n")
  _LOGGER.debug("Received Signal(%d)", signum)
  sys.exit(signum)


def _epipe_wrapper(func):
  def _f(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except IOError as e:
      if e.errno == errno.EPIPE:
        sys.exit(e.errno)
      raise

  return _f


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
      usage=__doc__,
      prog=__title__,
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
      metavar="path",
      help='Output Location (default: -)',
      type=FileType(_DEFAULT_FILE_WRITE_MODE + "+")
  )
  parser.add_argument(
      '--logfile',
      help='Log to File. (default: %(default)s)',
      metavar='FILE',
      default=LOGGING_FILENAME
  )
  return parser


@_epipe_wrapper
def main():
  """Module CLI Entry Point
  """
  _parser = _arg_parser()
  _options = _parser.parse_args()
  logging.basicConfig(
      filename=_options.logfile,
      level=logging.DEBUG if _options.debug else LOGGING_LEVEL
  )
  _LOGGER.debug("Created Logger: %s", _LOGGER.name)
  _LOGGER.warning("Command line interface not implemented.")
  if os.isatty(_options.output):
    _options.output.write("\n")
  return 0
