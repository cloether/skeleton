#!/usr/bin/env python3
# coding=utf8
"""depupdate.py

Update or check Python project dependencies.
"""
from __future__ import absolute_import, print_function, unicode_literals

import getpass
import json
import logging
import os
import re
import sys
from datetime import datetime
from subprocess import CalledProcessError, PIPE, check_call, run

# script version
__version__ = "0.0.1"

_SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0]

LOGGER = logging.getLogger(_SCRIPT_NAME)


def _serialize_args(args):
  def _serialize_value(v):
    # If it's a basic type, return as is
    if isinstance(v, (str, int, float, bool, type(None))):
      return v
    # If it's a file-like object, show its class and name
    if hasattr(v, 'name') and hasattr(v, 'mode'):
      return {
        "class": v.__class__.__name__,
        "name": v.name,
        "mode": v.mode
      }
    # If it's a type, return its name
    if isinstance(v, type):
      return v.__name__
    # If it's an object with __dict__, show class and attributes
    if hasattr(v, '__dict__'):
      return {
        "class": v.__class__.__name__,
        "attributes": {
          k: _serialize_value(val)
          for k, val in vars(v).items()
        }
      }
    # Fallback to string
    return str(v)

  return {
    k: _serialize_value(v)
    for k, v in vars(args).items()
    if v is not None
  }


def argument_parser(**kwargs):
  """Construct Argument Parser."""
  from argparse import (
    ArgumentParser,
    ArgumentDefaultsHelpFormatter,
    FileType,
    SUPPRESS
  )

  _file_mode_suffix = "b" if sys.version_info[0] == 2 else ""
  _filetype_read = FileType("r+{0}".format(_file_mode_suffix))
  _filetype_write = FileType("w+{0}".format(_file_mode_suffix))

  parser = ArgumentParser(**kwargs)
  parser.set_defaults(
    argument_default=SUPPRESS,
    conflict_handler="resolve",
    formatter_class=ArgumentDefaultsHelpFormatter,
    add_help=False
  )
  parser.add_argument(
    "-V", "--version",
    action="version",
    version=__version__
  )
  parser.add_argument(
    "-d", "--debug",
    "-v", "--verbose",
    dest="verbose",
    action="store_true",
    help="enable debug/verbose logging"
  )
  parser.add_argument(
    "--logfile",
    action="store",
    dest="logfile",
    required=False,
    help="path to log file"
  )
  parser.add_argument(
    "input",
    nargs="?",
    default="-",
    type=_filetype_read,
    help="program input"
  )
  parser.add_argument(
    "-o", "--output",
    action="store",
    nargs="?",
    default="-",
    required=False,
    type=_filetype_write,
    help="program output"
  )
  parser.add_argument(
    "requirements_file",
    nargs="?",
    default="requirements.txt",
    type=str,
    help="path to requirements.txt file (default: requirements.txt)"
  )
  parser.add_argument(
    "--update",
    action="store_true",
    dest="update",
    default=False,
    help="update dependencies to latest versions"
  )
  parser.add_argument(
    "--check",
    action="store_true",
    dest="check",
    default=False,
    help="check if dependencies are up to date"
  )
  parser.add_argument(
    "--write",
    action="store_true",
    dest="write",
    default=False,
    help="write latest versions to requirements file"
  )
  return parser


def parse_requirements(file_path):
  """Parse the requirements.txt file and return a list of dependencies."""
  # noinspection PyArgumentEqualDefault
  with open(file_path, 'r') as f:
    lines = f.readlines()
  dependencies = [
    line.strip()
    for line in lines
    if line.strip() and not line.startswith('#')
  ]
  return dependencies


def get_latest_version(package):
  """Get the latest version of a package using pip.
  """
  try:
    result = run(
      ['pip', 'index', 'versions', package],
      stdout=PIPE,
      stderr=PIPE,
      text=True
    )
    if result.returncode == 0 and "Available versions:" in result.stdout:
      match = re.search(r'Available versions: (.+)', result.stdout)
      if match:
        versions = match.group(1).split(', ')
        return versions[0]  # Return the latest version
    else:
      LOGGER.error(
        "failed to fetch versions for package: %s - %s",
        package, result.stderr
      )
  except Exception as e:
    LOGGER.error(
      "error fetching version for package: %s - %s",
      package, e
    )
  return None


def update_requirements(file_path):
  """Update the requirements.txt file with the latest versions.
  """
  dependencies = parse_requirements(file_path)
  updated_dependencies = []
  for dep in dependencies:
    package, _, current_version = dep.partition('==')
    latest_version = get_latest_version(package)
    if latest_version and latest_version != current_version:
      print(f"updating {package} from {current_version} to {latest_version}")
      updated_dependencies.append(f"{package}=={latest_version}")
    else:
      updated_dependencies.append(dep)
  with open(file_path, 'w') as f:
    f.write('\n'.join(updated_dependencies) + '\n')


