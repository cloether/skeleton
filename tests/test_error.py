#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""test_error.py

Error Testing.
"""
import logging

from skeleton.error import BaseError

LOGGER = logging.getLogger(__name__)


def test_base_error():
  try:
    raise BaseError(error="TEST ERROR MESSAGE")
  except BaseError as e:
    LOGGER.debug("Caught Test Exception: %r", e)
    assert e.args[0] == BaseError.fmt.format(error="TEST ERROR MESSAGE")
    return True
