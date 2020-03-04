#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""utils.py

General Utilities.
"""
import os
import pickle
from datetime import datetime
from errno import EEXIST

from six import binary_type


def timestamp_from_dt(dt, epoch=datetime(1970, 1, 1)):
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


def as_text(text_or_bytes):
  """Return value as text.

  Args:
    text_or_bytes (str or bytes): Text or Bytes

  Returns:
    str: Text Value.
  """
  if isinstance(text_or_bytes, binary_type):
    return text_or_bytes.decode('utf8')
  return text_or_bytes


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


def run_in_separate_process(func, *args, **kwargs):
  """Run function in a separate_process.

  Args:
    func (Callable): Function to invoked.

  Returns:
    return value of the invoked function
  """
  read_fd, write_fd = os.pipe()  # Create a pipe.
  pid = os.fork()  # Fork a child process.
  if pid > 0:  # in child process
    os.close(write_fd)  # Close write file descriptor.
    with os.fdopen(read_fd, 'rb') as f:  # Open read file descriptor.
      status, result = pickle.load(f)
    os.waitpid(pid, 0)  # Wait for completion of child process.
    if status == 0:
      return result
    else:
      raise result
  else:
    os.close(read_fd)  # Close read file descriptor.
    try:
      # Call the function.
      result = func(*args, **kwargs)
      status = 0  # Success
    except Exception as exc:
      result = exc
      status = 1  # Fail
    with os.fdopen(write_fd, 'wb') as f:  # Dump results.
      try:
        pickle.dump((status, result), f, pickle.HIGHEST_PROTOCOL)
      except pickle.PicklingError as exc:
        pickle.dump((2, exc), f, pickle.HIGHEST_PROTOCOL)
    # noinspection PyProtectedMember
    os._exit(0)
