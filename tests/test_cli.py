#!/usr/bin/env python3
# coding=utf8
"""test_cli.py

Command Line Interface (cli) Tests.
"""
from __future__ import absolute_import, print_function, unicode_literals

import logging
import sys
from subprocess import CalledProcessError, check_call

LOGGER = logging.getLogger(__name__)


def run(command):
  """Run Command.
  """
  try:
    returncode = check_call(command, shell=True)
  except CalledProcessError as e:
    returncode = e.returncode
    LOGGER.error(
        "check_call returned non-zero exit code: "
        "command=%s returncode=%s args=%s stdout=%s stderr=%s",
        e.cmd, returncode, e.args, e.stdout, e.stderr
    )
  return returncode


def test_cli():
  """Test Command Line Interface (cli).

  Returns:
    bool: True if success, otherwise False.
  """
  command = "{0!s} -m skeleton".format(sys.executable)
  LOGGER.debug("command: %s", command)
  # noinspection PyBroadException
  try:
    return_code = run(command)
    LOGGER.debug("return code: %s", return_code)
  except NotImplementedError:
    return False
  except Exception as e:
    LOGGER.exception(
        "cli command execution: status=failed command=%s error=%r",
        command, e
    )
    return False
  else:
    success = True if return_code == 0 else False
    LOGGER.exception(
        "cli command execution: status=%s command=%s error=%r",
        success, command, None
    )
    return success
