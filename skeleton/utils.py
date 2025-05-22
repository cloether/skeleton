# coding=utf8
"""utils.py

Generic Utilities
"""
from __future__ import absolute_import, print_function, unicode_literals

import os
import pickle
import re
import sys
import zlib
from base64 import b64decode
from contextlib import contextmanager
from datetime import timedelta
from errno import EEXIST
from io import UnsupportedOperation
from itertools import groupby, islice
from math import ceil
from operator import itemgetter
from string import Formatter

from six import integer_types, iteritems, string_types, text_type
from six.moves import filter, map

from .const import DEFAULT_CHUNK_SIZE, EPOCH
from .error import PathNotFound

__all__ = (
  "advance",
  "apply_values",
  "as_bool",
  "as_number",
  "chunk",
  "chunkify",
  "compress_file",
  "cwd",
  "DateRange",
  "get_file_size",
  "group_continuous",
  "isatty",
  "is_file_newer_than_file",
  "iterchunk",
  "make_executable",
  "memoize",
  "mkdir_p",
  "run_in_separate_process",
  "safe_b64decode",
  "script_dir",
  "strtobool",
  "timedelta_isoformat",
  "TIMEDELTA_ZERO",
  "timestamp_from_datetime",
  "to_valid_filename",
  "to_valid_module_name",
  "touch",
  "typename"
)


def typename(obj):
  """Return the name of the type for the provided object.

  Args:
    obj: Object to retrieve type name for.

  Returns:
    str: Name of the type for the provided object
  """
  return type(obj).__name__


def make_executable(path):
  """Make file executable.

  Args:
    path (str): Path to file.

  References:
    https://stackoverflow.com/a/30463972
  """
  mode = os.stat(path).st_mode
  # copy R bits to X
  mode |= (mode & 0o444) >> 2
  os.chmod(path, mode)


def safe_b64decode(data):
  """Incoming base64-encoded data is not always padded to a
  multiple of 4.

  Notes:
    Python's parser is stricter and requires padding, so we
    add padding if it's needed.

  Args:
    data (str or bytes): Data to base64 encode

  Returns:
    bytes: Base64 encoded data.
  """
  overflow = len(data) % 4
  if overflow:
    data += (
              "="
              if isinstance(data, string_types)
              else b"="
            ) * (4 - overflow)
  return b64decode(data)


def _parse_fmt_str(value):
  # (literal_text, field_name, fmt_spec, conversion) = f.parse(value)
  return Formatter().parse(value)


def _format_str_vars(value):
  parsed = (p[1] for p in _parse_fmt_str(value))
  return list(map(as_number, filter(None, parsed)))


# conversion

def strtobool(value, strict_errors=True):
  """Convert a string representation of truth to true (1) or
  false (0).

  Args:
    value (str or int): String to convert.
    strict_errors (bool): Raise error if val is not one the
      valid boolean values, otherwise return the input val.

  Notes:
    True Values:  "y", "yes", "t", "true", "on", and "1"
    False Values: "n", "no", "f", "false", "off", and "0"

  Raises:
    ValueError: If "val" is anything else.
  """
  value_copy = value
  if not isinstance(value_copy, string_types):
    value_copy = text_type(value_copy)
  value_copy = value_copy.lower()
  if value_copy in ("y", "yes", "t", "true", "on", "1"):
    return True
  if value_copy in ("n", "no", "f", "false", "off", "0"):
    return False
  if strict_errors:
    raise ValueError("invalid truth value: {!r}".format(value))
  return value


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
  """A context manager for operating in a different
  directory.
  """
  orig = os.getcwd()
  os.chdir(dirname)
  try:
    yield orig
  finally:
    os.chdir(orig)


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

  def _getmtime(filepath):
    try:
      return os.path.getmtime(filepath)
    except os.error:
      return 0

  return _getmtime(file_a) >= _getmtime(file_b)


def memoize(func, cls=dict):
  """Decorator to memoize.
  """
  memory = cls() if callable(cls) else cls

  def _inner(*args, **kwargs):
    full_args = args + tuple(iteritems(kwargs))
    if full_args not in memory:
      memory[full_args] = func(*args, **kwargs)
    return memory[full_args]

  return _inner


# pylint: disable=inconsistent-return-statements
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
    with os.fdopen(read_fd, "rb") as fd:
      status, result = pickle.load(fd)

    # wait for completion of child process.
    os.waitpid(pid, 0)

    if status == 0:
      return result

    raise result

  os.close(read_fd)  # close read file descriptor

  try:
    # call the function. status: success=0 fail=1
    result, status = func(*args, **kwargs), 0
  except Exception as e:  # pylint: disable=broad-except
    result, status = e, 1

  with os.fdopen(write_fd, "wb") as fd:
    try:  # dump results.
      pickle.dump(
        (status, result),
        fd,
        pickle.HIGHEST_PROTOCOL
      )
    except pickle.PicklingError as e:
      pickle.dump(
        (2, e),
        fd,
        pickle.HIGHEST_PROTOCOL
      )

  os._exit(0)  # noqa


