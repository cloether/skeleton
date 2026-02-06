# coding=utf8
"""test_version.py
"""
from __future__ import absolute_import, print_function, unicode_literals

import re

try:
  import importlib.metadata as importlib_metadata
except ImportError:
  import importlib_metadata  # noqa

from skeleton import __version__ as code_version


def __find_meta(filepath, **kwargs):
  """Extract metadata from a Python file.

  Args:
    filepath (str): Path to the file.
    **kwargs: Additional arguments for `open()`.

  Returns:
    dict: A dictionary containing the metadata.
  """
  if "b" not in kwargs.get("mode", ""):
    kwargs.setdefault("encoding", "utf8")

  with open(filepath, **kwargs) as fd:
    content = fd.read()

  pattern = re.compile(
    r'^__(?P<name>[a-zA-Z0-9_]+)__\s*=\s*([\'"])(?P<value>.*?)(?<!\\)\2\s*$',
    re.M
  )
  match = pattern.findall(content)

  if not match:
    raise RuntimeError("error finding module meta in file: %s" % filepath)

  return {k: v for k, _, v in match}


def __getkey(meta, key, default=None):
  """Retrieve a key from the metadata dictionary.

  Args:
    meta (dict): Metadata dictionary.
    key (str): Key to retrieve.
    default (any, optional): Default value if the key is not found.

  Returns:
    str: Value of the key in the metadata.

  Raises:
    KeyError: If the key is not found and no default is provided.
  """
  value = meta.get(key, default)
  if value is None:
    raise KeyError("key not found in metadata: {0}".format(key))
  return value


def test_version_matches_metadata(version_file):
  metadata = __find_meta(version_file)
  metadata_version = __getkey(metadata, "version")
  assert code_version == metadata_version
