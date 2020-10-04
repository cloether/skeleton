# coding=utf8
"""apidoc.py
"""
from __future__ import absolute_import, print_function, unicode_literals

import os
from subprocess import CalledProcessError, check_call

from setuptools import find_packages


def run(command):
  """Run Command.
  """
  try:
    return_code = check_call(command, shell=True)
  except CalledProcessError as e:
    sys.stderr.write("{0!r}\n".format(e))
    return_code = e.returncode
  return return_code


def module_name(exclude=("tests.*", "tests"), where="."):
  """Get current module name
  """
  return next(iter(find_packages(exclude=exclude, where=where)), None)


def main():
  """CLI Entry Point
  """
  repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  docs_source = os.path.join(repo_root, "docs", "source")
  module = module_name(where=repo_root)
  module_path = os.path.join(repo_root, module)
  return run(" ".join(["sphinx-apidoc", "-f", "-o", docs_source, module_path]))


if __name__ == '__main__':
  import sys

  sys.exit(main())
