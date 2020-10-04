# coding=utf8
"""__init__.py
"""
from __future__ import absolute_import, print_function, unicode_literals

import logging
import sys

if '-v' in sys.argv:
  logging.basicConfig(level=logging.DEBUG)
else:
  logging.basicConfig(level=logging.CRITICAL)
