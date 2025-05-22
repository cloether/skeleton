#!/usr/bin/env python3
# coding=utf8
"""run_tests.py

Run tests for python module.

Warnings:
  Do not run tests from the root repo dir.

  We want to ensure we're importing from the installed binary package not
  from the CWD.
"""
from __future__ import absolute_import, print_function, unicode_literals

import logging
import os
from contextlib import contextmanager
from errno import EEXIST
from subprocess import CalledProcessError, check_call

from setuptools import find_packages
from six import next


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


def module_name(exclude=("doc*", "example*", "script*", "test*"), where=".",
                include=('*',), default=None):
  """Get current module name.

  Args:
    exclude (tuple or list): sequence of package names to exclude;
      '*' can be used as a wildcard in the names, such that 'foo.*'
      will exclude all subpackages of 'foo' (but not 'foo' itself).
    where (str): root directory which will be searched for packages.
      It should be supplied as a "cross-platform" (i.e. URL-style)
      path; it will be converted to the appropriate local path
      syntax.
    include (tuple or list): sequence of package names to include.
      If it's specified, only the named packages will be included.
      If it's not specified, all found packages will be included.
      'include' can contain shell-style wildcard patterns just like
      'exclude'.
    default: default value to return if module name is not found.

  Returns:
    str: Module name if found otherwise None.
  """
  packages = find_packages(exclude=exclude, where=where, include=include)
  return next(iter(packages), default)


def mkdir_p(path):
  """Create entire filepath.

  Notes:
    Unix "mkdir -p" equivalent.

  Args:
    path (str): Filepath to create.

  Raises:
    OSError: Raised for exceptions unrelated to the
      directory already existing.
  """
  try:
    os.makedirs(path)
  except OSError as exc:
    if exc.errno != EEXIST:
      raise


def mkdirs_p(*path):
  """Create multiple directories.

  Notes:
    Unix "mkdir -p" equivalent.

  Args:
    path (str): Filepaths to create.

  Raises:
    OSError: Raised for exceptions unrelated to the
      directory already existing.
  """
  for p in path:
    mkdir_p(p)


def touch(filepath):
  """Equivalent of Unix `touch` command.

  Args:
    filepath (str): Path to touch file.
  """
  if not os.path.exists(filepath):
    fh = open(filepath, "a+")
    try:
      os.utime(filepath, None)
    finally:
      fh.close()


# TODO: update for changes in pytest and coverage configs

def main():
  """CLI Entry Point.

  Returns:
    int: Command return code.
  """
  logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")

  repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  module = module_name(where=repo_root)
  logging.debug("running tests for module: %s", module)

  return_code = -1  # noqa

  with cwd(repo_root):
    # noinspection PyUnusedLocal
    env_name = os.getenv("ENVNAME", "test")

    tests_dir = os.path.join(repo_root, "tests")
    logs_dir = os.path.join(tests_dir, "logs")
    reports_dir = os.path.join(tests_dir, "reports")
    tests_log_file = os.path.join(logs_dir, "pytest.log")

    mkdirs_p(logs_dir, reports_dir)
    touch(tests_log_file)  # prevent pytest error due to missing log file

    return_code = run("pytest {posargs} --cov={module}".format(
      posargs=tests_dir,
      module=module
    ))

  return return_code


if __name__ == "__main__":
  import sys

  sys.exit(main())
