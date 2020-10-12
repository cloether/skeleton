#!/usr/bin/env python
# coding=utf8
"""apidoc.py
"""
from __future__ import absolute_import, print_function, unicode_literals

import os
from contextlib import contextmanager
from subprocess import CalledProcessError, check_call

from setuptools import find_packages
from six import next


@contextmanager
def cwd(dirname):
  """A context manager for operating in a different directory.
  """
  orig = os.getcwd()
  os.chdir(dirname)
  try:
    yield orig
  finally:
    os.chdir(orig)


def run(command):
  """Run Command.
  """
  try:
    return_code = check_call(command, shell=True)
  except CalledProcessError as e:
    sys.stderr.write("{0!r}\n".format(e))
    return_code = e.returncode
  return return_code


def module_name(exclude=("test*", "script*", "example*"), where="."):
  """Get current module name
  """
  return next(iter(find_packages(exclude=exclude, where=where)), None)


def docs_gen():
  """Generate Project Documentation Files using sphinx-apidoc.
  """
  repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  docs_source = os.path.join(repo_root, "docs", "source")
  module = module_name(where=repo_root)
  module_path = os.path.join(repo_root, module)
  return run(" ".join(["sphinx-apidoc", "-f", "-o", docs_source, module_path]))


def docs_build():
  """Build Project Documentation.
  """
  repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  with cwd(os.path.join(repo_root, "docs")):
    return_code = run("make html")
  return return_code


def main():
  """CLI Entry Point
  """
  if "-b" in sys.argv or "--build" in sys.argv:
    return docs_build()
  return docs_gen()


if __name__ == '__main__':
  import sys

  sys.exit(main())
