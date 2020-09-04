# coding=utf8
"""
Skeleton
========
Skeleton is an template for easily creating Python modules.

See the official repo [here](https://github.com/cloether/skeleton)
"""
from __future__ import absolute_import, print_function, unicode_literals

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

__app_id__ = "-".join((__title__, __version__))

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
      """Emit Nothing
      """

from logging import getLogger

getLogger(__name__).addHandler(NullHandler())
