# coding=utf8
"""utils.py

Generic Utilities
"""
from __future__ import absolute_import, print_function, unicode_literals

import os
import pickle
import re
from contextlib import contextmanager
from datetime import datetime
from errno import EEXIST

from six import string_types

__all__ = (
    "as_number",
    "EPOCH",
    "mkdir_p",
    "run_in_separate_process",
    "timestamp_from_datetime",
    "to_valid_filename",
    "to_valid_module_name"
)

EPOCH = datetime(1970, 1, 1)


def as_number(value):
  """Coerced value to number.

  Args:
    value: Value to coerce to number

  Returns:
    int: Value coerced to number
  """
  if isinstance(value, string_types):
    if value.isdecimal():
      value = float(value)
    elif value.isdigit():
      value = int(value)
  if isinstance(value, float):
    value = int(value)
  return value


def mkdir_p(path):
  """Unix mkdir equivalent.

  Args:
    path (str): Filepath.

  Raises:
    OSError: Raised for exceptions unrelated to directory
      already existing.
  """
  try:
    os.makedirs(path)
  except OSError as exc:
    if not (exc.errno == EEXIST and os.path.isdir(path)):
      raise


@contextmanager
def cwd(dirname):
  """A context manager for operating in a different directory.
  """
  orig = os.getcwd()
  os.chdir(dirname)
  try:
    yield orig
  finally:
    os.chdir(orig)


def run_in_separate_process(func, *args, **kwargs):
  """Run function in a separate_process.

  Args:
    func (Callable): Function to invoked.

  Returns:
    return value of the invoked function
  """
  # Create a pipe.
  read_fd, write_fd = os.pipe()

  # Fork a child process.
  pid = os.fork()

  if pid > 0:  # in child process

    # Close write file descriptor.
    os.close(write_fd)

    # Open read file descriptor.
    with os.fdopen(read_fd, 'rb') as f:
      status, result = pickle.load(f)

    # Wait for completion of child process.
    os.waitpid(pid, 0)

    if status == 0:
      return result

    raise result
  else:
    # close read file descriptor
    os.close(read_fd)

    try:
      # call the function. Success=0, Fail=1
      result, status = func(*args, **kwargs), 0
    except Exception as exc:
      result, status = exc, 1

    with os.fdopen(write_fd, 'wb') as f:
      # dump results.
      try:
        pickle.dump((status, result), f, pickle.HIGHEST_PROTOCOL)
      except pickle.PicklingError as exc:
        pickle.dump((2, exc), f, pickle.HIGHEST_PROTOCOL)

    # noinspection PyProtectedMember,PyUnresolvedReferences
    os._exit(0)


def timestamp_from_datetime(dt, epoch=EPOCH):
  """Convert a datetime to a timestamp.

  References:
    https://stackoverflow.com/a/8778548/141395

  Args:
    dt (datetime): Datetime.
    epoch (datetime): Epoch Datetime.

  Returns:
    int: Timestamp
  """
  delta = dt - epoch
  return delta.seconds + delta.days * 86400


def to_valid_filename(filename):
  # noinspection LongLine
  """Given any string, return a valid filename.

  For this purpose, filenames are expected to be all lower-cased,
  and we err on the side of being more restrictive with allowed characters,
  including not allowing space.

  References:
    https://github.com/googleapis/gapic-generator-python/blob/master/gapic/utils/filename.py

  Args:
    filename (str): The input filename.

  Returns:
    str: A valid filename.
  """
  return re.sub(r'[^a-z0-9.$_-]+', '-', filename.lower())


def to_valid_module_name(module_name):
  # noinspection LongLine
  """Given any string, return a valid Python module name.

  References:
    https://github.com/googleapis/gapic-generator-python/blob/master/gapic/utils/filename.py

  Args:
    module_name (str): The input filename

  Returns:
    str: A valid module name. Extensions (e.g. *.py), if present,
      are untouched.
  """
  return to_valid_filename(module_name).replace('-', '_')
