#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""setup.py
"""
# io.open is needed for projects that support Python 2.7. It ensures open()
# defaults to text mode with universal newlines, and accepts an argument to
# specify the text encoding. Python 3 only  projects can skip this import.
# References:
#   https://raw.githubusercontent.com/pypa/sampleproject/master/setup.py
from io import open
from os import path

from setuptools import find_packages, setup

ROOT = path.abspath(path.dirname(__file__))


def __readfile(filepath, **kwargs):
  if not path.isfile(filepath):
    raise FileNotFoundError(filepath)
  kwargs.setdefault("encoding", 'utf-8')
  with open(filepath, **kwargs) as f:
    return f.read()


def __readlines(filepath, **kwargs):
  if not path.isfile(filepath):
    return []
  kwargs.setdefault("encoding", 'utf-8')
  with open(filepath, **kwargs) as f:
    return [line.strip() for line in filter(None, f)]


NAME = "skeleton"

setup(
    author="cloether",
    author_email="cloether@outlook.com",
    classifiers=[
        'Development Status :: 1 - Planning',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'License :: MIT',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet',
    ],
    description="Skeleton Python Module",
    entry_points={
        'console_scripts': [
            '%(name)s=%(name)s.__main__:main' % {
                "name": NAME
            }
        ]
    },
    extras_require={
        "docs": [
            "sphinx",
            "sphinxcontrib-napoleon",
            "guzzle_sphinx_theme"
        ],
        "tests": [
            "pycodestyle",
            "pytest"
        ]
    },
    include_package_data=True,
    install_requires=__readlines("requirements.txt"),
    license="MIT",
    long_description=__readfile('README.rst'),
    long_description_content_type="text/x-rst",
    name=NAME,
    packages=find_packages(exclude=('tests',)),
    package_data={},
    scripts=None,
    url="https://github.com/cloether/skeleton",
    version="0.0.1",
    zip_safe=False
)
