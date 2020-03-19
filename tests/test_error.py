#!/usr/bin/env python
# -*- coding: utf8 -*-
"""test_error.py

Error Testing.
"""
import logging

import pytest

from skeleton.error import BaseError

LOGGER = logging.getLogger(__name__)


@pytest.fixture
def error():
  """Error Fixture

  Returns:
    skeleton.BaseError: Instance of BaseError
  """
  return BaseError(error="TEST ERROR MESSAGE")


def test_base_error(error):
  """Test `skeleton.error.BaseError`

  Returns:
    bool: True if success, otherwise False
  """
  LOGGER.debug(
      "BaseError: fmt=%s, msg=%s, args=%s, kwargs=%s",
      error.msg, error.kwargs, error.fmt, error.args
  )

  try:
    raise BaseError(error="TEST ERROR MESSAGE")

  except BaseError as e:
    LOGGER.debug("Caught Test Exception: %r", e)
    assert e.args[0] == BaseError.fmt.format(error="TEST ERROR MESSAGE")
    return True

  except Exception as e:
    LOGGER.debug("Caught Incorrect Exception: %r", e)
    return False
