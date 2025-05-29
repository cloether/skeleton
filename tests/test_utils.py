# coding=utf8
"""test_utils.py
"""
from __future__ import absolute_import, print_function, unicode_literals

import logging
import os

from six import binary_type, integer_types

from skeleton.utils import (
  as_bool,
  as_number,
  is_file_newer_than_file, safe_b64decode,
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


def test_as_number_converts_numeric_string_to_int():
  """Test that as_number converts numeric strings to int."""
  assert as_number("42") == 42


def test_as_number_converts_decimal_string_to_float():
  """Test that as_number converts decimal strings to float."""
  assert as_number("3.14") == 3.14


def test_as_number_returns_int_for_int_input():
  """Test that as_number returns the original integer value."""
  assert as_number(7) == 7


def test_as_number_returns_value_for_non_numeric_string():
  """Test that as_number returns the original value for non-numeric strings."""
  assert as_number("foo") == "foo"


def test_as_bool_converts_true_strings_to_true():
  """Test that as_bool converts various true strings to True."""
  for val in ["y", "yes", "t", "true", "on", "1"]:
    assert as_bool(val) is True


def test_as_bool_converts_false_strings_to_false():
  """Test that as_bool converts various false strings to False."""
  for val in ["n", "no", "f", "false", "off", "0"]:
    assert as_bool(val) is False


def test_as_bool_returns_bool_for_bool_input():
  """Test that as_bool returns the original boolean value."""
  assert as_bool(True) is True
  assert as_bool(False) is False


def test_as_bool_returns_value_for_invalid_string():
  """Test that as_bool returns the original value for non-boolean strings."""
  assert as_bool("maybe") == "maybe"


def safe_b64decode_decodes_padded_base64():
  """Test that safe_b64decode can decode padded base64."""
  assert safe_b64decode("Q2hhZAo=") == b"Chad\n"


def safe_b64decode_decodes_unpadded_base64():
  """Test that safe_b64decode can decode unpadded base64."""
  assert safe_b64decode("Q2hhZAo") == b"Chad\n"


def to_valid_filename_replaces_invalid_characters():
  """Test that invalid characters are replaced in filenames."""
  assert to_valid_filename("My File@2024!.txt") == "my-file-2024-.txt"


def to_valid_filename_allows_valid_characters():
  """Test that valid characters are preserved in filenames."""
  assert to_valid_filename("abc-123.txt") == "abc-123.txt"


def to_valid_module_name_replaces_hyphens_with_underscores():
  """Test that hyphens are replaced with underscores in module names."""
  assert to_valid_module_name("my-module") == "my_module"


def to_valid_module_name_handles_file_extensions():
  """Test that file extensions are preserved in module names."""
  assert to_valid_module_name("my-module.py") == "my_module.py"


def test_is_file_newer_than_file_returns_true_for_newer_file(tmp_path):
  """Test that is_file_newer_than_file returns True for a newer file."""
  file_a = tmp_path / "a.txt"
  file_b = tmp_path / "b.txt"
  file_a.write_text("a")
  file_b.write_text("b")
  os.utime(
    file_a,
    (os.path.getmtime(file_b) + 10, os.path.getmtime(file_b) + 10)
  )
  assert is_file_newer_than_file(str(file_a), str(file_b)) is True


def test_is_file_newer_than_file_returns_false_for_older_file(tmp_path):
  """Test that is_file_newer_than_file returns False for an older file."""
  file_a = tmp_path / "a.txt"
  file_b = tmp_path / "b.txt"
  file_a.write_text("a")
  file_b.write_text("b")
  os.utime(
    file_b,
    (os.path.getmtime(file_a) + 10, os.path.getmtime(file_a) + 10)
  )
  assert is_file_newer_than_file(str(file_a), str(file_b)) is False


def test_is_file_newer_than_file_handles_missing_file(tmp_path):
  """Test that is_file_newer_than_file returns True for a
  file compared to a missing file.
  """
  file_a = tmp_path / "a.txt"
  file_a.write_text("a")
  assert is_file_newer_than_file(
    str(file_a),
    str(tmp_path / "missing.txt")
  ) is True
