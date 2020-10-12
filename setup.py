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


def __find_meta(filepath):
  content = __readfile(filepath)
  match = MODULE_META_RE.findall(content)
  if not match:
    raise RuntimeError("error finding module meta in file: %s" % filepath)
  return dict(match)


def __find_readme(basename="README", extensions=("rst", "md", "txt", "")):
  """Locate the Projects README file and determine its content type.

  Args:
    basename (str): README File basename.
    extensions (list of str): List of README file extensions.

  Returns:
     (tuple of str,str): Tuple containing the file content and content type.
  """

  def _readme_content_type(_filename, _default=None):
    if _filename.endswith("rst"):
      return "text/x-rst"
    if _filename.endswith("md"):
      return "text/x-markdown"
    if _filename.endswith("txt"):
      return "text"
    return _default

  long_description = None
  long_description_content_type = None

  for ext in extensions:
    filename = (
        basename
        if not ext or ext is None
        else "{0}.{1}".format(basename, ext)
    )

    filepath = path.join(ROOT, filename)

    if path.exists(filepath):
      long_description = __readfile(filepath)
      long_description_content_type = _readme_content_type(filename, "text")
      break

  return long_description, long_description_content_type


def __iterlines(filepath, **kwargs):
  kwargs.setdefault("encoding", 'utf8')
  with open(filepath, **kwargs) as f:
    for line in filter(None, (line.strip() for line in f)):
      yield line


def __readfile(filepath, **kwargs):
  kwargs.setdefault("encoding", 'utf8')
  with open(filepath, **kwargs) as f:
    return f.read()


def __readlines(filepath, **kwargs):
  return list(__iterlines(filepath, **kwargs))


PACKAGES = find_packages(exclude=("test*", "script*", "example*"))

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

ENTRY_POINTS = {'console_scripts': ['{0}={0}.__main__:main'.format(NAME)]}

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

KEYWORDS = '{0} template'.format(NAME)

LICENSE = METADATA.get("license")

LONG_DESCRIPTION, LONG_DESCRIPTION_CONTENT_TYPE = __find_readme()

PACKAGE_DATA = {}

PLATFORMS = 'Posix; MacOS X; Windows'

REQUIREMENTS = __readlines(path.join(ROOT, "requirements.txt"))

SCRIPTS = None

TITLE = METADATA.get("title")

URL = METADATA.get("url")

VERSION = METADATA["version"]

ZIP_SAFE = False

PROJECT_URLS = {'Source': URL, 'Tracker': '{0}/issues/'.format(URL)}

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
  # TODO: Test
  # This will actually give us a py2exe command.
  # https://github.com/aws/aws-cli/blob/develop/setup.py
  import py2exe  # noqa

  # py2exe specific options.
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