def script_dir():
  """Get the full path to the directory containing the
  current script.
  """
  script_filename = os.path.abspath(sys.argv[0])
  return os.path.dirname(script_filename)


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


def mkdir_p(path):
  """Create entire filepath.

  Notes:
    Unix "mkdir -p" equivalent.

  Args:
    path (str): Filepath to create.

  Raises:
    OSError: Raised for exceptions unrelated to the
      directory already existing.
  """
  try:
    os.makedirs(path)
  except OSError as exc:
    if exc.errno != EEXIST:
      raise


def touch(filepath):
  """Equivalent of Unix `touch` command.

  Args:
    filepath (str): Path to file to create.
  """
  if not os.path.exists(filepath):
    with open(filepath, "a"):
      os.utime(filepath, None)


def isatty(fd=None):
  """Check if file descriptor is connected to a terminal.

  Args:
    fd (io.IO or int): File descriptor or file-like object.

  Returns:
    bool: True if file descriptor is connected to a terminal,
      otherwise False.
  """
  if fd is None:
    fd = sys.stdout
  if hasattr(fd, "fileno"):
    fd = fd.fileno()
  # noinspection PyBroadException
  try:
    return os.isatty(fd)
  except Exception:  # pylint: disable=broad-except
    return False


# file

def fpchunk(fp, chunksize=None):
  """Read the file and yield chunks of `chunk_size` bytes.

  Args:
    fp (io.FileIO): File-like object.
    chunksize (int): Byte size (default: `const.DEFAULT_CHUNK_SIZE`)

  Yields:
    bytes: Chunk of bytes.
  """
  try:
    fp.seek(0)  # beginning of file
  except (AttributeError, UnsupportedOperation):
    pass
  chunksize = chunksize or DEFAULT_CHUNK_SIZE
  while True:
    data = fp.read(chunksize)
    if not data:
      break
    yield data


def compress_file(fp, level=6):
  """Compress file.

  Args:
    fp (io.FileIO): File
    level (int): The compression level (an integer in the
      range 0-9 or -1; default is currently equivalent to 6).
      Higher compression levels are slower, but produce
      smaller results.

  Returns:
    (tuple of bytes,bytes): Compressed chunks and uncompressed chunked.
  """
  # pylint: disable=c-extension-no-member
  compressor = zlib.compressobj(level)
  z_chunks, chunks = [], []
  for _chunk in fpchunk(fp, 512):
    chunks.append(_chunk)
    z_chunks.append(compressor.compress(_chunk))
  return b"".join(z_chunks) + compressor.flush(), b"".join(chunks)


def get_file_size(path):
  """Get a files size in bytes.

  Args:
    path (str): Path to file.

  Returns:
    int: Size of the specified file (int bytes).
  """
  stats = os.lstat(path)
  return stats.st_size


# iterable


def advance(n, iterator):
  """Advances an iterator n places.
  """
  next(islice(iterator, n, n), None)
  return iterator


def apply_values(func, mapping):
  # noinspection LongLine
  """Applies ``function`` to a sequence containing all the values
  in the provided mapping, returning a new mapping with the values
  replaced with the results of the provided function.

  Examples:
    def _format(value):
      return '{0} fish'.format(value)

    print(apply_values(_format, {1: 'red', 2: 'blue'}))
    # -> {1: 'red fish', 2: 'blue fish'}

  Args:
    func (callable): Callable to apply values to.
    mapping (dict): Map object.

  Returns:
    dict: New mapping with the values replaced with the results
      of the provided function.

  References:
    https://github.com/getsentry/sentry/blob/master/src/sentry/utils/functional.py#L19
  """
  if not mapping:
    return {}
  keys, values = zip(*iteritems(mapping))
  return dict(zip(keys, func(values)))


def chunk(iterable, size):
  """Splits an iterable into batches of the specified size.

  Notes:
    Consumes entire iterable into memory before iterating
    through it.

  Args:
    iterable (Iterable): Iterable of data.
    size (int): Chunk size.

  Yields:
    list: Chunk of data from iterable.
  """
  for i in range(0, len(iterable), size):
    yield iterable[i:i + size]


def iterchunk(iterable, size):
  """Splits an iterable into chunks of size chunksize.

  Notes:
    Handles types: generator, set, map, etc...

  Args:
    iterable (Iterable): Iterable of data.
    size (int): Chunk size.

  Yields:
    list: Chunk of data from iterable.
  """
  result = []
  for i in iterable:
    result.append(i)
    if len(result) == size:
      yield result
      result = []
  # TODO: if the length of the last chunk does not
  #   equal the provided size, then fill (append to)
  #   chunk until its length is equal to size.
  if result:
    # handle last chunk
    yield result


# TODO: add option to fill the last chunk to the specified size.
def chunkify(iterable, size):
  """Splits an iterable into chunks of size chunksize.

  Notes:
    The last chunk may be smaller than the provided chunksize.

  Args:
    iterable (Iterable): Iterable of data.
    size (int): Chunk size.

  Yields:
    list: Chunk of data from iterable.
  """
  if size <= 0:
    raise ValueError("non-positive chunk size: {0}".format(size))
  return (
    chunk
    if hasattr(iterable, '__getitem__')
    # generator, set, map, etc...
    else iterchunk
  )(iterable, size)


