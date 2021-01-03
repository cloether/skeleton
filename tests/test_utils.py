# coding=utf8
"""test_utils.py
"""
from __future__ import absolute_import, print_function, unicode_literals

import logging

from skeleton.utils import (
  as_bool, as_number, to_valid_filename,
  to_valid_module_name
)

LOGGER = logging.getLogger(__name__)


def test_as_number(number):
  """Test as_number function.
  """
  num = as_number(number)
  assert isinstance(num, int), "error converting string to number: " + number
  return num


def test_as_bool(boolean):
  """Test as_bool function.
  """
  num = as_bool(boolean)
  assert isinstance(num, bool), "error converting string to bool: " + boolean
  return num


def test_to_valid_filename(filename):
  """Test skeleton.to_valid_filename.
  """
  filename = to_valid_filename(filename)
  LOGGER.debug("input: %s output: %s", filename, filename)
  return filename


def test_to_valid_module_name(module_name):
  """Test skeleton.to_valid_module_name.
  """
  modname = to_valid_module_name(module_name)
  LOGGER.debug("input: %s output: %s", module_name, modname)
  return modname
