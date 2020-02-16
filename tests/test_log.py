#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""test_log.py
"""
import pytest
from requests import PreparedRequest, Response

from skeleton.log import log_request, log_response


@pytest.fixture
def prepared_request():
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
  log_request(prepared_request)


def test_log_response(response):
  log_response(response)
