# coding=utf8
"""cli.py

Command Line Interface (CLI)
"""
from __future__ import absolute_import, print_function, unicode_literals

import errno
import logging
import os
import sys

from .__version__ import __description__, __title__, __version__
from .log import LOGGING_FILENAME, LOGGING_LEVEL

__all__ = (
    "arg_parser",
    "main",
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
  import msvcrt  # noqa

  msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
  msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
  msvcrt.setmode(sys.stderr.fileno(), os.O_BINARY)

_DEFAULT_FILE_WRITE_MODE = 'wb' if _IS_PY2 else "w"


def epipe(func):
  """Decorator to Handle EPIPE Errors.

  Raises:
    IOError: Raised when non-EPIPE exceptions are encountered.
  """

  def _f(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except IOError as e:
      if e.errno == errno.EPIPE:
        sys.exit(e.errno)
      raise

  return _f


def arg_parser(**kwargs):
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
      help='Output Location (default: %(default)s)',
      type=FileType("{0!s}+".format(_DEFAULT_FILE_WRITE_MODE))
  )

  parser.add_argument(
      '--logfile',
      help='Log to File. (default: %(default)s)',
      metavar='FILE',
      default=LOGGING_FILENAME
  )

  return parser


@epipe
def main():
  """Module CLI Entry Point
  """
  # parse cli arguments
  parser = arg_parser()
  options = parser.parse_args()

  # setup logging
  logfile = options.logfile
  log_level = logging.DEBUG if options.debug else LOGGING_LEVEL
  logging.basicConfig(filename=logfile, level=log_level)
  LOGGER.debug("New Logger: level=%s logfile=%s", log_level, logfile)

  # run
  LOGGER.warning("command line interface not implemented")
  if os.isatty(options.output):
    options.output.write("\n")

  # return exit code
  return 0