def update_dependencies(requirements_file="requirements.txt"):
  """Update all dependencies listed in requirements.txt.
  """
  if not os.path.isfile(requirements_file):
    LOGGER.error("Requirements file not found: %s", requirements_file)
    return 1
  try:
    check_call([
      "python3", "-m", "pip", "install", "--upgrade", "-r",
      requirements_file
    ])
    LOGGER.info(
      "successfully updated dependencies from requirements file: %s",
      requirements_file
    )
    return 0
  except CalledProcessError as e:
    LOGGER.error(
      "failed to update dependencies from requirements file: %s - %s",
      requirements_file, e
    )
    return e.returncode


def write_latest_versions(requirements_file="requirements.txt"):
  """Write the latest versions of dependencies to the requirements file.

  Args:
    requirements_file: Path to the requirements.txt file.
  """
  dependencies = parse_requirements(requirements_file)

  updated = []
  for dep in dependencies:
    LOGGER.info("checking-dependency: %s", dep)

    package, _, current_version = dep.partition('==')

    latest_version = get_latest_version(package)

    if latest_version:
      LOGGER.info(
        "updating-package: %s from %s to %s",
        package, current_version or "not specified", latest_version
      )

      updated.append("{package}=={latest_version}".format(
        package=package, latest_version=latest_version
      ))
    else:
      LOGGER.warning(
        "no-latest-version-found: %s (current version: %s)",
        package, current_version or "not specified"
      )
      updated.append(dep)

  now = datetime.now().isoformat(timespec="seconds")
  user = getpass.getuser()
  comment = (
    "# Updated by depupdate.py on {now} by {user}\n"
    "# Do not edit this section manually.\n"
  ).format(now=now, user=user)

  LOGGER.info("writing-updated-dependencies: %s", requirements_file)

  with open(requirements_file, 'w') as f:
    f.write(comment)
    for n, dep in enumerate(updated, start=1):
      f.write(dep + '\n')
      LOGGER.debug("updated-dependency-%d: %s", n, dep)

  LOGGER.info(
    "requirements file updated with latest versions: %s",
    requirements_file
  )
  return 0


def check_dependencies(requirements_file="requirements.txt"):
  """Check if dependencies are up to date.
  """
  if not os.path.isfile(requirements_file):
    LOGGER.error("requirements-file-not-found: %s", requirements_file)
    return 1

  dependencies = parse_requirements(requirements_file)

  up_to_date = 0
  outdated = 0
  missing_version = 0

  for dep in dependencies:
    LOGGER.info("checking-dependency: %s", dep)

    package, _, current_version = dep.partition('==')
    latest_version = get_latest_version(package)

    if not current_version:
      LOGGER.warning(
        "no-package-version-specified: '%s' (latest: '%s')",
        package, latest_version or "unknown"
      )
      missing_version += 1
    elif latest_version and latest_version != current_version:
      LOGGER.warning(
        "package-is-outdated: name='%s', current-version='%s', "
        "latest-version='%s'",
        package, current_version, latest_version
      )
      outdated += 1
    else:
      LOGGER.info(
        "package-is-up-to-date: name='%s', version='%s'",
        package, current_version
      )
      up_to_date += 1

  LOGGER.info(
    "dependency-check-summary: up-to-date=%d outdated=%d missing-version=%d",
    up_to_date, outdated, missing_version
  )

  if outdated > 0 or missing_version > 0:
    LOGGER.error(
      "some dependencies are outdated or missing versions - "
      "please update your requirements file"
    )
    return 1

  LOGGER.info("all dependencies are up-to-date")
  return 0


def main(*args):
  """CLI Entry Point."""
  path = os.path.abspath(__file__)
  prog = os.path.splitext(os.path.basename(path))[0]

  parser = argument_parser(prog=prog, description=__doc__)
  args = parser.parse_args(args if args else None)

  # setup logging
  level = logging.DEBUG if args.verbose else logging.INFO
  logging.basicConfig(level=level, filename=args.logfile)
  LOGGER.setLevel(level)

  LOGGER.info("starting: %s (v%s)", prog, __version__)
  LOGGER.debug(
    "parsed arguments: %s",
    json.dumps(_serialize_args(args), indent=2, sort_keys=True)
  )

  if args.update:
    LOGGER.info("updating-dependencies: %s", args.requirements_file)
    return_code = update_dependencies(args.requirements_file)

  elif args.check:
    if args.write:
      LOGGER.info(
        "checking and updating requirements file: %s",
        args.requirements_file
      )
      return_code = write_latest_versions(args.requirements_file)
    else:
      LOGGER.info("checking-dependencies: %s", args.requirements_file)
      return_code = check_dependencies(args.requirements_file)

  else:
    LOGGER.error("no-action-specified: use --update or --check")
    parser.print_help()
    return_code = 1

  LOGGER.info(
    "finished: %s (v%s) exiting with return code: %s",
    prog, __version__, return_code
  )

  if args.input and not args.input.closed:
    args.input.close()
  if args.output and not args.output.closed:
    args.output.close()

  return return_code


if __name__ == "__main__":
  sys.exit(main())
