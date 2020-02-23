#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""test_cli.py

Command Line Interface (cli) Tests.
"""
import logging
from subprocess import check_call

LOGGER = logging.getLogger(__name__)


def test_cli():
  """Test Command Line Interface (cli).

  Returns:
    bool: True if success, otherwise False.
  """
  # noinspection PyBroadException
  try:
    check_call("python -m skeleton", shell=True)

  except NotImplementedError:
    return False

  except Exception:
    LOGGER.exception("CLI Command Execution FAILED: python -m skeleton")
    return False

  else:
    LOGGER.debug("CLI Command Execution SUCCESS: python -m skeleton")
    return True
