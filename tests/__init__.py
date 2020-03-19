#!/usr/bin/env python
# -*- coding: utf8 -*-
"""__init__.py
"""
import logging
import sys

if '-v' in sys.argv:
  logging.basicConfig(level=logging.DEBUG)
else:
  logging.basicConfig(level=logging.CRITICAL)
