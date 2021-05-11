# coding=utf8
"""setup.py

Examples:
  from setuptools import setup

  setup(
      name="my_other_package",
      version="1.0.0",
      author="me",
      author_email="my.self@example.com",
      url="https://github.com/me/my_other_package",
      description="Descriptive",
      license="Open-Source-Baybeeeeee-1.0",
      install_requires=["setuptools"],
      packages=["my_other_package"],
      package_data={"my_other_package": ["py.typed", "bar.pyi"]},
      data_files=[],
  )

References:
  https://packaging.python.org/guides/distributing-packages-using-setuptools/
  https://setuptools.readthedocs.io/en/latest/setuptools.html
  https://pypi.org/classifiers/
"""
from __future__ import absolute_import, print_function, unicode_literals

import re
import sys
# io.open is needed for projects that support Python 2.7. It ensures open()
# defaults to text mode with universal newlines, and accepts an argument to
# specify the text encoding. Python 3 only  projects can skip this import.
#
# References:
#   https://raw.githubusercontent.com/pypa/sampleproject/master/setup.py
from io import open
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
    """Determine README file content type.

    Notes:
      Currently based off file extension.

    Args:
      _filename (str): README file name.
      _default (str): Default content type.

    Returns:
      str: Content type of the README file.
    """
    if _filename.endswith(".rst"):
      return "text/x-rst"
    if _filename.endswith(".md"):
      return "text/x-markdown"
    if _filename.endswith(".txt"):
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
  if "b" not in kwargs.get("mode", ""):
    kwargs.setdefault("encoding", "utf8")
  with open(filepath, **kwargs) as fd:
    for line in filter(None, (line.strip() for line in fd)):
      yield line


def __readfile(filepath, **kwargs):
  if "b" not in kwargs.get("mode", ""):
    kwargs.setdefault("encoding", "utf8")
  with open(filepath, **kwargs) as fd:
    return fd.read()


def __readlines(filepath, **kwargs):
  return list(__iterlines(filepath, **kwargs))


# class MakeCleanCommand(Command):
#   """A custom command to delete all generated doc files.
#   """
#   description = "run 'make --clean' to delete generated doc files"
#   user_options = [
#       # The format is (long option, short option, description).
#       ('build-dir=', None, 'path to docs build dir'),
#   ]
#
#   def initialize_options(self):
#     """Set default values for options.
#     """
#     # Each user option must be listed here with their default value.
#     # noinspection PyAttributeOutsideInit
#     self.build_dir = 'docs'
#
#   def finalize_options(self):
#     """Post-process options.
#     """
#     if self.build_dir:
#       assert path.exists(self.build_dir), (
#           'Docs build dir %s does not exist.' % self.build_dir
#       )
#
#   def run(self):
#     """Run command.
#     """
#     command = (
#         "cd %(build_dir)s || echo directory %(build_dir)s does not exist. | "
#         "exit 1; make clean; cd .." % {"build_dir": self.build_dir}
#     )
#     self.announce('Running command: make --clean', level=INFO)
#     check_call(command, shell=True)
#     self.announce('Generated doc files cleaned from dir: %s' % self.build_dir,
#                   level=INFO)
#
#
# class RunTestsCommand(Command):
#   """A custom command to run tests.
#   """
#   description = "run 'scripts/run-tests' to to run tests"
#   user_options = [
#       # The format is (long option, short option, description).
#       ('test-runner', None, 'path to test runner script'),
#   ]
#
#   def initialize_options(self):
#     """Set default values for options.
#     """
#     # Each user option must be listed here with their default value.
#     # noinspection PyAttributeOutsideInit
#     self.test_runner = 'pytest'
#
#   def finalize_options(self):
#     """Post-process options.
#     """
#     if not self.test_runner:
#       assert self.test_runner, 'Missing Test Runner.'
#
#   def run(self):
#     """Run Command.
#     """
#     command = "%s" % self.test_runner
#     self.announce('Running test script: %s' % command, level=INFO)
#     try:
#       check_call(command, shell=True)
#     except CalledProcessError as e:
#       self.announce("%s" % e, level=ERROR)


PACKAGES = find_packages(exclude=("doc*", "example*", "script*", "test*"))
NAME = PACKAGES[0]

METADATA = __find_meta(path.join(ROOT, NAME, "__version__.py"))

AUTHOR = METADATA.get("author")
AUTHOR_EMAIL = METADATA.get("author_email")

CLASSIFIERS = [
    "Development Status :: 2 - Pre-Alpha",
    "Natural Language :: English",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Topic :: Software Development :: Libraries :: Python Modules"
]

DESCRIPTION = METADATA.get("description")

ENTRY_POINTS = {
    "console_scripts": [
        "{0}={0}.__main__:main".format(NAME)
    ]
}

EXTRAS_REQUIRE = {
    "docs": [
        "sphinx",
        "sphinxcontrib-napoleon",
        "guzzle_sphinx_theme"
    ],
    "tests": [
        "check-manifest",
        "coverage",
        "pycodestyle",
        "pytest",
        "pytest-cov",
        "pytest-html",
        "tox",
        "tox-travis",
        "twine",
        "wheel"
    ],
    ":python_version==\"2.6\"": [
        "ordereddict==1.1",
        "simplejson==3.3.0"
    ],
    ":python_version==\"2.7\"": [
        "ipaddress"
    ],
}

INCLUDE_PACKAGE_DATA = False

KEYWORDS = "{0} template".format(NAME)

LICENSE = METADATA.get("license")

LONG_DESCRIPTION, LONG_DESCRIPTION_CONTENT_TYPE = __find_readme()

PACKAGE_DATA = {}

PLATFORMS = "Posix; MacOS X; Windows"

REQUIREMENTS = __readlines(path.join(ROOT, "requirements.txt"))

SCRIPTS = None

TITLE = METADATA.get("title")

URL = METADATA.get("url")

VERSION = METADATA["version"]

ZIP_SAFE = False

PROJECT_URLS = {
    # TODO: support more than github-based repositories.
    #   - bitbucket
    #   - gitlab
    #   - etc...
    "Source": URL,
    "Tracker": "{0}/issues".format(URL)
}

# setup options
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

# compile module executable
if "py2exe" in sys.argv:
  # TODO: Test py2exe References:
  #  https://github.com/aws/aws-cli/blob/develop/setup.py
  import py2exe  # noqa

  # py2exe specific options.
  setup_options["options"] = {
      "py2exe": {
          "optimize": 0,
          "skip_archive": True,
          "dll_excludes": [
              "crypt32.dll"
          ],
          "packages": [
              "docutils",
              "urllib",
              "httplib",
              "HTMLParser",
              NAME,
              "ConfigParser",
              "xml.etree",
              "pipes"
          ],
      }
  }
  setup_options["console"] = [
      path.join("bin", NAME)
  ]

# run setup
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
