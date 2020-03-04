#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""install.py
"""
import os
import shutil
from subprocess import check_call

_DIRNAME = os.path.dirname

REPO_ROOT = _DIRNAME(_DIRNAME(os.path.abspath(__file__)))
os.chdir(REPO_ROOT)


def run(command):
  """Run Command.
  """
  return check_call(command, shell=True)


run('pip install -r requirements.txt')
run('pip install .[docs,tests]')

if os.path.isdir('dist') and os.listdir('dist'):
  shutil.rmtree('dist')

run('python setup.py release')
run('pip install %s' % (os.path.join('dist', os.listdir('dist')[0])))
