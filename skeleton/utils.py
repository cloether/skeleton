# coding=utf8
"""utils.py

Generic Utilities
"""
from __future__ import absolute_import, print_function, unicode_literals

import os
import pickle
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
)

EPOCH = datetime(1970, 1, 1)


def as_number(value):
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
    else:
      raise result
  else:
    # Close read file descriptor
    os.close(read_fd)

    try:
      # Call the function.
      # - Success:  0
      # - Fail:     1
      result, status = func(*args, **kwargs), 0
    except Exception as exc:
      result, status = exc, 1

    # Dump results.
    with os.fdopen(write_fd, 'wb') as f:
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
