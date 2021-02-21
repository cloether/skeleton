# coding=utf8
"""utils.py
"""
from __future__ import absolute_import, print_function, unicode_literals

import logging
import os
from contextlib import contextmanager
from subprocess import CalledProcessError, check_call

from setuptools import find_packages
from six import next

LOGGER = logging.getLogger(__name__)


@contextmanager
def cwd(dirname):
  """A context manager for operating in a different directory.

  Yields:
    str: original directory location.
  """
  orig = os.getcwd()
  os.chdir(dirname)
  try:
    yield orig
  finally:
    os.chdir(orig)


def module_name(exclude=("test*", "script*", "example*"), where="."):
  """Get current module name.

  Returns:
    str or NoneType: Module name or None
  """
  return next(iter(find_packages(exclude=exclude, where=where)), None)


def run(command, location=None):
  """Run Command.

  Args:
    command (str): Command to run.
    location (str): Location to run command from.

  Returns:
    int: Return Code.
  """

  def _run(_command):
    try:
      ret = check_call(command, shell=True)

    except CalledProcessError as e:
      ret = e.returncode

      LOGGER.exception(
          "error occurred while running command: %s return_code: %s",
          _command, ret
      )
    else:
      LOGGER.debug(
          "successfully ran command: %s return_code: %s",
          _command, ret
      )
    return ret

  if location is not None:
    with cwd(location):
      return_code = _run(command)
  else:
    return_code = _run(command)
  return return_code


def run_in_root(command):
  """Run command from the module root directory.

  Args:
    command (str): Command to run.

  Returns:
    int: Command return code.
  """
  location = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  return run(command, location=location)
