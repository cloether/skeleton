# coding=utf8
"""cli.py

Command Line Interface (CLI)
"""
from __future__ import absolute_import, print_function, unicode_literals

import logging
import os
import sys

from .__version__ import __description__, __title__, __version__
from .const import (
  LOGGING_DATEFMT,
  LOGGING_FILENAME,
  LOGGING_FORMAT,
  LOGGING_LEVEL
)

__all__ = ("arg_parser", "main")

LOGGER = logging.getLogger(__name__)

_DEFAULT_FILE_MODE_SUFFIX = "b" if sys.version_info[0] == 2 else ""


# TODO: Create argparser from Configuration
def arg_parser(*args, **kwargs):
  """Build Argument Parser

  Args:
    args: Existing argparse.ArgumentParser instance.

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

  parser = args[0] if args else ArgumentParser(**kwargs)
  parser.set_defaults(
      argument_default=SUPPRESS,
      conflict_handler="resolve",
      description=__description__,
      formatter_class=ArgumentDefaultsHelpFormatter,
      usage=__doc__,
      prog=__title__,
  )
  parser.add_argument(
      "-v", "--version",
      action="version",
      version=__version__
  )
  parser.add_argument(
      "-d", "--debug",
      action="store_true",
      help="enable debug logging"
  )
  parser.add_argument(
      "-i", "--input",
      default="-",
      metavar="path",
      help="input location (default: %(default)s)",
      type=FileType("r{0!s}+".format(_DEFAULT_FILE_MODE_SUFFIX))
  )
  parser.add_argument(
      "-o", "--output",
      default="-",
      metavar="path",
      help="output location (default: %(default)s)",
      type=FileType("w{0!s}+".format(_DEFAULT_FILE_MODE_SUFFIX))
  )
  parser.add_argument(
      "--logfile",
      help="log to file. (default: %(default)s)",
      metavar="FILE",
      default=LOGGING_FILENAME
  )
  return parser


def main():
  """Module CLI Entry Point.
  """
  # parse cli arguments
  parser = arg_parser()
  options = parser.parse_args()

  # setup logging
  logging.basicConfig(
      filename=options.logfile,
      level=logging.DEBUG if options.debug else LOGGING_LEVEL,
      format=LOGGING_FORMAT,
      datefmt=LOGGING_DATEFMT
  )

  # run logic
  LOGGER.warning("command line interface not yet implemented.")

  # write newline if output is connected to a terminal
  if os.isatty(options.output.fileno()):
    options.output.write(os.linesep)
    options.output.flush()

  # return exit code (0: success)
  return 0
