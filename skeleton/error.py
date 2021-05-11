# coding=utf8
"""error.py

Module Exception Definitions
"""
from __future__ import absolute_import, print_function, unicode_literals

__all__ = (
    "BaseError",
    "ImportStringError",
    "PathNotFound"
)


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

  Keyword Args:
    fmt (str): Error Message Format String
    msg (str): The descriptive message associated with the error.

  References:
    https://github.com/boto/botocore/blob/develop/botocore/exceptions.py
  """
  fmt = "an unexpected error occurred: {error}"

  def __init__(self, **kwargs):
    msg = self.fmt.format(**kwargs)
    Exception.__init__(self, msg)
    self.kwargs = kwargs

  def __reduce__(self):
    return _err_from_packed_args, (self.__class__, None, self.kwargs)

  def __dict__(self):
    return self.json

  @property
  def msg(self):
    """Return exception message.

    Returns:
      str: Exception message.
    """
    return self.args[0]

  @property
  def json(self):
    """Return exception as json.

    Returns:
      dict: Exception as JSON
    """
    return {"message": self.msg, "type": type(self).__name__}


class ImportStringError(BaseError):
  """Import String Exception.
  """
  fmt = (
      "import_string() failed for {import_name}. possible reasons are:\n\n"
      "- missing __init__.py in a package;\n"
      "- package or module path not included in sys.path;\n"
      "- duplicated package or module name taking precedence in "
      "sys.path;\n"
      "- missing module, class, function or variable;\n\n"
      "debugged import:\n\n{exception_name}\n\n"
      "original exception:\n\n{exception}"
  )

  def __init__(self, import_name, exception):
    self.import_name = import_name
    self.exception = exception
    BaseError.__init__(
        self,
        import_name=import_name,
        exception_name=exception.__class__.__name__,
        exception=exception
    )


class PathNotFound(BaseError):
  """Exception raised for errors in the input salary.

  Attributes:
    ancestor: input salary which caused the error
    dirname: explanation of the error
  """
  fmt = "unable to find ancestor {ancestor} in {dirname}"

  def __init__(self, ancestor, dirname):
    self.ancestor = ancestor
    self.dirname = dirname
    BaseError.__init__(self, ancestor=self.ancestor, dirname=self.dirname)
