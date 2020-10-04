# coding=utf8
"""test_log.py
"""
from __future__ import absolute_import, print_function, unicode_literals

import pytest

from skeleton.log import log_request, log_response


@pytest.fixture
def prepared_request():
  """PreparedRequest Fixture for Testing `skeleton.log_request`

  Returns:
    PreparedRequest:  PreparedRequest Instance
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


@pytest.fixture
def response():
  """Response Fixture for Testing `skeleton.log_response`

  Returns:
    Response: Response Instance
  """

  class Response(object):
    """Mock requests.Response
    """
    _content = b'{"TEST": "TEST"}'
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

    @staticmethod
    def json():
      """Mock json method.
      """
      return {}

  return Response()


def test_log_request(prepared_request):
  """Test `skeleton.log_request`

  Args:
    prepared_request (PreparedRequest):
  """
  log_request(prepared_request)


def test_log_response(response):
  """Test `skeleton.log_response`

  Args:
    response (Response): Response Instance
  """
  log_response(response)
