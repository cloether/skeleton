# coding=utf8
"""conftest.py

Define fixtures for static data used by tests (shared fixtures).

This data can be accessed by all tests in the suite unless
specified otherwise. This could be data as well as helpers
of modules which will be passed to all tests.
"""
from __future__ import absolute_import, print_function, unicode_literals

import json
import logging
import os

import pytest
import requests

from skeleton.error import BaseError
from .utils import module_name as _modname

__all__ = (
    "module_name",
    "prepared_request",
    "response",
    "error",
    "modname",
    "filename",
    "number",
    "boolean",
    "session"
)


@pytest.fixture(autouse=True)
def reset_log_level():
  """Automatically reset log level verbosity between tests.

  Generally want test output the Unix way: silence is golden.
  """
  logging.getLogger().setLevel(logging.WARN)


@pytest.fixture(name="module_name")
def module_name():
  """Current module name.

  Returns:
    str: Module name.
  """
  repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  return _modname(where=repo_root)


@pytest.fixture(name="prepared_request")
def prepared_request():
  """PreparedRequest Fixture for Testing `skeleton.log_request`

  Returns:
    requests.PreparedRequest:  PreparedRequest Instance
  """

  class PreparedRequest(object):
    """Mock requests.PreparedRequest
    """
    body = b""
    headers = {
        "Accept": "application/json",
        "Content-type": "application/json"
    }
    method = "get"
    path_url = "?p1=param1&p2=param2"
    url = "https://www.google.com/"

  return PreparedRequest()


@pytest.fixture(name="response")
def response():
  """Response Fixture for Testing `skeleton.log_response`

  Returns:
    requests.Response: Response Instance
  """

  class Response(object):
    """Mock requests.Response
    """
    _content = b"{\"TEST\": \"TEST\"}"
    cookies = {}
    encoding = "utf8"
    headers = {
        "Accept": "application/json",
        "Content-type": "application/json",
        "Content-disposition": "application/json"
    }
    reason = "OK"
    status_code = 200
    url = "https://www.google.com/"

    class PreparedRequest(object):
      """Mock requests.PreparedRequest
      """
      body = b""
      headers = {
          "Accept": "application/json",
          "Content-type": "application/json"
      }
      method = "get"
      path_url = "?p1=param1&p2=param2"
      url = "https://www.google.com/"

    request = PreparedRequest()

    def json(self):
      """Mock json method.
      """
      return json.loads(self._content)

  return Response()


@pytest.fixture(name="error")
def error():
  """Error Fixture

  Returns:
    skeleton.BaseError: Instance of BaseError
  """
  return BaseError(error="TEST ERROR MESSAGE")


@pytest.fixture(name="log_content")
def log_content():
  """Log content found in HTTP Requests/Responses.

  Returns:
    bool: True if log content should be enabled otherwise False.
  """
  return True


@pytest.fixture(name="filename")
def filename():
  """Filename used for to_valid_filename in test_utils.py.

  Returns:
    str: Filename
  """
  return "bad\\filename"


@pytest.fixture(name="modname")
def modname():
  """Module name used for to_valid_module_name in test_utils.py.

  Returns:
    str: Module name
  """
  return "bad\\module"


@pytest.fixture(name="number")
def number():
  """Number used for as_number test in test_utils.py.

  Returns:
    str: String number.
  """
  return "1"


@pytest.fixture(name="boolean")
def boolean():
  """Boolean string used for as_bool test in test_utils.py.

  Returns:
    str: String boolean.
  """
  return "yes"


@pytest.fixture(name="session")
def session():
  """Session.

  Returns:
    str: String boolean.
  """
  return requests.Session()
