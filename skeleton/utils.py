# coding=utf8
"""utils.py

Generic Utilities
"""
from __future__ import absolute_import, print_function, unicode_literals

import os
import pickle
import re
import sys
from contextlib import contextmanager
from datetime import datetime, timedelta
from errno import EEXIST
from math import ceil
from string import Formatter

from six import integer_types, iteritems, string_types, text_type

__all__ = (
    "as_bool",
    "as_number",
    "cwd",
    "DateRange",
    "EPOCH",
    "is_file_newer_than_file",
    "ISO_DATETIME_FORMAT",
    "ISO_DATETIME_STRING",
    "memoize",
    "mkdir_p",
    "run_in_separate_process",
    "script_dir",
    "strtobool",
    "timestamp_from_datetime",
    "to_valid_filename",
    "to_valid_module_name",
    "touch"
)

EPOCH = datetime(1970, 1, 1)

ISO_DATETIME_STRING = "1970-01-01 00:00:00.000"
ISO_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


class DateRange(object):
  """Creates a lazy range of date or datetime objects.

  Modeled after the Python 3 range type and has fast path
  membership checking, lazy iteration, indexing and slicing.

  Unlike range, DateRange allows an open ended range. Also
  unlike range, it does not have an implicit step so it must be
  provided.

  Args:
    start (datetime or date): Range Start Time.
    stop (datetime or date): Range End Time.
    step (datetime or date): Range Step Time.

  Examples:
    now = datetime.now().date()
    one_day = timedelta(days=1)
    one_week_ago = now - timedelta(weeks=1)

    for d in DateRange(start=one_week_ago, stop=now, step=one_day):
      print(d)
  """

  def __init__(self, start=None, stop=None, step=None):
    if start is None:
      raise TypeError("must provide starting point for DateRange.")
    if step is None:
      raise TypeError("must provide step for DateRange.")
    if step == timedelta(0):
      raise TypeError("must provide non-zero step for DateRange")
    self.start = start
    self.stop = stop
    self.step = step
    self._has_neg_step = self.step < timedelta(0)

  def __repr__(self):
    return "{!s}(start={!r}, stop={!r}, step={!r}".format(
        self.__class__.__name__, self.start, self.stop, self.step
    )

  def __reversed__(self):
    if self.stop:
      return DateRange(self.stop, self.start, -self.step)
    raise ValueError("cannot reverse infinite range")

  def __len__(self):
    if self.stop is None:
      # it would be nice if float("inf") could be returned
      raise TypeError("infinite range")
    calc = (
        self.start - self.stop
        if self._has_neg_step
        else self.stop - self.start
    )
    return int(ceil(abs(calc.total_seconds() / self.step.total_seconds())))

  def __contains__(self, x):
    if self.stop is not None:
      check = (self.start >= x > self.stop
               if self._has_neg_step
               else self.start <= x < self.stop)
    else:
      check = self.start >= x if self._has_neg_step else self.start <= x
    if not check:
      return False
    difference = x - self.start
    return difference.total_seconds() % self.step.total_seconds() == 0

  def _check_stop(self, current):
    if self._has_neg_step:
      return current <= self.stop
    return current >= self.stop

  def __iter__(self):
    current, stopping = self.start, self.stop is not None
    while True:
      if stopping and self._check_stop(current):
        break
      yield current
      current += self.step

  def __eq__(self, other):
    if isinstance(other, DateRange):
      return (
          self.start == other.start
          and self.stop == other.stop
          and self.step == other.step
      )
    return NotImplemented

  def __ne__(self, other):
    if isinstance(other, DateRange):
      return not self == other
    return NotImplemented

  def __getitem__(self, idx_or_slice):
    if isinstance(idx_or_slice, int):
      return self._getidx(idx_or_slice)
    elif isinstance(idx_or_slice, slice):
      return self._getslice(idx_or_slice)
    raise TypeError(
        "DateRange indices must be integers or slices not {0}".format(
            idx_or_slice.__class__
        )
    )

  def _getidx(self, idx):
    if not self.stop and 0 > idx:
      raise IndexError("Cannot negative index infinite range")
    if self.stop and abs(idx) > len(self) - 1:
      raise IndexError("DateRange index out of range")
    if idx == 0:
      return self.start
    elif 0 > idx:
      idx += len(self)
    return self.start + (self.step * idx)

  def _getslice(self, slice_):
    s = slice_.start, slice_.stop, slice_.step
    if s == (None, None, None) or s == (None, None, 1):
      return DateRange(start=self.start, stop=self.stop, step=self.step)
    start, stop, step = s
    # seems redundant but we are converting None -> 0
    start = start or 0
    stop = stop or 0
    step = step or 1  # use 1 here because of multiplication
    if not self.stop and (0 > start or 0 > stop):
      raise IndexError("cannot negative index infinite range")
    new_step = self.step * step
    new_start = self.start if not start else self[start]
    new_stop = self.stop if not stop else self[stop]
    return DateRange(start=new_start, stop=new_stop, step=new_step)


def _parse_fmt_str(s):
  return [
      (literal_text, field_name, fmt_spec, conversion)
      for literal_text, field_name, fmt_spec, conversion in
      Formatter().parse(s)
  ]


def _format_str_vars(s):
  return list(map(as_number, filter(None, (p[1] for p in _parse_fmt_str(s)))))


