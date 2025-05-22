#!/usr/bin/env python3
# coding=utf8
"""change.py

Generate a new changelog entry.

Usage
=====

To generate a new changelog entry::

  scripts/new-change

This will open up a file in your editor (via the ``EDITOR`` env var).
You will see this template::
  # Type should be one of: feature, bugfix
  type:

  # Category is the high level feature area.
  # This can be a service identifier (e.g. ``s3``),
  # or something like: ``Paginator``.
  category:

  # A brief description of the change.  You can use GitHub style
  # references to issues such as "fixes #489", "skeleton/skeleton#100", etc.
  # These will get automatically replaced with the correct link.
  description:


Fill in the appropriate values, save, and exit the editor.
Make sure to commit these changes as part of your pull request.

If, when your editor is open, you decide do not want to add
a changelog entry, save an empty file and no entry will be
generated.

Notes:
  You can then use the ``scripts/gen-changelog`` to generate the
  CHANGELOG.rst file.
"""
from __future__ import absolute_import, print_function, unicode_literals

import json
import os
import random
import re
import string
import subprocess
import sys
from tempfile import NamedTemporaryFile

_VALID_CHARS = set(string.ascii_letters + string.digits)
_ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

CHANGE_DIR = os.path.abspath(os.path.join(_ROOT_DIR, '.changes'))
CHANGE_TYPES = ('bugfix', 'feature', 'enhancement', 'api-change')
CHANGE_TEMPLATE = """\
# Type should be one of: feature, bugfix, enhancement, api-change
#   feature:      A larger feature or change in behavior, usually resulting in a
#                 minor version bump.
#   bugfix:       Fixing a bug in an existing code path.
#   enhancement:  Small change to an underlying implementation detail.
#   api-change:   Changes to a modeled API.
type: {change_type}

# Category is the high level feature area.
# This can be a service identifier (e.g ``s3``), or something like: Paginator.
category: {category}

# A brief description of the change.  You can use github style references to
# issues such as "fixes #489", "repo-base/repo-name#100", etc.  These will get
# automatically replaced with the correct link.
description: {description}
"""


def new_changelog_entry(args):
  """Changelog values come from one of two places.

  Either all values are provided on the command line,
  or we open a text editor and let the user provide
  enter their values.

  Args:
    args (argparse.Namespace): Parsed argparse arguments.

  Returns:
    int: 0 if success otherwise 1.
  """
  # get values from change content
  parsed_values = (
    {
      'type': args.change_type,
      'category': args.category,
      'description': args.description
    }
    if all_values_provided(args)
    else get_values_from_editor(args)
  )

  # exit if empty values are found
  if has_empty_values(parsed_values):
    sys.stderr.write("empty changelog values received.\n")
    sys.stderr.write("skipping entry creation.\n")
    return 1

  # replace issue references with correctly formatted issue
  # link references.
  replace_issue_references(parsed_values, args.repo)

  # write the new change.
  write_new_change(parsed_values)
  return 0


def has_empty_values(parsed_values):
  """Check for empty values.

  Returns:
    bool: True if any values are empty, otherwise False.
  """
  return not (
      parsed_values.get('type')
      and parsed_values.get('category')
      and parsed_values.get('description')
  )


def all_values_provided(args):
  """Check if all values are provided.
  """
  return (
      args.change_type
      and args.category
      and args.description
  )


def get_values_from_editor(args, template=CHANGE_TEMPLATE):
  """Get values from editor.
  """
  with NamedTemporaryFile('w') as f:
    contents = template.format(
      change_type=args.change_type,
      category=args.category,
      description=args.description,
    )
    f.write(contents)
    f.flush()

    env = os.environ
    editor = env.get('VISUAL', env.get('EDITOR', 'vim'))

    p = subprocess.Popen('{0} {1}'.format(editor, f.name), shell=True)
    p.communicate()

    with open(f.name) as _f:
      filled_in_contents = _f.read()
      parsed_values = parse_filled_in_contents(filled_in_contents)

    return parsed_values


def replace_issue_references(parsed, repo_name):
  """Replace issue reference with issue url.
  """
  description = parsed['description']

  def url(repository_name, issue):
    """Make GitHub issue url
    """
    issue_number = issue[1:]
    return '`{0} <https://github.com/{1}/issues/{2}>`__'.format(
      issue,
      repository_name,
      issue_number
    )

  def link(match):
    """Link GitHub issue.

    Args:
      match (re.Match): Regex match.

    Returns:
      str: Github issue link text.
    """
    return url(match.group(), repo_name)

  parsed['description'] = re.sub(r'#\d+', link, description)


def write_new_change(parsed_values):
  """Write new changelog entry.

  Args:
    parsed_values (dict): Change entry dictionary.
  """
  if not os.path.isdir(CHANGE_DIR):
    os.makedirs(CHANGE_DIR)

  # Assume that new changes go into the next release.
  dirname = os.path.join(CHANGE_DIR, 'next-release')
  if not os.path.isdir(dirname):
    os.makedirs(dirname)

  # Need to generate a unique filename for this change.
  # We will try a couple of things until we get a unique match.
  category = parsed_values['category']

  def _valid_char(x):
    return x in _VALID_CHARS

  filename = '{type_name}-{summary}'.format(
    type_name=parsed_values['type'],
    summary=''.join(filter(_valid_char, category))
  )

  possible_filename = os.path.join(
    dirname, '{0}-{1}.json'.format(filename, random.randint(1, 100000))
  )

  while os.path.isfile(possible_filename):
    possible_filename = os.path.join(
      dirname, '{0}-{1}.json'.format(filename, random.randint(1, 100000))
    )

  with open(possible_filename, 'w') as f:
    f.write(json.dumps(parsed_values, indent=2) + "\n")


def parse_filled_in_contents(contents):
  """Parse filled in file contents and returns parsed dict.

  Args:
    contents (str): Change contents.

  Returns:
    dict: Parsed contents dictionary. Example:
      {
        "type": "bugfix",
        "category": "category",
        "description": "This is a description"
      }
  """
  if not contents.strip():
    return {}

  parsed = {}
  lines = iter(contents.splitlines())

  for line in (line.strip() for line in lines):
    if line.startswith('#'):
      continue

    if 'type' not in parsed and line.startswith('type:'):
      parsed['type'] = line.split(':')[1].strip()

    elif 'category' not in parsed and line.startswith('category:'):
      parsed['category'] = line.split(':')[1].strip()

    elif 'description' not in parsed and line.startswith('description:'):
      # Assume that everything until the end of the file is part
      # of the description, so we can break once we pull in the
      # remaining lines.
      first_line = line.split(':')[1].strip()
      full_description = '\n'.join([first_line] + list(lines))
      parsed['description'] = full_description.strip()
      break

  return parsed


def main():
  """CLI Entry Point.

  Returns:
    int: 0 if success otherwise 1.
  """
  from argparse import ArgumentParser

  parser = ArgumentParser()
  parser.add_argument(
    '-t', '--type',
    dest='change_type',
    default='',
    choices=CHANGE_TYPES
  )
  parser.add_argument(
    '-c', '--category',
    dest='category',
    default=''
  )
  parser.add_argument(
    '-d', '--description',
    dest='description',
    default=''
  )
  parser.add_argument(
    '-r', '--repo',
    default='owner/repo',
    help='Optional repo name, e.g: owner/repo'
  )
  args = parser.parse_args()
  return new_changelog_entry(args)


if __name__ == '__main__':
  sys.exit(main())
