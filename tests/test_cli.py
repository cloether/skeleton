#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""test_cli.py

Command Line Interface (cli) Tests.
"""
from subprocess import check_call


def test_cli():
  try:
    check_call("python -m skeleton", shell=True)
  except NotImplementedError as e:
    return 0
  else:
    return 0
