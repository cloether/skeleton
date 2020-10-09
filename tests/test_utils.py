# coding=utf8
"""test_utils.py
"""
from __future__ import absolute_import, print_function, unicode_literals

import logging

from skeleton.utils import (
  to_valid_filename,
  to_valid_module_name
)

LOGGER = logging.getLogger(__name__)


def test_to_valid_filename():
  """Test skeleton.to_valid_filename
  """
  bad_filename = "iceceqrbv\\dfvrv"
  filename = to_valid_module_name("iceceqrbv\\dfvrv")
  LOGGER.debug("input: %s output: %s", bad_filename, filename)
  return True


def test_to_module_filename():
  """Test skeleton.to_valid_filename
  """
  bad_module_name = "iceceqrbv\\dfvrv"
  filename = to_valid_filename(bad_module_name)
  LOGGER.debug("input: %s output: %s", bad_module_name, filename)
  return True
