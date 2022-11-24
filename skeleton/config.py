# coding=utf8
"""config.py

Configuration
"""
from __future__ import absolute_import, print_function, unicode_literals

import copy
import json
import logging
import os
import sys
from collections import OrderedDict

from appdirs import AppDirs
from six import (
  PY2,
  ensure_binary,
  iteritems,
  reraise,
  string_types,
  text_type
)

from . import __app_id__, __author__, __title__, __version__
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
  """Create Configuration from an environment variables.

  Args:
    keys (list or tuple or str): Environment variables to retrieve.
    default: Default value to set for key when no value is found.
    drop_null (bool): If True null values will be ignored.

  Returns:
    dict: Dict of environment variable key/vales.
  """
  config = {}

  if not keys:
    return config

  if isinstance(keys, string_types):
    keys = (keys,)

  for key in keys:
    value = os.getenv(key, None)
    if drop_null and (not value or value is None):
      continue

    config[key] = (
        value
        if value is not None
        else default
    )
  return config


# pylint: disable=inconsistent-return-statements
def import_string(import_name, silent=False):
  """Imports an object based on a string.

  This is useful if you want to use import paths as endpoints
  or something similar.  An import path can be specified either
  in dotted notation (``xml.sax.saxutils.escape``) or with a
  colon as object delimiter (``xml.sax.saxutils:escape``).

  If `silent` is True the return value will be `None` if the
  import fails.

  Args:
    import_name (str): the dotted name for the object to import.
    silent (bool): if set to `True` import errors are ignored and
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
      traceback = sys.exc_info()[2]

      reraise(ImportError, e, traceback)
  except ImportError as e:
    if not silent:
      reraise(
          tp=ImportStringError,
          value=ImportStringError(import_name, e),
          tb=sys.exc_info()[2]
      )
      raise


# pylint: disable=useless-object-inheritance
class ConfigAttribute(object):
  """Makes an attribute forward to the config.
  """

  def __init__(self, name, get_converter=None):
    self.__name__ = name
    self.get_converter = get_converter

  def __get__(self, instance, owner=None):
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

  APP_DIRS = AppDirs(__title__, __author__, __version__)

  FILENAME = "{0}.json".format(__title__)
  FILEPATH_SITE = os.path.join(APP_DIRS.site_config_dir, FILENAME)
  FILEPATH_USER = os.path.join(APP_DIRS.user_config_dir, FILENAME)

  SEARCH_PATHS = (
      FILEPATH_SITE,
      FILEPATH_USER,
      FILENAME
  )

  # noinspection PyMissingConstructor
  # pylint: disable=super-init-not-called
  def __init__(self, *args, **kwargs):
    # record user provided options
    self._user_options = self._make_options(*args, **kwargs)
    # merge the user_provided options onto the default options
    config_vars = copy.copy(self.OPTIONS)
    config_vars.update(self._user_options)
    # set the attributes based on the config_vars
    dict.update(self, config_vars)

  def _make_options(self, *args, **kwargs):
    """Set configuration values.

    Returns:
      dict: Configuration dictionary.
    """
    config = {}
    for key, value in iteritems(kwargs):
      if key not in self.OPTIONS:
        raise ValueError("invalid key: {0}".format(key))
      config[key] = value

    keys = self.keylist()
    # number of args should not be longer than allowed options
    if len(args) > len(keys):
      raise TypeError(
          "takes at most {0} arguments ({1} given)".format(
              len(keys), len(args)
          )
      )

    # iterate through args passed through to the constructor
    # and map them tp their corresponding keys.
    for i, arg in enumerate(args):
      # if a kwarg was specified for the arg, then error out.
      if keys[i] in config:
        raise TypeError(
            "multiple values for keyword argument: {0}".format(keys[i])
        )
      config[keys[i]] = arg
    return config

  # compatibility

  if PY2:
    def items(self):
      """Dict Items."""
      # noinspection PyCompatibility
      return self.iteritems()

    def keys(self):
      """Dict Keys."""
      # noinspection PyCompatibility
      return self.iterkeys()

    def values(self):
      """Dict Values."""
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

    Args:
      value (object): Configuration object.

    Returns:
      Configuration: Configuration instance.
    """
    if isinstance(value, string_types):
      value = import_string(value)
    options = {}
    for key in dir(value):
      if key.isupper():
        options[key.lower()] = getattr(value, key, None)
    return cls(**options)

  @classmethod
  def from_dict(cls, value):
    """Create Configuration from a python dictionary.

    Args:
      value (dict or str): Configuration dictionary.

    Returns:
      Configuration: Configuration instance.
    """
    if isinstance(value, string_types):
      value = json.loads(value)
    options = {}
    for key in value:
      options[key] = value[key]
    return cls(**options)

  @classmethod
  def from_file(cls, value):
    """Create Configuration from a file.

    Returns:
      skeleton.config.Configuration: Configuration Instance.
    """
    with open(value) as fd:
      content = json.load(fd)
    return cls(**content)

  @classmethod
  def from_env(cls, default=None, drop_null=True):
    """Create Configuration from a environment variables.

    Returns:
      skeleton.config.Configuration: Configuration Instance.
    """
    return cls(**getenv(
        cls.keylist(),
        default=default,
        drop_null=drop_null
    ))

  def _update_from_env(self, default=None, drop_null=True):
    """Update Configuration from environment variables.
    """
    dict.update(self, getenv(
        self.keylist(),
        default=default,
        drop_null=drop_null
    ))

  @classmethod
  def get_env(cls, key, default=None):
    """Create Configuration from a environment variables.

    Returns:
      skeleton.config.Configuration: Configuration Instance.
    """
    cls.validate_key(key)
    return cls(key=os.getenv(key, default))

  @classmethod
  def validate_key(cls, key, strict=True):
    """Validate configuration key.

    Raises:
      ValueError: Raised when key is not valid and strict
        is set to True.

    Returns:
      bool: True if key is valid otherwise False.
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
  # pylint: disable=unused-argument
  def as_dict(self, **kwargs):
    """Return configuration as a dict.

    Returns:
      dict: Configuration dict.
    """
    # pylint: disable=unnecessary-comprehension
    return {k: v for k, v in self.items()}

  # noinspection PyUnusedLocal
  # pylint: disable=unused-argument
  def as_list(self, **kwargs):
    """Return configuration as list of tuples.

    Returns:
      (list or tuple): List of Configuration keys and values.
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

  # set

  def set(self, key, value):
    """Set configuration value.
    """
    if key not in self.OPTIONS:
      raise ValueError("non-existent option: {0}".format(key))
    dict.__setitem__(self, key, value)

  # get

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

    Returns:
      list: List of key values.
    """
    return [self.get(key, default=default, strict=strict) for key in keys]

  # merge

  def merge(self, other):
    """Merge current config with another config.

    This will merge in all non-default values from the
    provided config and return a new config object.

    Args:
      other (skeleton.config.Configuration): Configuration to merge with.

    Returns:
      skeleton.config.Configuration: A config object built
        from the merged values of both config objects.
    """
    # copy current attributes in config object.
    # pylint: disable=protected-access
    config_options = copy.copy(self._user_options)
    # merge user options from other config
    # pylint: disable=protected-access
    config_options.update(other._user_options)
    # return new config with merged properties
    return Configuration(**config_options)

  def merge_all(self, *others):
    """Merge current config with other configs.

    This will merge in all non-default values from the
    provided config and return a new config object.

    Args:
      others (Configuration): Configuration to merge with.

    Returns:
      Configuration: A config object built from the merged
        values of both config objects.
    """
    # copy current attributes in config object.
    # pylint: disable=protected-access
    options = copy.copy(self._user_options)
    for other in reversed(others):
      # pylint: disable=protected-access
      options.update(other._user_options)
    return Configuration(**options)

  # dump

  def dump(self, *args, **kwargs):
    """Write configuration to buffer.

    Keyword Args:
      end (str): String to write to the output buffer
        after the content is dumped.
    """
    fd = args[0] if args else sys.stdout
    end = kwargs.pop("end", None)
    json.dump(self, fd, **kwargs)
    if end and end is not None:
      fd.write(end)

  # builtin

  __str__ = __repr__ = as_string
  __bytes__ = as_bytes
  __dir__ = keylist
  __setitem__ = set
  __getitem__ = get
