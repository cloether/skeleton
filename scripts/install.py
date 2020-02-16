#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""install.py
"""
import os
import shutil
import sys
from subprocess import check_call

from six import text_type

_DIRNAME = os.path.dirname
REPO_ROOT = _DIRNAME(_DIRNAME(os.path.abspath(__file__)))
os.chdir(REPO_ROOT)


def run(command):
  return check_call(command, shell=True)


try:
  # Has the form "major.minor"
  python_version = os.environ['PYTHON_VERSION']
except KeyError:
  python_version = '.'.join([text_type(i) for i in sys.version_info[:2]])
run('pip install -r requirements.txt')
run('pip install coverage')
run('pip install pytest')
run('pip install pytest-cov')
run('pip install requests')
if os.path.isdir('dist') and os.listdir('dist'):
  shutil.rmtree('dist')
run('python setup.py bdist_wheel')
run('pip install %s' % (os.path.join('dist', os.listdir('dist')[0])))
