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

  # Needed for Backwards Compatibility (Python 2.6).
  # Note: NullHandler was introduced in Python 2.7.
  class NullHandler(Handler):
    """This handler does nothing. It's intended to be used
    to avoid the "No handlers could be found for logger XXX"
    one-off warning. This is important for library code, which
    may contain code to log events. If a user of the library
    does not configure logging, the one-off warning might be
    produced; to avoid this, the library developer simply needs
    to instantiate a NullHandler and add it to the top-level
    logger of the library module or package.
    """

    def handle(self, record):
      """stub"""

    def emit(self, record):
      """stub"""

    def createLock(self):
      """stub."""
      self.lock = None

    def _at_fork_reinit(self):
      """stub"""

from logging import getLogger  # pylint: disable=wrong-import-order

getLogger(__name__).addHandler(NullHandler())
