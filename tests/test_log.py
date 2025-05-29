# coding=utf8
"""test_log.py
"""
from __future__ import absolute_import, print_function, unicode_literals

import logging
from unittest.mock import patch

import pytest

from skeleton.log import (
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
  logging.basicConfig(level=logging.DEBUG)
  with patch("skeleton.log.LOGGER") as mock_logger:
    log_request(prepared_request)
    mock_logger.debug.assert_called()


def test_log_request_content(prepared_request, log_content=True):
  """Test `skeleton.log_request` with log_content set to True.

  Args:
    prepared_request (PreparedRequest): PreparedRequest Instance
  """
  logging.basicConfig(level=logging.DEBUG)
  with patch("skeleton.log.LOGGER") as mock_logger:
    log_request(prepared_request, log_content=log_content)
    mock_logger.debug.assert_called()


def test_log_response(response):
  """Test `skeleton.log_response`

  Args:
    response (Response): Response Instance
  """
  logging.basicConfig(level=logging.DEBUG)
  with patch("skeleton.log.LOGGER") as mock_logger:
    log_response(response)
    mock_logger.debug.assert_called()


def test_log_response_content(response, log_content=True):
  """Test `skeleton.log_response` with log_content set to True.

  Args:
    response (Response): Response Instance
  """
  logging.basicConfig(level=logging.DEBUG)
  with patch("skeleton.log.LOGGER") as mock_logger:
    log_response(response, log_content=log_content)
    mock_logger.debug.assert_called()


def test_log_request_response(response, log_content=False):
  """Test `skeleton.log_request_response` with log_content set to False.

  Args:
    response (Response): Response Instance
  """
  logging.basicConfig(level=logging.DEBUG)
  with patch("skeleton.log.LOGGER") as mock_logger:
    log_request_response(response, log_content=log_content)
    mock_logger.debug.assert_called()


def test_log_request_response_content(
    response,
    caplog: pytest.LogCaptureFixture,
    log_content: bool = True,
):
  """Test `skeleton.log_request_response` with log_content set to True.

  Args:
    response (Response): Response Instance
  """
  import logging

  logging.basicConfig(level=logging.DEBUG)

  from skeleton.log import LOGGER

  LOGGER.setLevel(logging.DEBUG)
  # Ensure the logger propagates to the root logger
  LOGGER.propagate = True

  with caplog.at_level(logging.DEBUG, logger=LOGGER.name):
    log_request_response(response, log_content=log_content)
    log_text = caplog.text
    assert "REQUEST:" in log_text
    assert "- METHOD:" in log_text
    assert "- URL:" in log_text
    assert "- HEADERS:" in log_text
    assert "- BODY:" in log_text
    assert "RESPONSE:" in log_text
    assert "- HEADERS:" in log_text
    assert "- STATUS CODE:" in log_text
    assert "- CONTENT:" in log_text


def test_apply_session_hook(session, log_content=False):
  """Test `skeleton.apply_session_hook` with log_content set to False.

  Args:
    session (requests.Session): Session Instance
  """
  from functools import partial
  from skeleton.log import log_request_response, apply_session_hook

  apply_session_hook(session, log_content=log_content)
  hook = session.hooks["response"][0]
  assert isinstance(hook, partial), "Session hook is not a functools.partial"
  assert hook.func is log_request_response, (
    "Session hook does not use log_request_response"
  )


def test_apply_session_hook_content(session, log_content=True):
  """Test `skeleton.apply_session_hook` with `log_content` set to True.

  Args:
    session (requests.Session): Session Instance
  """
  from functools import partial
  from skeleton.log import log_request_response, apply_session_hook

  apply_session_hook(session, log_content=log_content)
  hook = session.hooks["response"][0]
  assert isinstance(hook, partial), "Session hook is not a functools.partial"
  assert hook.func is log_request_response, (
    "Session hook does not use log_request_response"
  )
