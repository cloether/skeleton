#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""clean.py
"""
import os

_DIRNAME = os.path.dirname
REPO_ROOT = _DIRNAME(_DIRNAME(os.path.abspath(__file__)))
os.chdir(os.path.join(REPO_ROOT))
DELETE_DIRS = [
    os.path.join(REPO_ROOT, "tests", ".pytest_cache"),
    os.path.join(REPO_ROOT, "build"),
    os.path.join(REPO_ROOT, "dist"),
    os.path.join(REPO_ROOT, "skeleton.egg-info")
]
for dirname in DELETE_DIRS:
  # TODO: Implement equivalent of unix `rm -rf`
  os.system("rm -rf %s" % dirname)
  print("REMOVED: %s" % dirname)
