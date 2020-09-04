#!/usr/bin/env python3
# coding=utf8
"""install.py
"""
import os
import shutil
import sys
from contextlib import contextmanager
from functools import partial
from subprocess import CalledProcessError, check_call


@contextmanager
def cwd(dirname):
  """A context manager for operating in a different directory.
  """
  orig = os.getcwd()
  os.chdir(dirname)
  try:
    yield orig
  finally:
    os.chdir(orig)


def _run(command):
  """Run Command.
  """
  try:
    return_code = check_call(command, shell=True)
  except CalledProcessError as e:
    sys.stderr.write("{0!r}\n".format(e))
    return_code = e.returncode
  return return_code


def run(command, directory=None):
  """Run Command.
  """
  if not directory or directory is None:
    return _run(command)
  with cwd(directory):
    return_code = _run(command)
  return return_code


def run_factory(directory):
  return partial(run, directory=directory)


def main():
  """CLI Entry Point
  """
  repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  run_in_root = run_factory(repo_root)

  # full path of the currently running python interpreter
  exe = sys.executable

  # install requirements
  run_in_root("{0!s} -m pip install -r requirements.txt".format(exe))

  # install module with docs and test extras
  run_in_root("{0!s} -m pip install .[docs,tests]".format(exe))

  # cleanup generated distribution
  if os.path.isdir("dist") and os.listdir("dist"):
    shutil.rmtree("dist")

  # build release
  run_in_root("{0!s} setup.py release".format(exe))

  # install module
  dist = os.path.join(repo_root, "dist")
  dist = os.path.join(dist, os.listdir(dist)[0])

  run_in_root("{0!s} -m pip install {1!s}".format(exe, dist))
  return 0


if __name__ == '__main__':
  sys.exit(main())
