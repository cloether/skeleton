#!/usr/bin/env python3
# coding=utf8
"""apidoc.py

Documentation utilities.
"""
from __future__ import absolute_import, print_function, unicode_literals

import logging
import os
from contextlib import contextmanager
from hashlib import md5
from subprocess import CalledProcessError, check_call

from setuptools import find_packages
from six import next

LOGGER = logging.getLogger(__name__)

INDEX_TEMPLATE = """Reference
=========
``{0}`` module reference.

..  toctree::
    :maxdepth: 3

    modules

Indices and tables
------------------
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
"""


def _readfile(filepath, **kwargs):
  if "b" not in kwargs.get("mode", ""):
    kwargs.setdefault("encoding", "utf8")
  with open(filepath, **kwargs) as f:
    return f.read()


def _hash_md5(content):
  """Calculate md5 hash of content.
  """
  h = md5()
  h.update(content)
  return h.hexdigest()


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
      'include' may contain shell-style wildcard patterns, just like
      'exclude'.
    default: default value to return if module name is not found.

  Returns:
    str: Module name if found otherwise None.
  """
  packages = find_packages(
    exclude=exclude,
    where=where,
    include=include
  )
  return next(iter(packages), default)


# noinspection PyUnusedLocal
def docs_generate(parser, args):
  """Generate Project Documentation Files using sphinx-apidoc.

  Returns:
    int: Sphinx command return code.
  """
  repo_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
  docs_source = os.path.join(repo_root, "docs", "source")
  module_path = os.path.join(repo_root, module_name(where=repo_root))
  return run(" ".join(["sphinx-apidoc", "-f", "-o", docs_source, module_path]))


# noinspection PyUnusedLocal
def docs_build(parser, args):
  """Build Project Documentation.

  Returns:
    int: Sphinx command return code.
  """
  repo_root = os.path.abspath((os.path.dirname(os.path.dirname(__file__))))
  return run("make html", os.path.abspath(os.path.join(repo_root, "docs")))


# noinspection PyUnusedLocal
def docs_update(parser, args):
  """Update index.rst to match the project README.rst
  """
  repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

  readme_rst = os.path.join(repo_root, "README.rst")
  readme_content = _readfile(readme_rst, mode="rb")
  readme_hash = _hash_md5(readme_content)
  LOGGER.debug('readme: filepath="%s" md5="%s"', readme_rst, readme_hash)

  index_rst = os.path.join(repo_root, "docs", "source", "index.rst")
  index_content = _readfile(index_rst, mode="rb")[:len(readme_content) + 1]
  index_hash = _hash_md5(index_content)
  LOGGER.debug('index: filepath="%s" md5="%s"', index_rst, index_hash)

  should_update = not readme_hash == index_hash
  LOGGER.debug("needs-update: %s", should_update)

  if not should_update:
    return 0

  readme_content = _readfile(readme_rst)
  readme_content += (
      os.linesep + INDEX_TEMPLATE.format(module_name(where=repo_root))
  )

  with open(index_rst, "w+") as f:
    f.write(readme_content)

  LOGGER.debug('updated index.rst: filepath="%s"', index_rst)
  return 0


def main(**kwargs):
  """CLI Entry Point
  """
  from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, SUPPRESS

  LOGGER.debug("creating argument parser: kwargs=%s", kwargs)

  parser = ArgumentParser(**kwargs)
  parser.set_defaults(
    argument_default=SUPPRESS,
    conflict_handler="resolve",
    description="documentation utilities",
    formatter_class=ArgumentDefaultsHelpFormatter,
    prog=os.path.splitext(os.path.basename(__file__))[0],
  )
  parser.add_argument(
    "-d", "--debug",
    action="store_true",
    help="debug logging"
  )

  sub = parser.add_subparsers(
    title="Command",
    description="command to run (default: generate)",
    dest="command"
  )

  # build
  build_parser = sub.add_parser(
    "build",
    add_help=False,
    help="build full documentation from generated markup files"
  )
  build_parser.set_defaults(func=docs_build, command="build")

  # generate
  generate_parser = sub.add_parser(
    "generate",
    add_help=False,
    help="generate documentation markup files from source"
  )
  generate_parser.set_defaults(func=docs_generate, command="generate")

  # update
  update_parser = sub.add_parser(
    "update",
    add_help=False,
    help="update index.rst from README.rst"  # TODO: support markdown
  )
  update_parser.set_defaults(func=docs_update, command="update")

  parser.set_defaults(func=docs_build, command="build")

  args = parser.parse_args()

  logging.basicConfig(
    level=logging.DEBUG if args.debug else logging.CRITICAL
  )
  return args.func(parser, args)


if __name__ == "__main__":
  import sys

  sys.exit(main())
