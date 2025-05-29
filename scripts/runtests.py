#!/usr/bin/env python3
# coding=utf8
"""run_tests.py

Run tests for the Python module from outside the source directory.

Warning:
  Do not run this script from the root repo directory. This ensures
  we import the installed module, not the local source.
"""
from __future__ import absolute_import, print_function, unicode_literals

import logging
import os
import threading
from contextlib import contextmanager
from errno import EEXIST
from io import TextIOWrapper
from subprocess import PIPE, Popen
from typing import NamedTuple

from setuptools import find_packages
from six import next


class RunResult(NamedTuple):
  """Structured result of a command execution."""
  returncode: int
  stdout: str
  stderr: str


def _stream_output(
    stream: TextIOWrapper,
    target: TextIOWrapper,
    buffer: list,
    flush: bool = True
):
  for line in stream:
    print(line, end="", file=target)
    buffer.append(line)
    if flush and hasattr(target, "flush"):
      target.flush()
  stream.close()


def run_command(command: str, env: dict = None) -> RunResult:
  """Run a shell command with concurrent stdout/stderr streaming and capture.

  Args:
    command (str): Shell command to execute.
    env (dict, optional): Environment variables to set for the command.
      If None, it uses the current environment.

  Returns:
    RunResult: Captured return code, stdout, and stderr.
  """
  if env is None:
    env = os.environ.copy()

  proc = Popen(
    command,
    shell=True,
    env=env,
    stdout=PIPE,
    stderr=PIPE,
    text=True,
    bufsize=1
  )

  assert proc.stdout is not None and proc.stderr is not None

  stdout_lines = []
  stderr_lines = []

  # Stream both stdout and stderr concurrently
  t_out = threading.Thread(
    target=_stream_output,
    args=(proc.stdout, sys.stdout, stdout_lines)
  )
  t_err = threading.Thread(
    target=_stream_output,
    args=(proc.stderr, sys.stderr, stderr_lines)
  )

  t_out.start()
  t_err.start()

  proc.wait()
  t_out.join()
  t_err.join()

  return RunResult(
    returncode=proc.returncode,
    stdout="".join(stdout_lines).strip(),
    stderr="".join(stderr_lines).strip()
  )


@contextmanager
def cwd(dirname):
  """A context manager for operating in a different directory.

  Args:
    dirname (str): Directory to cd into.

  Yields:
    str: Original directory path.
  """
  orig = os.getcwd()
  os.chdir(dirname)
  try:
    yield orig
  finally:
    os.chdir(orig)


def module_name(exclude=("doc*", "example*", "script*", "test*"), where=".",
                include=('*',), default=None):
  """Get the current module name.

  Args:
    exclude (tuple or list): sequence of package names to exclude;
      '*' can be used as a wildcard in the names, such that 'foo.*'
      will exclude all subpackages of 'foo' (but not 'foo' itself).
    where (str): root directory which will be searched for packages.
      It should be supplied as a "cross-platform" (i.e. URL-style)
      path; it will be converted to the appropriate local path
      syntax.
    include (tuple or list): sequence of package names to include.
      If it's specified, only the named packages will be included.
      If it's not specified, all found packages will be included.
      'include' can contain shell-style wildcard patterns just like
      'exclude'.
    default: default value to return if module name is not found.

  Returns:
    str: Module name if found otherwise None.
  """
  packages = find_packages(exclude=exclude, where=where, include=include)
  return next(iter(packages), default)


def mkdir_p(path):
  """Create a directory and any necessary parent directories.

  Notes:
    Unix "mkdir -p" equivalent.

  Args:
    path (str): Filepath to create.

  Raises:
    OSError: Raised for exceptions unrelated to the
      directory already existing.
  """
  try:
    os.makedirs(path)
  except OSError as exc:
    if exc.errno != EEXIST:
      raise


def mkdirs_p(*path):
  """Create multiple directories.

  Notes:
    Unix "mkdir -p" equivalent.

  Args:
    path (str): Filepaths to create.

  Raises:
    OSError: Raised for exceptions unrelated to the
      directory already existing.
  """
  for p in path:
    mkdir_p(p)


def touch(filepath):
  """Equivalent of Unix `touch` command.

  Args:
    filepath (str): Path to touch file.
  """
  if not os.path.exists(filepath):
    fh = open(filepath, "a+")
    try:
      # noinspection PyArgumentEqualDefault
      os.utime(filepath, None)
    finally:
      fh.close()


# TODO: update for changes in pytest and coverage configs

def main():
  """CLI Entry Point.

  Returns:
    int: Command return code.
  """
  logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s"
  )

  repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  module = module_name(where=repo_root)

  if not module:
    logging.error("module name not found in repo root: %s", repo_root)
    return -1

  logging.debug("running tests for module: %s", module)

  run_result = -1  # noqa

  # noinspection PyUnusedLocal
  env_name = os.getenv("ENVNAME", "test")

  tests_dir = os.path.join(repo_root, "tests")
  logs_dir = os.path.join(tests_dir, "logs")
  reports_dir = os.path.join(tests_dir, "reports")
  tests_log_file = os.path.join(logs_dir, "pytest.log")

  mkdirs_p(logs_dir, reports_dir)
  touch(tests_log_file)  # prevent pytest error due to missing log file

  with cwd(repo_root):
    run_result = run_command("pytest --color=yes {posargs} --cov={module}".format(
      posargs=tests_dir,
      module=module
    ))
  return run_result.returncode


if __name__ == "__main__":
  import sys

  sys.exit(main())
