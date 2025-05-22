# coding=utf8
"""test_utils.py
"""
from __future__ import absolute_import, print_function, unicode_literals

import logging

from six import binary_type, integer_types

from skeleton.utils import (
  as_bool,
  as_number,
  safe_b64decode,
  to_valid_filename,
  to_valid_module_name
)

__all__ = (
  "test_safe_b64decode",
  "test_as_number",
  "test_as_bool",
  "test_to_valid_filename",
  "test_to_valid_module_name"
)

LOGGER = logging.getLogger(__name__)


def test_safe_b64decode():
  """Test Safe Base64 Decode
  """
  value = "Q2hhZAo="
  decoded = safe_b64decode(value)
  LOGGER.debug("input: %s output: %s", value, decoded)
  assert isinstance(decoded, binary_type), "invalid decoded base64 return type"


def test_as_number(number):
  """Test as_number function.
  """
  num = as_number(number)
  assert isinstance(num, integer_types), (
    "error converting str to number: {0}"
  ).format(number)


def test_as_bool(boolean):
  """Test as_bool function.
  """
  num = as_bool(boolean)
  assert isinstance(num, bool), "error converting string to bool: " + boolean


def test_to_valid_filename(filename):
  """Test skeleton.to_valid_filename.
  """
  valid_filename = to_valid_filename(filename)
  LOGGER.debug("input: %s output: %s", filename, filename)
  assert filename != valid_filename


def test_to_valid_module_name(modname):
  """Test skeleton.to_valid_module_name.
  """
  valid_module_name = to_valid_module_name(modname)
  LOGGER.debug("input: %s output: %s", modname, valid_module_name)
  assert modname != valid_module_name
