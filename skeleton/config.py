# coding=utf8
"""configf.py
"""
from __future__ import absolute_import, print_function, unicode_literals

import copy
import json
import logging
import os
from collections import OrderedDict

from six import (
  PY2,
  ensure_binary,
  iteritems,
  reraise,
  string_types,
  text_type
)

from . import __app_id__
from .const import (
  DEFAULT_MAX_POOL_CONNECTIONS,
  DEFAULT_POOLBLOCK,
  DEFAULT_POOLSIZE,
  DEFAULT_POOL_TIMEOUT,
  DEFAULT_RETRIES,
  DEFAULT_TIMEOUT,
  LOGGING_DATEFMT,
  LOGGING_FILEMODE,
  LOGGING_FILENAME,
  LOGGING_FORMAT,
  LOGGING_LEVEL,
  LOGGING_STYLE
)
from .error import ImportStringError

LOGGER = logging.getLogger(__name__)


def getenv(keys, default=None, drop_null=True):
  """Create Configuration from a environment variables.
  """
  config = {}
  for key in keys:
    value = os.getenv(key, default)
    if not value or value is None and drop_null:
      continue
    config[key] = value
  return config


def import_string(import_name, silent=False):
  """Imports an object based on a string.  This is useful if you want to
  use import paths as endpoints or something similar.  An import path can
  be specified either in dotted notation (``xml.sax.saxutils.escape``)
  or with a colon as object delimiter (``xml.sax.saxutils:escape``).

  If `silent` is True the return value will be `None` if the import fails.

  Args:
    import_name: the dotted name for the object to import.
    silent: if set to `True` import errors are ignored and
      `None` is returned instead.

  Returns:
    object: imported object
  """
  # force the import name to automatically convert to strings
  # __import__ is not able to handle unicode strings in the fromlist
  # if the module is a package
  import_name = text_type(import_name).replace(":", ".")

  try:
    try:
      __import__(import_name)
    except ImportError:
      if "." not in import_name:
        raise
    else:
      return sys.modules[import_name]

    module_name, obj_name = import_name.rsplit(".", 1)
    module = __import__(module_name, globals(), locals(), [obj_name])

    try:
      return getattr(module, obj_name)
    except AttributeError as e:
      raise ImportError(e)

  except ImportError as e:
    if not silent:
      reraise(
          tp=ImportStringError,
          value=ImportStringError(import_name, e),
          tb=sys.exc_info()[2]
      )


class ConfigAttribute(object):
  """Makes an attribute forward to the config.
  """

  def __init__(self, name, get_converter=None):
    self.__name__ = name
    self.get_converter = get_converter

  # noinspection PyShadowingBuiltins
  def __get__(self, instance, type=None):
    if instance is None:
      return self
    value = instance.config[self.__name__]
    if self.get_converter is not None:
      value = self.get_converter(value)
    return value

  def __set__(self, instance, value):
    instance.set(self.__name__, value)


