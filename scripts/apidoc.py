#!/usr/bin/env python
# coding=utf8
"""apidoc.py
"""
from __future__ import absolute_import, print_function, unicode_literals

import inspect
import logging
import os
import re
from contextlib import contextmanager
from subprocess import CalledProcessError, check_call

from setuptools import find_packages
from six import next, text_type

LOGGER = logging.getLogger(__name__)


@contextmanager
def cwd(dirname):
  """Context manager for operating in a different directory.

  Args:
    dirname (str): Path to directory which will become
      the current working directory.

  Yields:
    str: Original current working directory path.
  """
  orig = os.getcwd()
  os.chdir(dirname)
  try:
    yield orig
  finally:
    os.chdir(orig)


def _run(command, **kwargs):
  """Wrapper around subprocess.check_call with some
  added (minimal) error handling.

  Args:
    command (str or list): Command to run.

  Keyword Args:
    shell (bool): If true, the command will be executed
      through the shell.

  Returns:
    int: Return Code.
  """
  kwargs.setdefault("shell", True)

  try:
    return_code = check_call(command, **kwargs)
  except CalledProcessError as e:
    LOGGER.exception(
        "error occurred while running command: "
        "command=\"{0}\" returncode={1}".format(command, e.returncode)
    )
    return_code = e.returncode
  return return_code


def run(command, location=None):
  """Run Command.

  Args:
    command (str): Command to run.
    location (str): Location to run command from.

  Returns:
    int: Return Code.
  """
  LOGGER.debug(
      'running command: command="%s" location="%s"',
      command, location
  )
  if location is not None:
    with cwd(location):
      return _run(command)
  return _run(command)


def module_name(exclude=("doc*", "example*", "script*", "test*"), where=".",
                include=('*',), default=None):
  """Get current module name.

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
      'include' can contain shell style wildcard patterns just like
      'exclude'.
    default: default value to return if module name is not found.

  Returns:
    str: Module name if found otherwise None.
  """
  packages = find_packages(exclude=exclude, where=where, include=include)
  return next(iter(packages), default)


def docs_gen():
  """Generate Project Documentation Files using sphinx-apidoc.

  Returns:
    int: Sphinx command return code.
  """
  repo_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
  docs_source = os.path.join(repo_root, "docs", "source")
  module_path = os.path.join(repo_root, module_name(where=repo_root))
  return run(" ".join(["sphinx-apidoc", "-f", "-o", docs_source, module_path]))


def docs_build():
  """Build Project Documentation.

  Returns:
    int: Sphinx command return code.
  """
  repo_root = os.path.abspath((os.path.dirname(os.path.dirname(__file__))))
  return run("make html", os.path.abspath(os.path.join(repo_root, "docs")))


# EXPERIMENTAL

def extract_full_summary_from_signature(operation):
  """Extract the summary from the docstring of the command.

  Returns:
    str: Full summary information.
  """
  lines = inspect.getdoc(operation)
  summary = ''
  if lines:
    match = re.search(r'\s*(:param)\s+(.+?)\s*:(.*)', lines)
    summary = lines[:match.regs[0][0]] if match else lines
  summary = summary.replace('\n', ' ').replace('\r', '')
  return summary


def option_descriptions(operation):
  """Extract parameter help from docstring of the command.

  Returns:
    dict: Dictionary of argument names and description.
  """
  lines = inspect.getdoc(operation)
  if not lines:
    return {}

  # param_breaks = ["'''", '"""', ':param', ':type', ':return', ':rtype']
  param_breaks = ["'''", '"""', ':param', ':type', ':return', ':rtype']
  descriptions = {}
  lines = lines.splitlines()
  index = 0

  while index < len(lines):
    line = lines[index]
    match = re.search(r'\s*(:param)\s+(.+?)\s*:(.*)', line)
    if not match:
      index += 1
      continue
    # 'arg name' portion might have type info, we don't need it
    arg_name = text_type.split(match.group(2))[-1]
    arg_desc = match.group(3).strip()

    # look for more descriptions on subsequent lines
    index += 1
    while index < len(lines):
      temp = lines[index].strip()
      if any(temp.startswith(x) for x in param_breaks):
        break
      if temp:
        arg_desc += (' ' + temp)
      index += 1
    descriptions[arg_name] = arg_desc
  return descriptions


def extract_args_from_signature(operation, excluded_params=None):
  """Extracts basic argument data from an operation's
  signature and docstring

  Args:
    operation: Object to extract signature from.
    excluded_params (list of str): List of params to
      ignore and not extract.

  Notes:
    By default we ignore ['self', 'kwargs'].

  Yields:
    tuple of str,dict: Tuple containing argument name and
      arguments information as a dictionary.
  """
  # noinspection PyUnusedLocal
  args = []

  try:
    # only supported in python3
    # - falling back to argspec if not available
    sig = inspect.signature(operation)
    args = sig.parameters
  except AttributeError:
    # noinspection PyDeprecation
    sig = inspect.getargspec(operation)
    args = sig.args

  arg_docstring_help = option_descriptions(operation)
  excluded_params = excluded_params or ['self', 'kwargs']

  for arg_name in [a for a in args if a not in excluded_params]:
    try:  # this works in python3
      default = args[arg_name].default
      required = default == inspect.Parameter.empty
    except TypeError:
      arg_defaults = (
          dict(zip(sig.args[-len(sig.defaults):], sig.defaults))
          if sig.defaults
          else {}
      )
      default = arg_defaults.get(arg_name)
      required = arg_name not in arg_defaults

    action = (
        'store_{0}'.format(text_type(not default).lower())
        if isinstance(default, bool)
        else None
    )

    try:
      # noinspection PyUnresolvedReferences,PyProtectedMember
      default = (
          default
          if default != inspect._empty
          else None
      )
    except AttributeError:
      pass

    options_list = ['--' + arg_name.replace('_', '-')]
    help_str = arg_docstring_help.get(arg_name)
    yield (arg_name, dict(
        arg_name=arg_name,
        options_list=options_list,
        required=required,
        default=default,
        help=help_str,
        action=action
    ))


# END EXPERIMENTAL

def main():
  """CLI Entry Point
  """
  from argparse import ArgumentParser

  parser = ArgumentParser()
  parser.add_argument(
      "action",
      default="generate",
      choices=["build", "generate"],
      help="build documentation"
  )
  parser.add_argument(
      "-d", "--debug",
      action="store_true",
      help="debug logging"
  )
  args = parser.parse_args()
  if args.debug:
    logging.basicConfig(level=logging.DEBUG)
  return (docs_build if args.action == "build" else docs_gen)()


if __name__ == "__main__":
  import sys

  sys.exit(main())
