#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""test_log.py
"""
import pytest
from requests import PreparedRequest, Response

from skeleton.log import log_request, log_response


@pytest.fixture
def prepared_request():
  """PreparedRequest Fixture for Testing `skeleton.log_request`

  Returns:
    PreparedRequest:  PreparedRequest Instance
  """
  _request = PreparedRequest()
  _request.url = "https://www.google.com/"
  _request.method = "get"
  _request.headers = {
      "Accept": "application/json",
      "Content-type": "application/json"
  }
  return _request


@pytest.fixture
def response():
  """Response Fixture for Testing `skeleton.log_response`

  Returns:
    Response: Response Instance
  """
  _response = Response()
  _response.status_code = 200
  _response.reason = "OK"
  _response.url = "https://www.google.com/"
  _response._content = b'{"TEST": "TEST"}'
  _response.headers = {
      "Accept": "application/json",
      "Content-type": "application/json",
      "Content-disposition": "application/json"
  }
  return _response


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
