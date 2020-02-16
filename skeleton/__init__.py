#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""__init__.py
"""
__all__ = ("__version__", "cli", "error", "log", "utils")

from .__version__ import __version__
from . import cli, error, log, utils

try:
  from logging import NullHandler
except ImportError:
  from logging import Handler


  class NullHandler(Handler):
    """Python 2.7 introduced a NullHandler which we want to use,
    but to support older versions, we implement our own if needed.
    """

    def emit(self, record):
      """Emit Nothing"""

from logging import getLogger

getLogger(__name__).addHandler(NullHandler())
