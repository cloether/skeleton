# coding=utf8
"""test_log.py
"""
from __future__ import absolute_import, print_function, unicode_literals

from skeleton.log import log_request, log_response


def test_log_request(prepared_request):
  """Test `skeleton.log_request`

  Args:
    prepared_request (PreparedRequest): PreparedRequest Instance
  """
  log_request(prepared_request)


def test_log_request_content(prepared_request, log_content=True):
  """Test `skeleton.log_request` with log_content set to True.

  Args:
    prepared_request (PreparedRequest): PreparedRequest Instance
  """
  log_request(prepared_request, log_content=log_content)


def test_log_response(response):
  """Test `skeleton.log_response`

  Args:
    response (Response): Response Instance
  """
  log_response(response)


def test_log_response_content(response, log_content=True):
  """Test `skeleton.log_response` with log_content set to True.

  Args:
    response (Response): Response Instance
  """
  log_response(response, log_content=log_content)
