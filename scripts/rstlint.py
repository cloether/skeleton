#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""rst.py

Check for stylistic and formal issues in .rst and .py files included
in the documentation.

References:
  https://raw.githubusercontent.com/python/devguide/master/tools/rstlint.py
"""
from __future__ import with_statement, unicode_literals

import getopt
import os
import re
import sys
from collections import defaultdict
from os.path import join, splitext, abspath, exists, basename

# TODO:
#  wrong versions in versionadded/changed
#  wrong markup after versionchanged directive

directives = [
    # standard docutils ones
    'admonition',
    'attention',
    'caution',
    'class',
    'compound',
    'container',
    'contents',
    'csv-table',
    'danger',
    'date',
    'default-role',
    'epigraph',
    'error',
    'figure',
    'footer',
    'header',
    'highlights',
    'hint',
    'image',
    'important',
    'include',
    'line-block',
    'list-table',
    'meta',
    'note',
    'parsed-literal',
    'pull-quote',
    'raw',
    'replace',
    'restructuredtext-test-directive',
    'role',
    'rubric',
    'sectnum',
    'sidebar',
    'table',
    'target-notes',
    'tip',
    'title',
    'topic',
    'unicode',
    'warning',
    # Sphinx and Python docs custom ones
    'acks',
    'attribute',
    'autoattribute',
    'autoclass',
    'autodata',
    'autoexception',
    'autofunction',
    'automethod',
    'automodule',
    'centered',
    'cfunction',
    'class',
    'classmethod',
    'cmacro',
    'cmdoption',
    'cmember',
    'code-block',
    'confval',
    'cssclass',
    'ctype',
    'currentmodule',
    'cvar',
    'data',
    'decorator',
    'decoratormethod',
    'deprecated-removed',
    'deprecated(?!-removed)',
    'describe',
    'directive',
    'doctest',
    'envvar',
    'event',
    'exception',
    'function',
    'glossary',
    'highlight',
    'highlightlang',
    'impl-detail',
    'index',
    'literalinclude',
    'method',
    'miscnews',
    'module',
    'moduleauthor',
    'opcode',
    'pdbcommand',
    'productionlist',
    'program',
    'role',
    'sectionauthor',
    'seealso',
    'sourcecode',
    'staticmethod',
    'tabularcolumns',
    'testcode',
    'testoutput',
    'testsetup',
    'toctree',
    'todo',
    'todolist',
    'versionadded',
    'versionchanged',
]

all_directives = '(' + '|'.join(directives) + ')'

# noinspection RegExpAnonymousGroup
seems_directive_re = re.compile(
    r'(?<!\.)\.\. %s([^a-z:]|:(?!:))' % all_directives
)

# noinspection RegExpAnonymousGroup
default_role_re = re.compile(r'(^| )`\w([^`]*?\w)?`($| )')

leaked_markup_re = re.compile(r'[a-z]::\s|`|\.\.\s*\w+:')

checkers = {}

checker_props = {
    'severity': 1,
    'falsepositives': False
}


def checker(*suffixes, **kwargs):
  """Decorator to register a function as a checker.
  """

  def deco(func):
    for suffix in suffixes:
      checkers.setdefault(suffix, []).append(func)
    for prop in checker_props:
      setattr(func, prop, kwargs.get(prop, checker_props[prop]))
    return func

  return deco


@checker('.py', severity=4)
def check_syntax(fn, lines):
  """Check Python examples for valid syntax.
  """
  code = ''.join(lines)
  if '\r' in code:
    if os.name != 'nt':
      yield 0, '\\r in code file'
    code = code.replace('\r', '')
  try:
    compile(code, fn, 'exec')
  except SyntaxError as err:
    yield err.lineno, 'not compilable: %s' % err


# noinspection PyUnusedLocal
@checker('.rst', severity=2)
def check_suspicious_constructs(fn, lines):
  """Check for suspicious reST constructs.
  """
  in_prod = False
  for lno, line in enumerate(lines):
    if seems_directive_re.search(line):
      yield lno + 1, 'comment seems to be intended as a directive'
    if '.. productionlist::' in line:
      in_prod = True
    elif not in_prod and default_role_re.search(line):
      yield lno + 1, 'default role used'
    elif in_prod and not line.strip():
      in_prod = False


# noinspection PyUnusedLocal
@checker('.py', '.rst')
def check_whitespace(fn, lines):
  """Check for whitespace and line length issues.
  """
  for lno, line in enumerate(lines):
    if '\r' in line:
      yield lno + 1, '\\r in line'
    if '\t' in line:
      yield lno + 1, 'OMG TABS!!!1'
    if line[:-1].rstrip(' \t') != line[:-1]:
      yield lno + 1, 'trailing whitespace'


# noinspection PyUnusedLocal
@checker('.rst', severity=0)
def check_line_length(fn, lines):
  """Check for line length; this checker is not run by default.
  """
  for lno, line in enumerate(lines):
    if len(line) > 81:
      # don't complain about tables, links and function signatures
      if (
          line.lstrip()[0] not in '+|' and 'http://' not in line
          and not line.lstrip().startswith(('.. function',
                                            '.. method',
                                            '.. cfunction')
                                           )):
        yield lno + 1, "line too long"


# noinspection PyUnusedLocal
@checker('.html', severity=2, falsepositives=True)
def check_leaked_markup(fn, lines):
  """Check HTML files for leaked reST markup.

  Notes:
    This only works if the HTML files have been built.
  """
  for lno, line in enumerate(lines):
    if leaked_markup_re.search(line):
      yield lno + 1, 'possibly leaked markup: %r' % line


def main(argv):
  """CLI Entry Point
  """
  usage = """%s
