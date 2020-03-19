#!/usr/bin/env python
# -*- coding: utf8 -*-
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


def _touch(filepath):
  """Equivalent of Unix `touch` command
  """
  if not os.path.exists(filepath):
    fh = open(filepath, 'a')
    try:
      os.utime(filepath, None)
    finally:
      fh.close()


TESTS_DIR = os.path.join(REPO_ROOT, 'tests')
TESTS_LOG_FILE = os.path.join(TESTS_DIR, "pytest.log")

_touch(TESTS_LOG_FILE)

_run(
    "pytest %(posargs)s "
    "--cov=skeleton "
    "--html=tests/reports/%(envname)s.html "
    "--self-contained-html" % {
        "envname": os.getenv("ENVNAME", "test"),
        "posargs": TESTS_DIR
    }
)
