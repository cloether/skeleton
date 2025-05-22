# coding=utf8
"""__main__.py

Module CLI Entry Point.

Usage:
  python3 -m <module-name> [options...]
"""
from __future__ import absolute_import, print_function, unicode_literals

import errno
import os
import sys

from .cli import main

# force absolute path when running on python 2.
# https://github.com/microsoft/debugpy/blob/master/src/debugpy/__main__.py
__file__ = os.path.abspath(__file__)  # noqa


def epipe(func):
  """Decorator to Handle EPIPE Errors.

  Args:
    func (callable): Function to decorate.

  Returns:
    callable: Decorated function.

  Raises:
    IOError: Raised when non-EPIPE exceptions are encountered.
  """

  def _inner(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except IOError as e:
      if e.errno == errno.EPIPE:
        sys.exit(e.errno)
      raise

  return _inner


def handle_shutdown(func):
  """Decorator to catch shutdown signals.

  Args:
    func (callable): Function to decorate.

  Returns:
    callable: Decorated function.
  """
  import signal  # pylint: disable=import-outside-toplevel

  def _shutdown_handler(signum, frame):  # pylint: disable=unused-argument
    """Handle Shutdown.

    Args:
      signum (int): Signal Number,
      frame (types.FrameType): Interrupted Stack Frame.

    Raises:
      (SystemExit): Calls sys.exit(), which raises a SystemExit exception.
    """
    sys.stderr.write("\b\b")  # write 2 backspaces to stderr
    sys.stderr.write(
      "interrupt detected: signal={0:d} "
      "frame=\"{1:s}\"\n".format(signum, frame)
    )
    sys.exit(signum)

  def _inner(*args, **kwargs):
    signal.signal(signal.SIGTERM, _shutdown_handler)
    signal.signal(signal.SIGINT, _shutdown_handler)
    if os.name == "nt":
      # pylint: disable=no-member
      signal.signal(signal.SIGBREAK, _shutdown_handler)
    # TODO: Remove signal handlers?
    return func(*args, **kwargs)

  return _inner


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
    except Exception as e:  # pylint: disable=broad-except
      sys.stderr.write("{0!r}".format(e))
      sys.stderr.flush()
      sys.exit(1)
    else:
      sys.exit(ret)

  return _inner


def persistence_mode(func):
  """Decorator for when binary mode is required for
  persistent mode on Windows.

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
      # noinspection PyUnresolvedReferences
      import msvcrt  # pylint: disable=import-error,import-outside-toplevel

      msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)  # pylint: disable=E1101
      msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)  # pylint: disable=E1101
      msvcrt.setmode(sys.stderr.fileno(), os.O_BINARY)  # pylint: disable=E1101
      return func(*args, **kwargs)
  else:
    def _inner(*args, **kwargs):
      return func(*args, **kwargs)

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
  wrap_func(main, (persistence_mode, handle_shutdown, handle_errors))()
