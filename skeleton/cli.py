# coding=utf8
"""cli.py

Command Line Interface (CLI)
"""
from __future__ import absolute_import, print_function, unicode_literals

import logging
import os

from .__version__ import __description__, __title__, __version__
from .const import (
  DEFAULT_FILE_READ_MODE,
  DEFAULT_FILE_WRITE_MODE,
  LOGGING_DATEFMT,
  LOGGING_FILENAME,
  LOGGING_FORMAT,
  LOGGING_LEVEL
)

__all__ = ("argparser", "main")

LOGGER = logging.getLogger(__name__)


# TODO: create argparser from configuration file/dict
def argparser(**kwargs):
  """Build Argument Parser

  Keyword Args:
    prog (str): Name of the program (default: sys.argv[0]).
    usage (str): Usage message (default: auto-generated from
      arguments).
    description (str): Description of what the program does.
    epilog (str): Text following the argument descriptions.
    formatter_class (argparse.HelpFormatter): HelpFormatter class
      for printing help messages.
    prefix_chars (list of str or str): Characters that prefix
      optional arguments.
    fromfile_prefix_chars (list of str or str): Characters that
      prefix files containing additional arguments.
    argument_default: Default value for all arguments.
    add_help (bool): Add a -h/-help option.
    conflict_handler (str): String indicating how to handle conflicts.
    parents (list of argparse.ArgumentParser): Parsers whose arguments
      should be copied into this one.
    allow_abbrev (bool): Allow long options to be abbreviated
      unambiguously.
    exit_on_error (bool): Determines whether ArgumentParser
      exits with error info when an error occurs.

  Returns:
    (argparse.ArgumentParser): ArgumentParser Instance.
  """
  # pylint: disable=import-outside-toplevel
  from argparse import (
    ArgumentDefaultsHelpFormatter,
    ArgumentParser,
    FileType,
    SUPPRESS
  )

  LOGGER.debug("creating argument parser: kwargs=%s", kwargs)

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
      "-V", "--version",
      action="version",
      version=__version__
  )
  parser.add_argument(
      "-d", "--debug",
      "-v", "--verbose",
      action="store_true",
      help="enable verbose logging"
  )
  parser.add_argument(
      "-i", "--input",
      default="-",
      metavar="path",
      help="input location (default: %(default)s)",
      type=FileType("{0!s}+".format(DEFAULT_FILE_READ_MODE))
  )
  parser.add_argument(
      "-o", "--output",
      default="-",
      metavar="path",
      help="output location (default: %(default)s)",
      type=FileType("{0!s}+".format(DEFAULT_FILE_WRITE_MODE))
  )
  parser.add_argument(
      "--logfile",
      help="log to file. (default: %(default)s)",
      metavar="FILE",
      default=LOGGING_FILENAME
  )
  return parser


def main(*args, **kwargs):
  """Module CLI Entry Point.

  Notes:
    args are passed into the function `ArgumentParser.parse_args`
    kwargs are passed to the function `argparser`

  Returns:
    int: returns 0 if successful otherwise any other integer.
  """
  # create argument parser
  parser = argparser(**kwargs)

  # parse cli arguments
  args = parser.parse_args(*args)

  # setup logging
  logging.basicConfig(
      filename=args.logfile,
      level=logging.DEBUG if args.debug else LOGGING_LEVEL,
      format=LOGGING_FORMAT,
      datefmt=LOGGING_DATEFMT
  )

  LOGGER.warning("command line interface not yet implemented.")

  # write newline and flush when output is connected to a terminal
  if os.isatty(args.output.fileno()):
    args.output.write(os.linesep)
    args.output.flush()
  return 0