def group_continuous(iterable, key=None, start=0):
  """Group continuous entries in an iterable.

  Examples:
    >> list(group_continuous([1, 2, 4, 5, 7, 8, 10]))
    [[1, 2], [4, 5], [7, 8], [10]]

    >> list(group_continuous(range(5)))
    [[0, 1, 2, 3, 4]]
  """
  if key is None:
    def key(value):
      """noop key function.
      """
      return value

  def grouper(i, value):
    """grouper function.
    """
    return i - key(value)

  # pylint: disable=unused-variable
  for _, group in groupby(enumerate(iterable, start), grouper):
    yield map(itemgetter(1), group)


# datetime


def timestamp_from_datetime(dt, epoch=EPOCH):
  """Convert a datetime to a timestamp.

  References:
    https://stackoverflow.com/a/8778548/141395

  Args:
    dt (datetime.datetime or datetime.date): Datetime.
    epoch (datetime.datetime or datetime.date): Epoch Datetime.

  Returns:
    int: Timestamp
  """
  delta = dt - epoch
  return delta.seconds + delta.days * 86400


def timedelta_isoformat(td):
  """ISO-8601 encoding for timedelta.

  Args:
    td (datetime.timedelta): Timedelta to convert.

  Returns:
    str: ISO formatted timedelta.
  """
  minutes, seconds = divmod(td.seconds, 60)
  hours, minutes = divmod(minutes, 60)
  return (
    'P{td.days}DT'
    '{hours:d}H'
    '{minutes:d}M'
    '{seconds:d}'
    '.{td.microseconds:06d}S'.format(
      td=td,
      hours=hours,
      minutes=minutes,
      seconds=seconds
    )
  )


# noinspection PyArgumentEqualDefault
TIMEDELTA_ZERO = timedelta(0)


class DateRange(object):  # pylint: disable=useless-object-inheritance
  """Creates a lazy range of date or datetime objects.

  Modeled after the Python 3 range type and has fast path
  membership checking, lazy iteration, indexing and slicing.

  Unlike range, DateRange allows an open-ended range. Also
  unlike range, it does not have an implicit step, so it must be
  provided.

  Args:
    start (datetime.datetime or datetime.date): Range Start Time.
    stop (datetime.datetime or datetime.date): Range End Time.
    step (datetime.timedelta): Range Step Time.

  Examples:
    > now = datetime.now().date()
    > one_day = timedelta(days=1)
    > one_week_ago = now - timedelta(weeks=1)
    > for d in DateRange(start=one_week_ago, stop=now, step=one_day):
    >> print(d)
  """

  def __init__(self, start=None, stop=None, step=None):
    if start is None:
      raise TypeError("must provide starting point for DateRange")
    if step is None:
      raise TypeError("must provide step for DateRange")
    # noinspection PyArgumentEqualDefault
    if step == timedelta(0):
      raise TypeError("must provide non-zero step for DateRange")
    self.start = start
    self.stop = stop
    self.step = step
    self._has_neg_step = self.step < TIMEDELTA_ZERO

  def __repr__(self):
    return "{!s}(start={!r}, stop={!r}, step={!r}".format(
      self.__class__.__name__,
      self.start,
      self.stop,
      self.step
    )

  def __reversed__(self):
    if self.stop:
      # pylint: disable=invalid-unary-operand-type
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

  def __contains__(self, value):
    if self.stop is not None:
      check = (
        self.start >= value > self.stop
        if self._has_neg_step
        else self.start <= value < self.stop
      )
    else:
      check = self.start >= value if self._has_neg_step else self.start <= value
    if not check:
      return False
    difference = value - self.start
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
    if isinstance(idx_or_slice, slice):
      return self._getslice(idx_or_slice)
    raise TypeError(
      "DateRange indices must be integers or slices not {0}".format(
        idx_or_slice.__class__
      )
    )

  def _getidx(self, idx):
    if not self.stop and idx < 0:
      raise IndexError("Cannot negative index infinite range")
    if self.stop and abs(idx) > len(self) - 1:
      raise IndexError("DateRange index out of range")
    if idx == 0:
      return self.start
    if idx < 0:
      idx += len(self)
    return self.start + (self.step * idx)

  def _getslice(self, slice_):
    sss = slice_.start, slice_.stop, slice_.step
    # if s == (None, None, None) or s == (None, None, 1):
    if sss in [(None, None, None), (None, None, 1)]:
      return DateRange(start=self.start, stop=self.stop, step=self.step)
    start, stop, step = sss
    # seems redundant but we are converting None -> 0
    start = start or 0
    stop = stop or 0
    step = step or 1  # use 1 here because of multiplication
    if not self.stop and (start < 0 or stop < 0):
      raise IndexError("cannot negative index infinite range")
    new_step = self.step * step
    new_start = self.start if not start else self[start]
    new_stop = self.stop if not stop else self[stop]
    return DateRange(start=new_start, stop=new_stop, step=new_step)
