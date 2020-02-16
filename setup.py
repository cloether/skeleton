#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""setup.py
"""
import re
from io import open
# io.open is needed for projects that support Python 2.7. It ensures open()
# defaults to text mode with universal newlines, and accepts an argument to
# specify the text encoding. Python 3 only  projects can skip this import.
#
# References:
#   https://raw.githubusercontent.com/pypa/sampleproject/master/setup.py
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


def __find_attr(filepath, name):
  file = __readfile(filepath)
  match = re.search(r"^__%(name)s__ = ['\"](?P<%(name)s>[^'\"]*)['\"]"
                    % dict(name=name), file, re.M)
  if match:
    return match.group(name)
  raise RuntimeError("Unable to find %s string." % name)


# GET PACKAGE NAME
PACKAGES = find_packages(exclude=('tests',))
NAME = PACKAGES[0]

# COLLECT SETUP OPTIONS
# TODO: Get ALL setup options from __version.py

METADATA_FILE = path.join(NAME, "__version__.py")
AUTHOR = "cloether"
AUTHOR_EMAIL = "cloether@outlook.com"
DESCRIPTION = "Skeleton Python Module"
INCLUDE_PACKAGE_DATA = False
LICENSE = "MIT"
LONG_DESCRIPTION = __readfile('README.rst')
LONG_DESCRIPTION_CONTENT_TYPE = "text/x-rst"
NAME = __find_attr(METADATA_FILE, "title")
PACKAGE_DATA = {}
REQUIREMENTS = __readlines("requirements.txt")
SCRIPTS = None
URL = "https://github.com/%s/%s" % (AUTHOR, NAME)
VERSION = __find_attr(METADATA_FILE, "version")
ZIP_SAFE = False

# RUN SETUP

setup(
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
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
    description=DESCRIPTION,
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
            "pytest",
            "pytest-cov",
            "pycodestyle",
            "coverage",
            "requests"
        ]
    },
    include_package_data=INCLUDE_PACKAGE_DATA,
    install_requires=REQUIREMENTS,
    license=LICENSE,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
    name=NAME,
    packages=PACKAGES,
    package_data=PACKAGE_DATA,
    scripts=SCRIPTS,
    url=URL,
    version=VERSION,
    zip_safe=ZIP_SAFE
)
