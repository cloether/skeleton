#!/usr/bin/env python
# coding=utf8
"""List Python files that are missing a coding directive.
"""
from __future__ import absolute_import, print_function, unicode_literals

import errno
import logging
import os
import re
import sys
from operator import itemgetter

from six import ensure_str, text_type

__version__ = "0.0.2"

LOGGER = logging.getLogger(__name__)

BINARY_RE = re.compile(br'[\x00-\x08\x0E-\x1F\x7F]')
BLANK_RE = re.compile(rb'^[ \t\f]*(?:[#\r\n]|$)')
DECL_RE = re.compile(rb'^[ \t\f]*#.*?coding[:=][ \t]*([-\w.]+)')  # noqa

if sys.platform == "Win32":
  # Binary mode is required for persistent mode on windows.
  # sys.stdout in Python is by default opened in text mode,
  # and writes to this stdout produce corrupted binary data
  # on Windows.
  #   python -c "import sys; sys.stdout.write('_\n_')" > file
  #   python -c "print(repr(open('file', 'rb').read()))"
  import msvcrt  # noqa

  msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
  msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
  msvcrt.setmode(sys.stderr.fileno(), os.O_BINARY)


def get_declaration(line):
  """Get encoding declaration from line.
  """
  match = DECL_RE.match(line)
  if match:
    return match.group(1)
  return b''


def has_python_ext(filepath):
  """Check if filepath has a python extension.
  """
  return filepath.endswith((".py", ".pyw"))


def _open(filepath):
  try:
    size = os.stat(filepath).st_size
  except OSError as err:
    # Permission denied - ignore the file
    LOGGER.debug("permission denied: %s. %r", filepath, err)
    return None

  if size > 1024 * 1024:  # too big
    LOGGER.debug("file too large (%d bytes): %s", size, filepath)
    return None

  try:
    return open(filepath, "rb")
  except IOError as err:
    # Access denied, or a special file - ignore it
    LOGGER.debug("access denied: %s. %r", filepath, err)
    return None


def can_be_compiled(filepath):
  """Check if file at filepath can be compiled.
  """
  infile = _open(filepath)
  if infile is None:
    return False

  with infile:
    code = infile.read()

  try:
    compile(code, filepath, "exec")
  except Exception:  # noqa
    return False

  return True


def looks_like_python(filepath):
  """Check if file at filepath looks like a python file.
  """
  infile = _open(filepath)
  if infile is None:
    return False

  with infile:
    line = infile.readline()

  if BINARY_RE.search(line):
    # file appears to be binary
    return False

  if has_python_ext(filepath):
    return True

  # disguised Python script (e.g. CGI)
  return b"python" in line


def has_correct_encoding(text, codec):
  """Check if text match the provided codec.
  """
  try:
    text_type(text, codec)
  except UnicodeDecodeError:
    return False
  else:
    return True


def needs_declaration(filepath):
  """Check if file at filepath needs a declaration.
  """
  try:
    infile = open(filepath, 'rb')
  except IOError:
    # oops, the file was removed - ignore it
    return None

  with infile:
    line1 = infile.readline()
    line2 = infile.readline()

    if (
        get_declaration(line1)
        or BLANK_RE.match(line1)
        and get_declaration(line2)
    ):
      # the file does have an encoding declaration, so trust it
      return False

    # check the whole file for non utf-8 characters
    rest = infile.read()
  return has_correct_encoding(line1 + line2 + rest, "utf8")


def walk_python_files(paths, is_python=looks_like_python, exclude_dirs=None):
  """Recursively yield all Python source files below the given
  paths.

  Args:
    paths (list): list of files and/or directories to be
      checked.
    is_python (Callable): function that takes a file name and
      checks whether it is a python source file.
    exclude_dirs (list or str): list of directory base names
      that should be excluded in the search.
  """
  if exclude_dirs is None:
    exclude_dirs = []

  for path in map(os.path.abspath, paths):
    if os.path.isfile(path):
      if is_python(path):
        yield path
    elif os.path.isdir(path):
      for dirpath, dirnames, filenames in os.walk(path):
        for exclude in exclude_dirs:
          if exclude in dirnames:
            LOGGER.debug("excluded directory: %s",
                         os.path.join(dirpath, exclude))
            dirnames.remove(exclude)
        for filename in filenames:
          fullpath = os.path.join(dirpath, filename)
          if is_python(fullpath):
            yield fullpath
    else:
      LOGGER.debug("unknown: %s", path)


