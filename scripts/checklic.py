#!/usr/bin/env python3
# coding=utf8
"""checklic.py

Verify that all *.py files have a license header in the file.

References:
  # modified from link below
  https://github.com/microsoft/knack/blob/master/scripts/license_verify.py
"""
# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# See License.txt in the project root for license information.
# ------------------------------------------------------------------------------
from __future__ import absolute_import, print_function, unicode_literals

import logging
import os

LOGGER = logging.getLogger(__name__)

PARENT_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(PARENT_DIR, '..'))

# noinspection LongLine
PY_LICENSE_HEADER = """\
# ------------------------------------------------------------------------------
# Copyright (c) {0}. All rights reserved.
# Licensed under the MIT License.
# See LICENSE.txt in the project root for license information.
# ------------------------------------------------------------------------------
"""

ENV_DIRS = frozenset([
    os.path.join(ROOT_DIR, 'env'),
    os.path.join(ROOT_DIR, 'env27'),
    os.path.join(ROOT_DIR, '.tox'),
])


def contains_header(text):
  """Check if the provided text contains the PY_LICENSE_HEADER.

  Args:
    text (str): Text to check.

  Returns:
    bool: True if the text contains the PY_LICENSE_HEADER,
      otherwise False.
  """
  return PY_LICENSE_HEADER in text


def get_files_without_header(extensions=('.py',), root_dir=ROOT_DIR,
                             env_dirs=ENV_DIRS):
  """Find files without a license header.

  Args:
    extensions (str or tuple): File extension(s) to search for.
    root_dir (str): Root directory.
    env_dirs (list): List of directories.

  Returns:
    list of str: List of files which do not contain a license header.
  """
  files_without_header = []
  for dirpath, _, filenames in os.walk(root_dir):
    # skip folders generated by virtual env
    if any(d for d in env_dirs if d in dirpath):
      continue
    for a_file in filenames:
      if a_file.endswith(extensions):
        cur_file_path = os.path.join(dirpath, a_file)
        with open(cur_file_path, 'r') as fd:
          file_text = fd.read()
        if len(file_text) > 0 and not contains_header(file_text):
          files_without_header.append((cur_file_path, file_text))
  return files_without_header


def main():
  """Entry Point.
  """
  missing_header = [
      file_path
      for file_path, file_contents
      in get_files_without_header()
  ]
  n = len(missing_header)
  sys.stderr.write("file(s) missing license header: {0:d}\n".format(n))
  for filepath in missing_header:
    sys.stderr.write("missing license header: {0:s}\n".format(filepath))
  return bool(n)


if __name__ == "__main__":
  import sys

  sys.exit(main())
