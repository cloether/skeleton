#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""clean.py
"""
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

for file_or_dir in map(lambda parts: os.path.join(REPO_ROOT, *parts), (
    (".coverage",),
    (".tox",),
    ("build",),
    ("dist",),
    ("docs", "build"),
    ("skeleton.egg-info",),
    ("tests", ".pytest_cache"),
    ("tests", "pytest.log"),
    ("tests", "reports"),
)):

  if os.path.isdir(file_or_dir):
    os.system("rm -rf %s" % file_or_dir)
    print("Removed Directory: %s" % file_or_dir)

  elif os.path.isfile(file_or_dir):
    os.remove(file_or_dir)
    print("Removed File: %s" % file_or_dir)

  else:
    print("Unknown File or Directory: %s" % file_or_dir)
