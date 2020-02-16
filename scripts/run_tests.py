#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""run_tests.py

Don't run tests from the root repo dir.

We want to ensure we're importing from the installed binary package not
from the CWD.
"""

import os
from subprocess import check_call

_DIRNAME = os.path.dirname
REPO_ROOT = _DIRNAME(_DIRNAME(os.path.abspath(__file__)))
TESTS_DIR = os.path.join(REPO_ROOT, 'tests')

os.chdir(os.path.join(REPO_ROOT))


def _run(command):
  return check_call(command, shell=True)


def _touch(filename, times=None):
  fh = open(filename, 'a')
  try:
    os.utime(filename, times)
  finally:
    fh.close()


TESTS_LOG_FILE = os.path.join(TESTS_DIR, "pytest.log")

if not os.path.exists(TESTS_LOG_FILE):
  _touch(TESTS_LOG_FILE)

_run("python -m pytest -c %s" % os.path.join(REPO_ROOT, "setup.cfg"))
