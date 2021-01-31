#!/usr/bin/env python
# coding=utf8
"""apidoc.py
"""
from __future__ import absolute_import, print_function, unicode_literals

import os
from contextlib import contextmanager
from subprocess import CalledProcessError, check_call

from setuptools import find_packages
from six import next


@contextmanager
def cwd(dirname):
  """Context manager for operating in a different directory.

  Args:
    dirname (str): Path to directory which will become
      the current working directory.

  Yields:
    str: Original current working directory path.
  """
  orig = os.getcwd()
  os.chdir(dirname)
  try:
    yield orig
  finally:
    os.chdir(orig)


def _run(command, **kwargs):
  """Wrapper around subprocess.check_call with some
  added (minimal) error handling.

  Args:
    command (str): Command to run.

  Returns:
    int: Return Code.
  """
  kwargs.setdefault("shell", True)
  try:
    return_code = check_call(command, **kwargs)
  except CalledProcessError as e:
    sys.stderr.write("{0!r}\n".format(e))
    return_code = e.returncode
  return return_code


def run(command, location=None):
  """Run Command.

  Args:
    command (str): Command to run.
    location (str): Location to run command from.

  Returns:
    int: Return Code.
  """
  if location is not None:
    with cwd(location):
      return run(command)
  return run(command)


def module_name(exclude=("doc*", "example*", "script*", "test*"), where=".",
                include=('*',), default=None):
  """Get current module name.

  Args:
    exclude (tuple or list): sequence of package names to exclude; '*'
      can be used as a wildcard in the names, such that 'foo.*' will
      exclude all subpackages of 'foo' (but not 'foo' itself).
    where (str): root directory which will be searched for packages.  It
      should be supplied as a "cross-platform" (i.e. URL-style) path; it will
      be converted to the appropriate local path syntax.
    include (tuple or list): sequence of package names to include.
      If it's specified, only the named packages will be included.
      If it's not specified, all found packages will be included.
      'include' can contain shell style wildcard patterns just like
      'exclude'.
    default: default value to return if module name is not found.

  Returns:
    str: Module name if found otherwise None.
  """
  packages = find_packages(exclude=exclude, where=where, include=include)
  return next(iter(packages), default)


def docs_gen():
  """Generate Project Documentation Files using sphinx-apidoc.

  Returns:
    int: Return code.
  """
  repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  docs_source = os.path.join(repo_root, "docs", "source")
  module_path = os.path.join(repo_root, module_name(where=repo_root))
  return run(" ".join(["sphinx-apidoc", "-f", "-o", docs_source, module_path]))


def docs_build():
  """Build Project Documentation.
  """
  repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  return run("make html", os.path.join(repo_root, "docs"))


def main():
  """CLI Entry Point
  """
  return (
      docs_build
      if "-b" in sys.argv or "--build" in sys.argv
      else docs_gen
  )()


if __name__ == "__main__":
  import sys

  sys.exit(main())
