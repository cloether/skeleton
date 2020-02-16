#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""__init__.py

Skeleton
--------
Skeleton is an template for easily creating Python modules.

The official repo is at <https://github.com/cloether/skeleton>.

:copyright: (c) 2020 Chad Loether.
:license: MIT, see LICENSE for more details.
"""
__all__ = (
    "__author__",
    "__author_email__",
    "__copyright__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "cli",
    "error",
    "log",
    "utils"
)

from .__version__ import (
  __author__,
  __author_email__,
  __copyright__,
  __description__,
  __license__,
  __title__,
  __url__,
  __version__,
)

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
