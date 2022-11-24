#!/usr/bin/env python3
# coding=utf8
"""cleanup.py
"""
from __future__ import absolute_import, print_function, unicode_literals

import copy
import glob
import os
import sys

from setuptools import find_packages
from six import next

TARGETS = [
    # TODO: Add support for globs/regex
    (".coverage*",),
    (".pytest_cache",),
    (".tox",),
    ("build",),
    ("dist",),
    ("docs", "build"),
    ("logs",),
    ("tests", ".pytest_cache"),
    ("tests", "pytest.log"),
    ("tests", "logs"),
    ("tests", "reports"),
    ("tests", "tests")
]


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
      'include' may contain shell-style wildcard patterns, just like
      'exclude'.
    default: default value to return if module name is not found.

  Returns:
    str: Module name if found otherwise None.
  """
  packages = find_packages(exclude=exclude, where=where, include=include)
  return next(iter(packages), default)


def main():
  """Script Entry Point.
  """
  repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

  files = copy.copy(TARGETS)
  files.append(("{0!s}.egg-info".format(module_name(where=repo_root)),))

  def _join_repo(parts):
    return os.path.join(repo_root, *parts)

  def _handle_file(value):
    sys.stdout.write("removing File: {0!s}\n".format(value))
    os.remove(value)

  def _handle_dir(value):
    sys.stdout.write("removing directory: {0!s}\n".format(value))
    os.system("rm -rf {0}".format(value))

  def _handle_unknown(value):
    sys.stderr.write("invalid filepath: {0!s}\n".format(value))

  for file_or_dir in map(_join_repo, files):
    for item in glob.glob(file_or_dir):
      if os.path.isdir(item):
        _handle_dir(item)
      elif os.path.isfile(item):
        _handle_file(item)
      else:
        _handle_unknown(item)
  return 0


if __name__ == "__main__":
  sys.exit(main())