Usage:
  %s [-v] [-f] [-s sev] [-i path]* [path]

Options:
  -v       verbose (print all checked file names)
  -f       enable checkers that yield many false positives
  -s sev   only show problems with severity >= sev
  -i path  ignore subdir or file path
""" % (__doc__, basename(argv[0]))
  try:
    opts, args = getopt.getopt(argv[1:], 'vfs:i:')
  except getopt.GetoptError:
    sys.stderr.write("%s\n" % usage)
    return 2
  verbose = False
  severity = 1
  ignore = []
  false_pos = False
  for opt, val in opts:
    if opt == '-v':
      verbose = True
    elif opt == '-f':
      false_pos = True
    elif opt == '-s':
      severity = int(val)
    elif opt == '-i':
      ignore.append(abspath(val))
  if len(args) == 0:
    path = '.'
  elif len(args) == 1:
    path = args[0]
  else:
    sys.stderr.write("%s\n" % usage)
    return 2
  if not exists(path):
    sys.stderr.write('Error: path %s does not exist\n' % path)
    return 2
  count = defaultdict(int)
  for root, dirs, files in os.walk(path):
    # ignore subdirectories in ignore list
    if abspath(root) in ignore:
      del dirs[:]
      continue
    for fn in files:
      fn = join(root, fn)
      if fn[:2] == './':
        fn = fn[2:]
      # ignore files in ignore list
      if abspath(fn) in ignore:
        continue
      ext = splitext(fn)[1]
      checker_list = checkers.get(ext, None)
      if not checker_list:
        continue
      if verbose:
        sys.stdout.write('Checking %s...\n' % fn)
      try:
        with open(fn, encoding='utf-8') as f:
          lines = list(f)
      except (IOError, OSError) as err:
        sys.stderr.write('%s: cannot open: %s\n' % (fn, err))
        count[4] += 1
        continue
      for _checker in checker_list:
        if _checker.falsepositives and not false_pos:
          continue
        c_sev = _checker.severity
        if c_sev >= severity:
          for lno, msg in _checker(fn, lines):
            sys.stdout.write('[%d] %s:%d: %s\n' % (c_sev, fn, lno, msg))
            count[c_sev] += 1
  if verbose:
    sys.stdout.write("\n")
  if not count:
    if severity > 1:
      sys.stdout.write('No problems with severity >= %d found.\n' % severity)
    else:
      sys.stdout.write('No problems found.\n')
  else:
    for severity in sorted(count):
      number = count[severity]
      sys.stdout.write(
          '%d problem%s with severity %d found.\n'
          % (number, 's' if number > 1 else '', severity)
      )
  return int(bool(count))


if __name__ == '__main__':
  sys.exit(main(sys.argv))
