# coding=utf8
"""error.py

Module Exception Definitions
"""
from __future__ import absolute_import, print_function, unicode_literals

__all__ = ("BaseError",)


def _err_from_packed_args(exception_cls, args=None, kwargs=None):
  """This is helpful for reducing Exceptions that only accept kwargs as
  only positional arguments can be provided for __reduce__.

  Ideally, this would also be a class method on the BaseError but instance
  methods cannot be pickled.

  References:
    https://github.com/boto/botocore/blob/develop/botocore/exceptions.py

  Args:
    exception_cls (type): Exception class
    args (tuple): Packed exception arguments
    kwargs (dict): Packed exception keyword arguments

  Returns:
    Exception: Exception from packed arguments
  """
  if args is None:
    args = ()

  if kwargs is None:
    kwargs = {}

  return exception_cls(*args, **kwargs)


class BaseError(Exception):
  """Base Exception Class for Module.

  Attributes:
    fmt (str): Error Message Format String
    msg (str): The descriptive message associated with the error.

  References:
    https://github.com/boto/botocore/blob/develop/botocore/exceptions.py
  """
  fmt = "An unspecified error occurred: {error}"

  def __init__(self, **kwargs):
    msg = self.fmt.format(**kwargs)
    Exception.__init__(self, msg)
    self.kwargs = kwargs

  def __reduce__(self):
    return _err_from_packed_args, (self.__class__, None, self.kwargs)

  @property
  def msg(self):
    return self.args[0]
