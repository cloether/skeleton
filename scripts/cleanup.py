#!/usr/bin/env python
# coding=utf8
"""cleanup.py
"""
import os
import sys

from setuptools import find_packages

FILES = [
    (".coverage",),
    (".tox",),
    ("build",),
    ("dist",),
    ("docs", "build"),
    ("tests", ".pytest_cache"),
    ("tests", "pytest.log"),
    ("tests", "reports")
]


def module_name(exclude=("test",), where="."):
  """Get current module name.

  Returns:
    str or NoneType: Module name or None
  """
  return next(iter(find_packages(exclude=exclude, where=where)), None)


def main():
  """Script Entry Point
  """
  repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

  files = FILES.copy()

  files.append(
      ("{0!s}.egg-info".format(module_name(where=repo_root)),)
  )

  def join_repo(parts):
    return os.path.join(repo_root, *parts)

  def _handle_file(value):
    sys.stdout.write("Removing File: {0!s}\n".format(value))
    os.remove(value)

  def _handle_dir(value):
    sys.stdout.write("Removing Directory: {0!s}\n".format(value))
    os.system("rm -rf %s" % value)

  def _handle_unknown(value):
    sys.stderr.write("Invalid Filepath: {0!s}\n".format(value))

  for file_or_dir in map(join_repo, files):
    if os.path.isdir(file_or_dir):
      _handle_dir(file_or_dir)
    elif os.path.isfile(file_or_dir):
      _handle_file(file_or_dir)
    else:
      _handle_unknown(file_or_dir)

  return 0


if __name__ == '__main__':
  sys.exit(main())
