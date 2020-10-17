# coding=utf8
"""test_error.py

Error Testing.
"""
from __future__ import absolute_import, print_function, unicode_literals

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
      """
BaseError:
  fmt=%s
  msg=%s
  args=%s
  kwargs=%s
""",
      error.msg,
      error.kwargs,
      error.fmt,
      error.args
  )
  try:
    raise error
  except BaseError as e:
    LOGGER.exception("Caught Test Exception: %s", e.json)
    assert e.args[0] == BaseError.fmt.format(error="TEST ERROR MESSAGE")
    return True
  except Exception as e:
    LOGGER.debug("Caught Incorrect Exception: %r", e)
    return False
