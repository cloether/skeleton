# coding=utf8
"""test_log.py
"""
from __future__ import absolute_import, print_function, unicode_literals

from skeleton.log import (
  apply_session_hook,
  log_request,
  log_request_response,
  log_response
)

__all__ = (
    "test_log_request",
    "test_log_request_content",
    "test_log_response",
    "test_log_response_content",
    "test_log_request_response",
    "test_log_request_response_content",
    "test_apply_session_hook",
    "test_apply_session_hook_content"
)


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


def test_log_request_response(response, log_content=False):
  """Test `skeleton.log_response` with log_content set to True.

  Args:
    response (Response): Response Instance
  """
  log_request_response(response, log_content=log_content)


def test_log_request_response_content(response, log_content=True):
  """Test `skeleton.log_response` with log_content set to True.

  Args:
    response (Response): Response Instance
  """
  log_request_response(response, log_content=log_content)


def test_apply_session_hook(session, log_content=False):
  """Test `skeleton.log_response` with log_content set to True.

  Args:
    session (requests.Session): Session Instance
  """
  apply_session_hook(session, log_content=log_content)


def test_apply_session_hook_content(session, log_content=True):
  """Test `skeleton.log_response` with log_content set to True.

  Args:
    session (requests.Session): Session Instance
  """
  apply_session_hook(session, log_content=log_content)