def iter_check_decl(paths, is_python_func, exclude):
  for filepath in walk_python_files(paths, is_python_func, exclude):
    LOGGER.debug("python-file: %s", filepath)
    yield filepath, needs_declaration(filepath)


def find_no_encoding(paths, try_compile=False, exclude=None):
  """Find python files with a missing encoding declaration.

  Args:
    paths (list of str): search paths.
    try_compile (bool): recognize python files by trying to compile.
    exclude (list of str): directories to exclude while searching.
  """
  is_python = looks_like_python if not try_compile else can_be_compiled

  decl_checks = iter_check_decl(paths, is_python, exclude)

  def _filter_ok(results):
    LOGGER.debug("%s: %s", "missing-decl" if results[1] else "ok", results[0])
    return results[1]

  return map(itemgetter(0), filter(_filter_ok, decl_checks))


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


def handle_shutdown(func):
  """Decorator to various shutdown signals.
  """
  import signal

  def _shutdown_handler(signum, _):
    """Handle Shutdown.

    Args:
      signum (int): Signal Number,
      _ (types.FrameType): Interrupted Stack Frame.

    Raises:
      (SystemExit): Calls sys.exit(), which raises a SystemExit exception.
    """
    sys.stderr.write("\b\b")  # write 2 backspaces to stderr
    logging.debug("shutdown handler called: signal=%d", signum)
    sys.exit(signum)

  def _f(*args, **kwargs):
    signal.signal(signal.SIGTERM, _shutdown_handler)
    signal.signal(signal.SIGINT, _shutdown_handler)
    if os.name == 'nt':
      signal.signal(signal.SIGBREAK, _shutdown_handler)
    result = func(*args, **kwargs)
    return result

  return _f


def _parse_args():
  from argparse import ArgumentParser, RawDescriptionHelpFormatter, FileType

  # noinspection PyTypeChecker
  parser = ArgumentParser(
      prog=os.path.basename(__file__),
      description=__doc__,
      formatter_class=RawDescriptionHelpFormatter,
      epilog="""References:
    https://github.com/python/cpython/blob/master/Tools/scripts/findnocoding.py
  """
  )

  parser.add_argument(
      "paths",
      metavar="PATHS",
      nargs="+",
      help="search path(s)."
  )

  parser.add_argument(
      "-c", "--compile",
      action="store_true",
      help="recognize python files by trying to compile. (default: %(default)s)"
  )

  parser.add_argument(
      "-e", "--exclude",
      nargs="+",
      default=[".git", ".idea", "__pycache__"],
      help="directories to exclude while searching. (default: %(default)s)"
  )

  parser.add_argument(
      "-d", "--debug",
      action="store_true",
      help="enable debug logging. (default: %(default)s)"
  )

  parser.add_argument(
      "-v", "--version",
      version=__version__,
      action="version"
  )

  parser.add_argument(
      '-o', '--output',
      default="-",
      metavar="path",
      help='Output Location (default: %(default)s)',
      type=FileType("{0!s}+".format('wb' if sys.version_info[0] == 2 else "w"))
  )

  args = parser.parse_args()

  if args.debug is True:
    logging.basicConfig(level=logging.DEBUG)

  return args


@handle_shutdown
@epipe
def main():
  """Entry Point
  """
  args = _parse_args()
  write = args.output.write
  for fullpath in find_no_encoding(args.paths, args.compile, args.exclude):
    write(ensure_str("{0}\n".format(fullpath)))
  args.output.flush()
  return 0


if __name__ == '__main__':
  sys.exit(main())
