# coding=utf8
"""setup.py

References:
  https://packaging.python.org/guides/distributing-packages-using-setuptools/
  https://setuptools.readthedocs.io/en/latest/setuptools.html
"""
from __future__ import absolute_import, print_function, unicode_literals

import re
import sys
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

MODULE_META_RE = re.compile(
    r"^__(?P<name>.*)__ = ['\"](?P<value>[^'\"]*)['\"]", re.M
)


def __readfile(filepath, **kwargs):
  if not path.isfile(filepath):
    raise FileNotFoundError(filepath)

  kwargs.setdefault("encoding", 'utf8')

  with open(filepath, **kwargs) as f:
    return f.read()


def __iterlines(filepath, **kwargs):
  if not path.isfile(filepath):
    raise FileNotFoundError(filepath)

  kwargs.setdefault("encoding", 'utf8')

  with open(filepath, **kwargs) as f:
    for line in filter(None, (line.strip() for line in f)):
      yield line


def __readlines(filepath, **kwargs):
  return list(__iterlines(filepath, **kwargs))


def __find_meta(filepath):
  content = __readfile(filepath)

  match = MODULE_META_RE.findall(content)

  if not match:
    raise RuntimeError("error finding module meta in file: %s" % filepath)

  return dict(match)


PACKAGES = find_packages(exclude=('test*',))

NAME = PACKAGES[0]

METADATA = __find_meta(path.join(ROOT, NAME, "__version__.py"))

AUTHOR = METADATA.get("author")

AUTHOR_EMAIL = METADATA.get("author_email")

CLASSIFIERS = [
    'Development Status :: 1 - Planning',
    'Natural Language :: English',
    'Intended Audience :: Developers',
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
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
]

DESCRIPTION = METADATA.get("description")

ENTRY_POINTS = {
    'console_scripts': [
        '%(name)s=%(name)s.__main__:main' % {
            "name": NAME
        }
    ]
}

EXTRAS_REQUIRE = {
    "docs": [
        "sphinx",
        "sphinxcontrib-napoleon",
        "guzzle_sphinx_theme"
    ],
    "tests": [
        "wheel",
        "coverage",
        "pycodestyle",
        "pytest",
        "pytest-cov",
        "pytest-html",
        "tox",
        "tox-travis",
        "twine"
    ],
    ':python_version=="2.6"': [
        'ordereddict==1.1',
        'simplejson==3.3.0'
    ],
    ':python_version=="2.7"': [
        "ipaddress"
    ],
}

INCLUDE_PACKAGE_DATA = False

KEYWORDS = '%s template' % NAME

LICENSE = METADATA.get("license")

# TODO: detect long description file/content type.
LONG_DESCRIPTION = __readfile(path.join(ROOT, 'README.rst'))
LONG_DESCRIPTION_CONTENT_TYPE = "text/x-rst"

PACKAGE_DATA = {}

PLATFORMS = 'Posix; MacOS X; Windows'

REQUIREMENTS = __readlines(path.join(ROOT, "requirements.txt"))

SCRIPTS = None

TITLE = METADATA.get("title")

URL = METADATA.get("url")

VERSION = METADATA["version"]

ZIP_SAFE = False

PROJECT_URLS = {
    'Source': URL,
    'Tracker': '%s/issues/' % URL
}

setup_options = dict(
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    classifiers=CLASSIFIERS,
    description=DESCRIPTION,
    entry_points=ENTRY_POINTS,
    extras_require=EXTRAS_REQUIRE,
    include_package_data=INCLUDE_PACKAGE_DATA,
    install_requires=REQUIREMENTS,
    keywords=KEYWORDS,
    license=LICENSE,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
    name=NAME,
    packages=PACKAGES,
    package_data=PACKAGE_DATA,
    platforms=PLATFORMS,
    project_urls=PROJECT_URLS,
    scripts=SCRIPTS,
    url=URL,
    version=VERSION,
    zip_safe=ZIP_SAFE
)

if 'py2exe' in sys.argv:
  # This will actually give us a py2exe command.
  #
  # References:
  #   https://github.com/aws/aws-cli/blob/develop/setup.py
  #
  # noinspection PyUnresolvedReferences,PyPackageRequirements
  import py2exe

  # And we have some py2exe specific options.
  setup_options['options'] = {
      'py2exe': {
          'optimize': 0,
          'skip_archive': True,
          'dll_excludes': [
              'crypt32.dll'
          ],
          'packages': [
              'docutils',
              'urllib',
              'httplib',
              'HTMLParser',
              NAME,
              'ConfigParser',
              'xml.etree',
              'pipes'
          ],
      }
  }
  setup_options['console'] = [path.join("bin", NAME)]

setup(
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    classifiers=CLASSIFIERS,
    description=DESCRIPTION,
    entry_points=ENTRY_POINTS,
    extras_require=EXTRAS_REQUIRE,
    include_package_data=INCLUDE_PACKAGE_DATA,
    install_requires=REQUIREMENTS,
    keywords=KEYWORDS,
    license=LICENSE,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
    name=NAME,
    packages=PACKAGES,
    package_data=PACKAGE_DATA,
    platforms=PLATFORMS,
    project_urls=PROJECT_URLS,
    scripts=SCRIPTS,
    url=URL,
    version=VERSION,
    zip_safe=ZIP_SAFE
)
