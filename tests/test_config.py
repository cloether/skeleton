# coding=utf8
"""test_config.py
"""
from __future__ import absolute_import, print_function, unicode_literals

import logging
import os

from six import StringIO

from skeleton.config import Configuration

__all__ = (
    "test_config",
    "test_configuration_from_env",
    "test_configuration_update_from_env",
    "test_configuration_from_object",
    "test_configuration_dump",
    "test_configuration_from_dict",
    "test_configuration_merge_all",
    "test_configuration_search_paths"
)

LOGGER = logging.getLogger(__name__)


# TODO: Finish Test Implementation

def test_config():
  """Test skeleton.config.Configuration.
  """
  LOGGER.debug("Testing Skeleton Configuration")

  config = Configuration()

  LOGGER.debug("configuration: %s", config)

  assert isinstance(config, Configuration), "Invalid configuration type: " \
                                            "{0}".format(type(config))
  return True


def test_configuration_from_env():
  """Test Configuration.from_env.
  """
  LOGGER.debug("Testing: Configuration.from_env")

  config = Configuration.from_env()

  LOGGER.debug(
      "(from_env) Configuration: %s",
      config.as_string(indent=2, sort_keys=True)
  )
  return True


def test_configuration_update_from_env():
  """Test Configuration.update_from_env.
  """
  LOGGER.debug("Testing: Configuration.update_from_env")

  os.environ["client_cert"] = "bbb"
  os.environ["max_pool_connections"] = "20"

  config = Configuration()
  config._update_from_env()

  assert os.environ["max_pool_connections"] == "20", "Failed to update from env"
  assert os.environ["client_cert"] == "bbb", "Failed to update from env"

  LOGGER.debug(
      "(update_from_env) Configuration: %s",
      config.as_string(indent=2, sort_keys=True)
  )
  return True


def test_configuration_from_object():
  """Test Configuration.from_object.
  """
  LOGGER.debug("Testing: Configuration.from_object")

  class CONFIG:
    """Config Object
    """
    CLIENT_CERT = "b"

  config = Configuration.from_object(CONFIG)
  LOGGER.debug(
      "(from_object) Configuration: %s",
      config.as_string(indent=2, sort_keys=True)
  )
  assert config.get("client_cert") == CONFIG.CLIENT_CERT, "invalid client cert"
  return True


def test_configuration_merge_all():
  """Test Configuration.merge_all.
  """
  LOGGER.debug("Testing: Configuration.merge_all")

  config_base = Configuration("a", proxies="B")

  config_1 = Configuration("b", proxies="C")
  config_2 = Configuration("c", proxies="D")
  config_merged = config_base.merge_all(config_1, config_2)

  LOGGER.debug(
      "(merged) Configuration: %s",
      config_merged.as_string(indent=2, sort_keys=True)
  )
  return True


def test_configuration_from_dict():
  """Test Configuration.from_dict.
  """
  LOGGER.debug("Testing: Configuration.from_dict")

  config = Configuration.from_dict({
      'client_cert': "b",
      'connect_timeout': 60,
      'log_datefmt': "%Y-%m-%d %H:%M:%S",
      'log_file': None,
      'log_filemode': "a+",
      'log_format': (
          "(%(asctime)s)[%(levelname)s]%(name)s."
          "%(funcName)s(%(lineno)d):%(message)s"
      ),
      'log_level': "ERROR",
      'log_style': "%",
      'max_pool_connections': 10,
      'pool_timeout': None,
      'poolblock': False,
      'poolsize': 10,
      'proxies': "C",
      'proxies_config': None,
      "read_timeout": 60,
      "retries": 0,
      "user_agent": "skeleton-0.0.8",
      "verify": False
  })

  LOGGER.debug(
      "(from_dict) Configuration: %s",
      config.as_string(indent=2, sort_keys=True)
  )
  return True


def test_configuration_dump():
  """Test Configuration.dump.
  """
  LOGGER.debug("Testing: Configuration.dump")

  config = Configuration()
  LOGGER.debug("Configuration: %s", config.as_string(indent=2, sort_keys=True))

  s = StringIO()
  config.dump(s)
  config_dumped = Configuration.from_dict(s.getvalue())

  LOGGER.debug(
      "(Dumped) Configuration: %s",
      config_dumped.as_string(indent=2, sort_keys=True)
  )

  assert config == config_dumped
  return True


def test_configuration_search_paths():
  """Test Configuration.SEARCH_PATHS.
  """
  LOGGER.debug("Testing: Configuration.SEARCH_PATHS")
  config = Configuration()
  LOGGER.debug("Configuration Search Paths: %s", config.SEARCH_PATHS)
  return True
