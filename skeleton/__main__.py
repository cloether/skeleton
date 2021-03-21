# coding=utf8
"""__main__.py

Module CLI Entry Point
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

  Args:
    func (callable): Function to decorate.

  Returns:
    callable: Decorated function.
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

    result = func(*args, **kwargs)
    # TODO: Remove signal handlers?
    return result

  return _f


def persistence_mode(func):
  """Decorator for when binary mode is required for
  persistent mode on windows.

  Notes:
    sys.stdout in Python is by default opened in text
    mode, and writes to this stdout produce corrupted
    binary data on Windows.

    Examples:
      python -c "import sys; sys.stdout.write(\"_\n_\")" > file
      python -c "print(repr(open(\"file\", \"rb\").read()))"

  Args:
    func (callable): Function to decorate.

  Returns:
    callable: Decorated function.
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

  Args:
    func (callable): Function to decorate.

  Returns:
    callable: Decorated function.

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
  """Error handler decorator.

  Args:
    func (callable): Function to decorate.

  Returns:
    callable: Decorated function.
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


def wrap_func(func, wrappers=()):
  """Wrap the provided function in each wrapper function.

  Args:
    func (callable): Function to wrap.
    wrappers (callable or tuple or list of callable): Iterable
      of callables in which to wrap the provided callable.

  Returns:
    callable: Wrapped callable.
  """
  if not wrappers or wrappers is None:
    return func

  if callable(wrappers):
    wrappers = (wrappers,)

  for wrapper in wrappers:
    func = wrapper(func)
  return func


if __name__ == "__main__":
  # Module CLI Entry Point
  # python -m <module-name> [options...]
  wrap_func(main, (persistence_mode, handle_shutdown, handle_errors))()
