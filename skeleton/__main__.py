# coding=utf8
"""__main__.py

Command Line Interface (CLI) Entry Point
"""
from __future__ import absolute_import, print_function, unicode_literals

import errno
import os
import sys

from .cli import main

# Force absolute path on Python 2.
# https://github.com/microsoft/debugpy/blob/master/src/debugpy/__main__.py
__file__ = os.path.abspath(__file__)  # noqa


def handle_shutdown(func):
  """Decorator to catch shutdown signals.
  """
  import signal

  def _shutdown_handler(signum, frame):  # noqa
    """Handle Shutdown.

    Args:
      signum (int): Signal Number,
      frame (types.FrameType): Interrupted Stack Frame.

    Raises:
      (SystemExit): Calls sys.exit(), which raises a SystemExit exception.
    """
    sys.stderr.write("\b\b")  # write 2 backspaces to stderr
    sys.stderr.write("interrupt detected: signal={0:d}\n".format(signum))
    sys.exit(signum)

  def _f(*args, **kwargs):
    signal.signal(signal.SIGTERM, _shutdown_handler)
    signal.signal(signal.SIGINT, _shutdown_handler)

    if os.name == "nt":
      signal.signal(signal.SIGBREAK, _shutdown_handler)

    return func(*args, **kwargs)

  return _f


def persistence_mode(func):
  """Decorator for when binary mode is required for persistent
  mode on windows. sys.stdout in Python is by default opened in
  text mode, and writes to this stdout produce corrupted binary
  data on Windows.

    python -c "import sys; sys.stdout.write(\"_\n_\")" > file
    python -c "print(repr(open(\"file\", \"rb\").read()))"
  """
  if sys.platform == "Win32":
    def _inner(*args, **kwargs):
      import msvcrt  # noqa

      msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
      msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
      msvcrt.setmode(sys.stderr.fileno(), os.O_BINARY)

      return func(*args, **kwargs)
  else:
    def _inner(*args, **kwargs):
      return func(*args, **kwargs)

  return _inner


def epipe(func):
  """Decorator to Handle EPIPE Errors.

  Raises:
    IOError: Raised when non-EPIPE exceptions are encountered.
  """

  def _f(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except IOError as e:
      if e.errno == errno.EPIPE:
        sys.exit(e.errno)
      raise

  return _f


def handle_errors(func):
  """Error handler decorator
  """

  def _inner(*args, **kwargs):
    try:
      ret = func(*args, **kwargs)
    except NotImplementedError as e:
      sys.stderr.write("{0!r}".format(e))
      sys.stderr.flush()
      sys.exit(0)

    except KeyboardInterrupt as e:
      sys.exit(e)

    except Exception as e:
      sys.stderr.write("{0!r}".format(e))
      sys.stderr.flush()
      sys.exit(1)

    except:  # noqa
      import traceback

      traceback.print_last()
      sys.exit(-1)
    else:
      sys.exit(ret)

  return _inner


def _wrap_func(func, wrappers=()):
  for wrapper in wrappers:
    func = wrapper(func)
  return func


if __name__ == "__main__":
  _wrap_func(main, (persistence_mode, handle_shutdown, handle_errors))()
