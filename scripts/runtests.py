#!/usr/bin/env python
# coding=utf8
"""run_tests.py

Don not run tests from the root repo dir.

We want to ensure we're importing from the installed binary package not
from the CWD.
"""
from __future__ import absolute_import, print_function, unicode_literals

import os
from contextlib import contextmanager
from subprocess import CalledProcessError, check_call

from setuptools import find_packages


def run(command):
  """Run Command.
  """
  try:
    return_code = check_call(command, shell=True)
  except CalledProcessError as e:
    sys.stderr.write("{0!r}\n".format(e))
    return_code = e.returncode
  return return_code


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


def module_name(exclude=("tests.*", "tests"), where="."):
  """Get current module name.

  Returns:
    str or NoneType: Module name or None
  """
  return next(iter(find_packages(exclude=exclude, where=where)), None)


def touch(filepath):
  """Equivalent of Unix `touch` command
  """
  if not os.path.exists(filepath):
    fh = open(filepath, 'a')
    try:
      os.utime(filepath, None)
    finally:
      fh.close()


def main():
  """CLI Entry Point
  """
  repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  module = module_name(where=repo_root)

  return_code = -1  # noqa

  with cwd(repo_root):
    env_name = os.getenv("ENVNAME", "test")

    tests_dir = os.path.join(repo_root, 'tests')
    tests_log_file = os.path.join(tests_dir, "pytest.log")

    touch(tests_log_file)  # prevent pytest errors

    tests_html_filename = "{0!s}.html".format(env_name)
    tests_html_file = os.path.join(tests_dir, "reports", tests_html_filename)

    return_code = run(
        "pytest {posargs} "
        "--cov={module} "
        "--html={tests_html_file} "
        "--self-contained-html".format(
            module=module,
            tests_html_file=tests_html_file,
            envname=env_name,
            posargs=tests_dir
        )
    )
  return return_code


if __name__ == '__main__':
  import sys

  sys.exit(main())