def as_number(value):
  """Coerced value to number.

  Args:
    value (str or int or float): Value to coerce to number.

  Returns:
    int: Value coerced to number.
  """
  if isinstance(value, integer_types):
    return value
  if isinstance(value, string_types):
    if value.isnumeric():
      value = int(value)
    elif value.isdecimal():
      value = float(value)
    elif value.isdigit():
      value = int(value)
  return value


def as_bool(value):
  """Coerced value to boolean.

  Args:
    value (str or int or bool): Value to coerce to boolean.

  Returns:
    int: Value coerced to boolean.
  """
  if isinstance(value, bool):
    return value
  value = as_number(value)
  return strtobool(value, strict_errors=False)


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


class PathNotFound(Exception):
  """Exception raised for errors in the input salary.

  Attributes:
    ancestor: input salary which caused the error
    dirname: explanation of the error
  """

  def __init__(self, ancestor, dirname):
    self.ancestor = ancestor
    self.dirname = dirname
    Exception.__init__(self.ancestor, self.dirname)

  def __str__(self):
    return "Unable to find ancestor {0} in {1}".format(
        self.ancestor, self.dirname
    )


def find_ancestor(start_dir, ancestor):
  """Finds an ancestor dir in a path.

  For example, find_ancestor("c:\foo\bar\baz", "bar") would
  return "c:\foo\bar".

  Unlike FindUpward*, this only looks at direct path ancestors.
  """
  start_dir = os.path.abspath(start_dir)
  path = start_dir
  while True:
    (parent, tail) = os.path.split(path)
    if tail == ancestor:
      return path
    if not tail:
      break
    path = parent
  raise PathNotFound(ancestor, start_dir)


def is_file_newer_than_file(file_a, file_b):
  """Returns True if file_a mtime is newer than file_b mtime.

  Returns:
    bool: True if file_a mtime is newer than file_b mtime.
  """

  def _getmtime(f):
    try:
      return os.path.getmtime(f)
    except os.error:
      return 0

  return _getmtime(file_a) >= _getmtime(file_b)


def memoize(fn, cls=dict):
  """Decorator to memoize.
  """
  memory = cls()

  def impl(*args, **kwargs):
    full_args = args + tuple(iteritems(kwargs))
    if full_args not in memory:
      memory[full_args] = fn(*args, **kwargs)
    return memory[full_args]

  return impl


def mkdir_p(path):
  """Create entire filepath.

  Notes:
    Unix "mkdir -p" equivalent.

  Args:
    path (str): Filepath to create.

  Raises:
    OSError: Raised for exceptions unrelated to the directory
      already existing.
  """
  try:
    os.makedirs(path)
  except OSError as exc:
    if exc.errno != EEXIST:
      raise


def run_in_separate_process(func, *args, **kwargs):
  """Run function in a separate_process.

  Args:
    func (Callable): Function to invoked.

  Returns:
    return value of the invoked function
  """
  # create a pipe.
  read_fd, write_fd = os.pipe()

  # fork a child process.
  pid = os.fork()

  if pid > 0:  # in child process
    # close write file descriptor.
    os.close(write_fd)

    # open read file descriptor.
    with os.fdopen(read_fd, "rb") as f:
      status, result = pickle.load(f)

    # wait for completion of child process.
    os.waitpid(pid, 0)

    if status == 0:
      return result

    raise result
  else:
    # close read file descriptor
    os.close(read_fd)

    try:
      # call the function.
      # status: success=0 fail=1
      result, status = func(*args, **kwargs), 0
    except Exception as exc:
      result, status = exc, 1

    with os.fdopen(write_fd, "wb") as f:
      # dump results.
      try:
        pickle.dump((status, result), f, pickle.HIGHEST_PROTOCOL)
      except pickle.PicklingError as exc:
        pickle.dump((2, exc), f, pickle.HIGHEST_PROTOCOL)

    os._exit(0)  # noqa


def script_dir():
  """Get the full path to the directory containing the current script.
  """
  script_filename = os.path.abspath(sys.argv[0])
  return os.path.dirname(script_filename)


def strtobool(val, strict_errors=True):
  """Convert a string representation of truth to true (1) or
  false (0).

  Args:
    val (str or int): String to convert.
    strict_errors (bool): Raise error if val is not one the
      valid boolean values, otherwise return the input val.

  Notes:
    True Values:  "y", "yes", "t", "true", "on", and "1"
    False Values: "n", "no", "f", "false", "off", and "0"

  Raises:
    ValueError: If "val" is anything else.
  """
  v = val
  if not isinstance(v, string_types):
    v = text_type(v)
  if v.lower() in ("y", "yes", "t", "true", "on", "1"):
    return True
  elif v.lower() in ("n", "no", "f", "false", "off", "0"):
    return False
  elif strict_errors:
    raise ValueError("invalid truth value {!r}".format(val))
  else:
    return val


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
  """Given any string, return a valid filename.

  For this purpose, filenames are expected to be all
  lower-cased, and we err on the side of being more
  restrictive with allowed characters, including not
  allowing space.

  Args:
    filename (str): The input filename.

  Returns:
    str: A valid filename.
  """
  return re.compile(r"[^a-z0-9.$_-]+").sub("-", filename.lower())


def to_valid_module_name(module_name):
  """Given any string return a valid Python module name.

  Args:
    module_name (str): Input filename.

  Notes:
    File extensions if present are untouched.

  Returns:
    (str): A valid module name.
  """
  return to_valid_filename(module_name).replace("-", "_")


def touch(filepath):
  """Equivalent of Unix `touch` command
  """
  if not os.path.exists(filepath):
    fh = open(filepath, "a")
    try:
      os.utime(filepath, None)
    finally:
      fh.close()