class Configuration(dict):
  """Configuration Object.

  TODO:
    - Ability to specify type.
    - Default Values.
    - Read/Write Variables.
    - Configuration Sections (ex: logging, http, etc...)
  """
  # defaults
  OPTIONS = OrderedDict([
      ('client_cert', None),
      ('connect_timeout', DEFAULT_TIMEOUT),
      ('log_datefmt', LOGGING_DATEFMT),
      ('log_format', LOGGING_FORMAT),
      ('log_file', LOGGING_FILENAME),
      ('log_filemode', LOGGING_FILEMODE),
      ('log_level', LOGGING_LEVEL),
      ('log_style', LOGGING_STYLE),
      ('max_pool_connections', DEFAULT_MAX_POOL_CONNECTIONS),
      ('poolblock', DEFAULT_POOLBLOCK),
      ('poolsize', DEFAULT_POOLSIZE),
      ('pool_timeout', DEFAULT_POOL_TIMEOUT),
      ('proxies', None),
      ('proxies_config', None),
      ('read_timeout', DEFAULT_TIMEOUT),
      ('retries', DEFAULT_RETRIES),
      ('user_agent', __app_id__),
      ('verify', False),
  ])

  # noinspection PyMissingConstructor
  def __init__(self, *args, **kwargs):
    # record user provided options
    self._user_options = self._make_options(*args, **kwargs)
    # Merge the user_provided options onto the default options
    config_vars = copy.copy(self.OPTIONS)
    config_vars.update(self._user_options)
    # Set the attributes based on the config_vars
    dict.update(self, config_vars)

  def _make_options(self, *args, **kwargs):
    """Set configuration values.
    """
    config = {}
    keys = self.keylist()
    for key, value in iteritems(kwargs):
      if key not in self.OPTIONS:
        raise ValueError("invalid key: {0}".format(key))
      config[key] = value
    # number of args should not be longer than allowed options
    if len(args) > len(keys):
      raise TypeError('takes at most {0} arguments ({1} given)'.format(
          len(keys), len(args)
      ))
    # iterate through args passed through to the constructor
    # and map them tp their corresponding keys.
    for i, arg in enumerate(args):
      # if a kwarg was specified for the arg, then error out.
      if keys[i] in config:
        raise TypeError(
            "got multiple values for keyword argument: {0}".format(
                keys[i]
            )
        )
      config[keys[i]] = arg
    return config

  # compatibility

  if PY2:
    def items(self):
      """Dict Items.
      """
      # noinspection PyCompatibility
      return self.iteritems()

    def keys(self):
      """Dict Keys.
      """
      # noinspection PyCompatibility
      return self.iterkeys()

    def values(self):
      """Dict Values.
      """
      # noinspection PyCompatibility
      return self.itervalues()
  else:
    iteritems = dict.items
    iterkeys = dict.keys
    itervalues = dict.values

  # class methods

  @classmethod
  def from_object(cls, value):
    """Create configuration from a python object.
    """
    if isinstance(value, string_types):
      value = import_string(value)
    new = cls()
    for key in dir(value):
      if key.isupper():
        new[key] = getattr(value, key)
    return new

  @classmethod
  def from_code(cls, value):
    """Create configuration from a python file..
    """
    return cls.from_object(value)

  @classmethod
  def from_file(cls, value):
    """Create Configuration from a file.
    """
    with open(value) as f:
      content = json.load(f)
    return cls(**content)

  @classmethod
  def from_env(cls, default=None, drop_null=True):
    """Create Configuration from a environment variables.
    """
    return cls(**getenv(
        cls.OPTIONS,
        default=default,
        drop_null=drop_null
    ))

  def update_from_env(self, default=None, drop_null=True):
    """Update Configuration from environment variables.
    """
    dict.update(self, getenv(
        self.OPTIONS,
        default=default,
        drop_null=drop_null
    ))

  @classmethod
  def get_env(cls, key, default=None):
    """Create Configuration from a environment variables.
    """
    cls.validate_key(key)
    return cls(key=os.getenv(key, default))

  @classmethod
  def validate_key(cls, key, strict=True):
    """Validate configuration key.
    """
    if key not in cls.OPTIONS:
      if strict:
        raise ValueError("non-existent option: {0}".format(key))
      return False
    return True

  @classmethod
  def keylist(cls):
    """Return a list of configuration keys (options)

    Returns:
      list of str: List of configuration keys (options)
    """
    return list(cls.OPTIONS)

  # conversion

  # noinspection PyUnusedLocal
  def as_dict(self, **kwargs):
    """Return configuration as a dict.

    Returns:
      dict: Configuration dict.
    """
    return {k: v for k, v in self.items()}

  # noinspection PyUnusedLocal
  def as_list(self, **kwargs):
    """Return configuration as list of tuples.
    """
    return list(self.items())

  def as_string(self, **kwargs):
    """Return configuration as a string.

    Returns:
      str: Configuration str.
    """
    return json.dumps(self, **kwargs)

  def as_bytes(self, **kwargs):
    """Return configuration as a string.

    Returns:
      str: Configuration str.
    """
    encoding = kwargs.pop("encoding", None)
    errors = kwargs.pop("errors", None)
    return ensure_binary(self.as_string(**kwargs), encoding, errors)

  # get/set/merge

  def set(self, key, value):
    """Set configuration value.
    """
    if key not in self.OPTIONS:
      raise ValueError("non-existent option: {0}".format(key))
    dict.__setitem__(self, key, value)

  def get(self, key, default=None, strict=False):
    """Get configuration value.
    """
    if key not in self.OPTIONS:
      if strict:
        raise ValueError("non-existent option: {0}".format(key))
      return default
    return dict.__getitem__(self, key)

  def getall(self, keys, default=None, strict=False):
    """Get configuration value.
    """
    return [self.get(key, default=default, strict=strict) for key in keys]

  def merge(self, other):
    """Merge current config with another config.

    This will merge in all non-default values from the
    provided config and return a new config object.

    Args:
      other (Configuration): Configuration to merge with.

    Returns:
      Configuration: A config object built from the merged
        values of both config objects.
    """
    # copy current attributes in config object.
    config_options = copy.copy(self._user_options)
    # merge user options from other config
    config_options.update(other._user_options)
    # return new config with merged properties
    return Configuration(**config_options)

  def merge_all(self, *others, reverse=True):
    """Merge current config with other configs.

    This will merge in all non-default values from the
    provided config and return a new config object.

    Args:
      others (Configuration): Configuration to merge with.
      reverse (bool): If True, others will be reversed before
        merging, otherwise merging is done in the order the
        others are provided.

    Returns:
      Configuration: A config object built from the merged
        values of both config objects.
    """
    # copy current attributes in config object.
    config_options = copy.copy(self._user_options)
    for other in others if not reverse else reversed(others):
      config_options.update(other._user_options)
    return Configuration(**config_options)

  def dump(self, fd, **kwargs):
    """Write configuration to buffer.
    """
    end = kwargs.pop("end", None)
    json.dump(self, fd, **kwargs)
    if end and end is not None:
      fd.write(end)

  # builtin

  def __repr__(self):
    return self.as_string()

  __str__ = __repr__

  def __setitem__(self, key, value):
    self.set(key, value)

  def __getitem__(self, key, default=None, strict=False):
    return self.get(key, default=default, strict=strict)

  def __dir__(self):
    return self.keylist()


if __name__ == "__main__":
  import sys

  def _test():
    """Test Configuration.
    """
    os.environ["client_cert"] = "bbb"
    os.environ["max_pool_connections"] = "20"
    print("-" * 80)

    c = Configuration("a", proxies="B")
    cc = Configuration("b", proxies="C")
    ccc = Configuration("c", proxies="D")
    cccc = c.merge_all(ccc, cc)
    cccc.dump(sys.stdout, indent=2, sort_keys=True, end="\n")
    print("-" * 80)

    cccc.dump(sys.stdout, indent=2, sort_keys=True, end="\n")
    cccc.update_from_env()
    cccc.dump(sys.stdout, indent=2, sort_keys=True, end="\n")
    print("-" * 80)

    ccccc = Configuration.from_env()
    print(ccccc.dump(sys.stdout, indent=2, sort_keys=True, end="\n"))
    return 0

  sys.exit(_test())
