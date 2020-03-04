#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""clean.py
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILES = (
    (".coverage",),
    (".tox",),
    ("build",),
    ("dist",),
    ("docs", "build"),
    ("skeleton.egg-info",),
    ("tests", ".pytest_cache"),
    ("tests", "pytest.log"),
    ("tests", "reports"),
)


def main():
  """Script Entry Point
  """
  for file_or_dir in map(lambda parts: os.path.join(REPO_ROOT, *parts), FILES):
    if os.path.isdir(file_or_dir):
      os.system("rm -rf %s" % file_or_dir)
      sys.stdout.write("Removed Directory: %s\n" % file_or_dir)
    elif os.path.isfile(file_or_dir):
      os.remove(file_or_dir)
      sys.stdout.write("Removed File: %s\n" % file_or_dir)
    else:
      sys.stderr.write("Unknown File or Directory: %s\n" % file_or_dir)
  return 0


if __name__ == '__main__':
  sys.exit(main())
