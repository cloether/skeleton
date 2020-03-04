#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""__init__.py

Skeleton
--------
Skeleton is an template for easily creating Python modules.

The official repo is at <https://github.com/cloether/skeleton>.

:copyright: Copyright 2020 Chad Loether
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

APP_ID = "-".join((__title__, __version__))

from . import cli, error, log, utils

try:
  from logging import NullHandler
except ImportError:
  from logging import Handler

  class NullHandler(Handler):
    """Needed for Backwards Compatibility (Python 2.6).

    Notes:
      NullHandler was introduced in Python 2.7
    """

    def emit(self, record):
      """Emit Nothing"""

from logging import getLogger

getLogger(__name__).addHandler(NullHandler())
