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
os.chdir(REPO_ROOT)


def _run(command):
  return check_call(command, shell=True)


TESTS_DIR = os.path.join(REPO_ROOT, 'tests')
TESTS_LOG_FILE = os.path.join(TESTS_DIR, "pytest.log")
if not os.path.exists(TESTS_LOG_FILE):
  # `touch` file pytest.log
  fh = open(TESTS_LOG_FILE, 'a')
  try:
    os.utime(TESTS_LOG_FILE, None)
  finally:
    fh.close()
_run("tox")
