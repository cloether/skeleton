#!/usr/bin/env python
# coding=utf8
"""install.py
"""
from __future__ import absolute_import, print_function, unicode_literals

import logging
import os
import shutil
import sys
from contextlib import contextmanager
from functools import partial
from subprocess import CalledProcessError, check_call

LOGGER = logging.getLogger(__name__)


@contextmanager
def cwd(dirname):
  """A context manager for operating in a different directory.

  Args:
    dirname (str): Directory to cd into.

  Yields:
    str: Original directory path.
  """
  orig = os.getcwd()
  os.chdir(dirname)
  try:
    yield orig
  finally:
    os.chdir(orig)


def _run(command):
  """Run Command.

  Args:
    command (str): Command to run.

  Returns:
    int: Command return code.
  """
  try:
    return_code = check_call(command, shell=True)
  except CalledProcessError as e:
    sys.stderr.write("{0!r}\n".format(e))
    return_code = e.returncode
  return return_code


def run(command, directory=None):
  """Run Command.

  Args:
    command (str): Command to run.
    directory (str): Directory to run command from.
      Defaults to current working directory.

  Returns:
    int: Command return code.
  """
  if not directory or directory is None:
    return _run(command)
  with cwd(directory):
    return_code = _run(command)
  return return_code


def run_factory(directory):
  """Create a `run` function which will always run from
  the provided directory.

  Args:
    directory (str): Directory to run commands from.

  Returns:
    callable: Run function which will run from the
      provided directory.
  """
  return partial(run, directory=directory)


def main():
  """CLI Entry Point
  """
  repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  run_in_root = run_factory(repo_root)

  # full path of the currently running python interpreter
  exe = sys.executable
  args = " ".join(sys.argv[1:])
  pip = "{0} -m pip".format(exe)

  # upgrade pip, setuptools, and wheel
  run_in_root("{0} install --upgrade pip setuptools wheel".format(pip))

  # install requirements
  run_in_root("{0} install -r requirements.txt {1}".format(pip, args))

  # install module with docs and test extras
  run_in_root("{0} install .[docs,tests] {1}".format(pip, args))

  # cleanup generated distribution
  if os.path.isdir("dist") and os.listdir("dist"):
    shutil.rmtree("dist")

  # build release
  run_in_root("{0!s} setup.py release".format(exe))

  # install module
  dist = os.path.join(repo_root, "dist")
  dist = os.path.join(dist, os.listdir(dist)[0])

  run_in_root("{0} install {1} {2}".format(pip, dist, args))
  return 0


if __name__ == "__main__":
  sys.exit(main())
