# coding=utf8
"""error.py

Module Exception Definitions.
"""
from __future__ import absolute_import, print_function, unicode_literals

from typing import Any, Callable, Dict, Optional, Tuple, Type, TypeVar

__all__ = (
  "BaseError",
  "ImportStringError",
  "PathNotFound"
)

T = TypeVar("T", bound=BaseException)


def _err_from_packed_args(
    exception_cls: Type[T],
    args: Optional[Tuple[Any, ...]] = None,
    kwargs: Optional[Dict[str, Any]] = None
) -> T:
  """This is helpful for reducing Exceptions that only accept kwargs as
  only positional arguments can be provided for __reduce__.

  Ideally, this would also be a class method on the BaseError but instance
  methods cannot be pickled.

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
    msg (str): Descriptive message associated with the error.
    json (dict): Exception in JSON Format.
  """
  fmt: str = "unexpected error occurred: {error}"
  kwargs: Dict[str, Any]

  def __init__(self, **kwargs: Any) -> None:
    msg = self.fmt.format(**kwargs)
    super().__init__(msg)
    self.kwargs = kwargs

  def __reduce__(self) -> Tuple[Callable[..., T], Tuple[Type[T], None, Dict[str, Any]]]:
    return _err_from_packed_args, (self.__class__, None, self.kwargs)

  def __dict__(self) -> Dict[str, Any]:
    return self.json

  @property
  def msg(self) -> str:
    """Return the exception message."""
    return self.args[0]

  @property
  def json(self) -> Dict[str, str]:
    """Return the exception in JSON format."""
    return {"message": self.msg, "type": type(self).__name__}


class ImportStringError(BaseError):
  """Import String Exception.
  """
  fmt: str = (
    "import_string() failed for {import_name}. possible reasons are:\n\n"
    "- missing __init__.py in a package;\n"
    "- package or module path not included in sys.path;\n"
    "- duplicated package or module name taking precedence in "
    "sys.path;\n"
    "- missing module, class, function or variable;\n\n"
    "debugged import:\n\n{exception_name}\n\n"
    "original exception:\n\n{exception}"
  )
  import_name: str
  exception: Exception

  def __init__(self, import_name: str, exception: Exception) -> None:
    self.import_name = import_name
    self.exception = exception
    super().__init__(
      import_name=import_name,
      exception_name=exception.__class__.__name__,
      exception=exception
    )


class PathNotFound(BaseError):
  """Exception raised for missing ancestors in a path.

  Attributes:
    ancestor: input path component which could not be found
    dirname: containing directory where lookup failed
  """
  fmt: str = "unable to find ancestor {ancestor} in {dirname}"
  ancestor: str
  dirname: str

  def __init__(self, ancestor: str, dirname: str) -> None:
    self.ancestor = ancestor
    self.dirname = dirname
    super().__init__(ancestor=self.ancestor, dirname=self.dirname)
