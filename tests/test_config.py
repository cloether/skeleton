# coding=utf8
"""test_config.py
"""
from __future__ import absolute_import, print_function, unicode_literals

import logging

from skeleton.config import Configuration

LOGGER = logging.getLogger(__name__)


# TODO: Implement Tests

def test_config():
  """Test skeleton.config.Configuration.
  """
  LOGGER.debug("Testing Skeleton Configuration")
  config = Configuration()
  LOGGER.debug("configuration: %s", config)
  assert isinstance(config, Configuration), "Invalid configuration type: " \
                                            "{0}".format(type(config))
  return True
