# coding=utf8
"""test_error.py

Error Testing.
"""
from __future__ import absolute_import, print_function, unicode_literals

import logging

from skeleton.error import BaseError

__all__ = (
  "test_base_error",
)

LOGGER = logging.getLogger(__name__)


def test_base_error(error):
  """Test `skeleton.error.BaseError`

  Returns:
    bool: True if success, otherwise False
  """
  LOGGER.debug("""\
BaseError:
  fmt=%s
  msg=%s
  args=%s
  kwargs=%s
""", error.msg, error.kwargs, error.fmt, error.args)

  try:
    raise error
  except BaseError as e:
    LOGGER.exception("Caught Test Exception: %s", e.json)
    assert e.args[0] == BaseError.fmt.format(error="TEST ERROR MESSAGE")

  except Exception as e:
    LOGGER.debug("Caught Incorrect Exception: %r", e)
    assert False, "Caught Incorrect Exception: {0}".format(e)
