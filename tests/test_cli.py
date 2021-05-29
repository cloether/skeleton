# coding=utf8
"""test_cli.py

Command Line Interface (cli) Tests.
"""
from __future__ import absolute_import, print_function, unicode_literals

import logging
import sys
from argparse import ArgumentParser

from skeleton.cli import argparser
from .utils import run

LOGGER = logging.getLogger(__name__)

__all__ = (
    "test_arg_parser",
    "test_main"
)


def test_arg_parser():
  """Test cli.py argparser.
  """
  parser = argparser()
  is_argparser = isinstance(parser, ArgumentParser) is True
  assert is_argparser, "Invalid argparser type: {0}".format(type(parser))
  return is_argparser


def test_main(module_name):
  """Test Command Line Interface (cli).

  Returns:
    bool: True if success, otherwise False.
  """
  command = "{0!s} -m {1!s}".format(sys.executable, module_name)
  LOGGER.debug("test_cli command: %s", command)
  ret = None
  try:
    ret = run(command)
    LOGGER.debug("return code: %s", ret)
  except NotImplementedError:
    success = False
  except Exception as e:
    LOGGER.exception(
        "cli command execution: status=failed command=%s error=%r",
        command, e
    )
    success = False
  else:
    success = True if ret == 0 else False
    LOGGER.debug(
        "cli command execution: status=%s command=%s error=%r",
        success, command, None
    )
  assert success is True, "CLI Test Failed with return_code: {0}".format(ret)
  return success
