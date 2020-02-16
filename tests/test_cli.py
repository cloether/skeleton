#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""test_cli.py

Command Line Interface (cli) Tests.
"""
import logging
from subprocess import check_call

LOGGER = logging.getLogger(__name__)


def test_cli():
  """Test Command Line Interface (cli)

  Returns:
    int: 0 if success, otherwise 1.
  """
  try:
    check_call("python -m skeleton", shell=True)
  except NotImplementedError as e:
    return 0
  except Exception as e:
    LOGGER.error("CLI Failed: %s", e)
    return 1
  else:
    return 0
