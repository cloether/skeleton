#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""__init__.py
"""

from .__version__ import (
  __author__,
  __author_email__,
  __description__,
  __license__,
  __name__,
  __url__,
  __version__
)

from . import cli, errors, log, utils

try:
  from logging import NullHandler
except ImportError:
  from logging import Handler

  class NullHandler(Handler):
    """Python 2.7 introduced a NullHandler which we want to use,
    but to support older versions, we implement our own if needed.
    """

    def emit(self, record):
      """Emit Nothing
      """

import logging

logging.getLogger(__name__).addHandler(NullHandler())

__all__ = (
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__name__",
    "__url__",
    "__version__",
    "cli",
    "errors",
    "log",
    "utils"
)
