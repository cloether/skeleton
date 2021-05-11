# coding=utf8
"""__init__.py

``skeleton`` is a template used for creating Python modules.

The official repo is `here`_.

  .. note:: This library is under active development.

.. _here: https://github.com/cloether/skeleton
"""
from __future__ import absolute_import, print_function, unicode_literals

__all__ = (
    "__app_id__",
    "__author__",
    "__author_email__",
    "__copyright__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "cli",
    "config",
    "const",
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

try:
  from logging import NullHandler
except ImportError:
  from logging import Handler

  class NullHandler(Handler):
    """Needed for Backwards Compatibility (Python 2.6).

    Notes:
      NullHandler was introduced in Python 2.7.
    """

    def emit(self, record):
      """Emit Nothing."""

from logging import getLogger  # pylint: disable=wrong-import-order

getLogger(__name__).addHandler(NullHandler())
