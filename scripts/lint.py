#!/usr/bin/env python3
# coding=utf8
"""rstlint.py

Check for stylistic and formal issues in .rst and .py files
included in the documentation.

Usage:
  rstlint.py [-vf] [-s SEVERITY] [-i IGNORED_PATH*] PATH

Options:
  -v       verbose (print all checked file names)
  -f       enable checkers that yield many false positives
  -s sev   only show problems with severity >= sev
  -i path  ignore subdir or file path

References:
  https://raw.githubusercontent.com/python/devguide/master/tools/rstlint.py
"""
from __future__ import print_function, unicode_literals, with_statement

import getopt
import logging
import os
import re
import sys
from collections import defaultdict
from os.path import abspath, exists, join, splitext

# TODO: Wrong versions in versionadded/changed.
#  Wrong markup after versionchanged directive.

LOGGER = logging.getLogger(__name__)

PARENT_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(PARENT_DIR, '..'))

CHECKERS = {}

CHECKER_PROPS = {"severity": 1, "falsepositives": False}

DEFAULT_ROLE_RE = re.compile(r"(?:^| )`\w(?P<default_role>[^`]*?\w)?`(?:$| )")

DIRECTIVES = [
  # standard docutils ones
  "admonition",
  "attention",
  "caution",
  "class",
  "compound",
  "container",
  "contents",
  "csv-table",
  "danger",
  "date",
  "default-role",
  "epigraph",
  "error",
  "figure",
  "footer",
  "header",
  "highlights",
  "hint",
  "image",
  "important",
  "include",
  "line-block",
  "list-table",
  "meta",
  "note",
  "parsed-literal",
  "pull-quote",
  "raw",
  "replace",
  "restructuredtext-test-directive",
  "role",
  "rubric",
  "sectnum",
  "sidebar",
  "table",
  "target-notes",
  "tip",
  "title",
  "topic",
  "unicode",
  "warning",
  # Sphinx and Python docs custom ones
  "acks",
  "attribute",
  "autoattribute",
  "autoclass",
  "autodata",
  "autoexception",
  "autofunction",
  "automethod",
  "automodule",
  "centered",
  "cfunction",
  "class",
  "classmethod",
  "cmacro",
  "cmdoption",
  "cmember",
  "code-block",
  "confval",
  "cssclass",
  "ctype",
  "currentmodule",
  "cvar",
  "data",
  "decorator",
  "decoratormethod",
  "deprecated-removed",
  "deprecated(?!-removed)",
  "describe",
  "directive",
  "doctest",
  "envvar",
  "event",
  "exception",
  "function",
  "glossary",
  "highlight",
  "highlightlang",
  "impl-detail",
  "index",
  "literalinclude",
  "method",
  "miscnews",
  "module",
  "moduleauthor",
  "opcode",
  "pdbcommand",
  "productionlist",
  "program",
  "role",
  "sectionauthor",
  "seealso",
  "sourcecode",
  "staticmethod",
  "tabularcolumns",
  "testcode",
  "testoutput",
  "testsetup",
  "toctree",
  "todo",
  "todolist",
  "versionadded",
  "versionchanged",
]

ALL_DIRECTIVES = "({0})".format("|".join(DIRECTIVES))

LEAKED_MARKDOWN_RE = re.compile(r"[a-z]::\s|`|\.\.\s*\w+:")
SEEMS_DIRECTIVE_RE = re.compile(
  r"(?<!\.)\.\. {0}(?P<directive>[^a-z:]|:(?!:))".format(
    ALL_DIRECTIVES
  )
)

ENV_DIRS = frozenset(filter(None, [
  os.path.join(ROOT_DIR, 'env'),
  os.path.join(ROOT_DIR, 'env27'),
  os.path.join(ROOT_DIR, '.tox'),
  os.getenv('VIRTUAL_ENV', None),
  os.path.join(ROOT_DIR, 'venv'),
  os.path.join(ROOT_DIR, '.venv'),
  os.path.join(ROOT_DIR, '.idea'),
  os.path.join(ROOT_DIR, '.git'),
  os.path.join(ROOT_DIR, '.github'),
  "__pycache__"
]))


def checker(*suffixes, **kwargs):
  """Decorator to register a function as a checker.
  """

  def _inner(func):
    for suffix in suffixes:
      CHECKERS.setdefault(suffix, []).append(func)
    for prop in CHECKER_PROPS:
      setattr(func, prop, kwargs.get(prop, CHECKER_PROPS[prop]))
    return func

  return _inner


@checker(".py", severity=4)
def check_syntax(fn, lines):
  """Check Python examples for valid syntax.

  Yields:
    (tuple of int,str): Line Number and Message.
  """
  code = "".join(lines)
  if "\r" in code:
    if os.name != "nt":
      yield 0, "\\r in code file"
    code = code.replace("\r", "")
  try:
    compile(code, fn, "exec")
  except SyntaxError as err:
    yield err.lineno, "not compilable: {0}".format(err)


@checker(".rst", severity=2)
def check_suspicious_constructs(_, lines):
  """Check for suspicious restructured text constructs.

  Yields:
    (tuple of int,str): Line Number and Message.
  """
  in_prod = False
  for lno, line in enumerate(lines):
    if SEEMS_DIRECTIVE_RE.search(line):
      yield lno + 1, "comment seems to be intended as a directive"
    if ".. productionlist::" in line:
      in_prod = True
    elif not in_prod and DEFAULT_ROLE_RE.search(line):
      yield lno + 1, "default role used"
    elif in_prod and not line.strip():
      in_prod = False


@checker(".py", ".rst")
def check_whitespace(_, lines):
  """Check for whitespace and line length issues.

  Yields:
    (tuple of int,str): Line Number and Message.
  """
  for lno, line in enumerate(lines):
    if "\r" in line:
      yield lno + 1, "\\r in line"
    if "\t" in line:
      yield lno + 1, "OMG TABS!!!1"
    if line[:-1].rstrip(" \t") != line[:-1]:
      yield lno + 1, "trailing whitespace"


@checker(".rst", severity=0)
def check_line_length(_, lines):
  """Check for line length.

  Notes:
    This checker is NOT run by default.

  Yields:
    (tuple of int,str): Line Number and Message.
  """
  for lno, line in enumerate(lines):
    if len(line) > 81:
      # do not complain about tables, links or function signatures
      # noinspection HttpUrlsUsage
      if (
          line.lstrip()[0] not in "+|"
          and "http://" not in line
          and not line.lstrip().startswith((".. function",
                                            ".. method",
                                            ".. cfunction"))
      ):
        yield lno + 1, "line too long"


@checker(".html", severity=2, falsepositives=True)
def check_leaked_markup(_, lines):
  """Check HTML files for leaked reST markup.

  Notes:
    This only works if the HTML files have been built.

  Yields:
    (tuple of int,str): Line Number and Message.
  """
  for lno, line in enumerate(lines):
    if LEAKED_MARKDOWN_RE.search(line):
      yield lno + 1, "possibly leaked markup: {0!r}".format(line)


def lint(path, false_pos=False, ignore=ENV_DIRS, severity=1, verbose=False):
  """Check for stylistic and formal issues in .rst and .py files
  included in the documentation.

  Args:
    path (str): Path to search for files.
    false_pos (bool): Enable checkers that yield many false positives
    ignore (list): Ignore subdir or file path
    severity (int): Only show problems with severity >= sev
    verbose (bool): Verbose (print all checked file names)

  Returns:
    (defaultdict of int,int): Severity and Error Hit Count.
  """
  count = defaultdict(int)
  totals = {
    "checked": 0,
    "skipped": 0,
    "ignored": 0,
    "errors": 0,
    "total": 0
  }

  for root, dirs, files in os.walk(path):

    # ignore subdirectories in ignore list
    if abspath(root) in ignore:
      if verbose:
        sys.stdout.write("[-] IGNORING: {0}\n".format(root))
      del dirs[:]
      totals["ignored"] += 1
      continue

    if os.path.basename(os.path.dirname(abspath(root))) in ignore:
      if verbose:
        sys.stdout.write("[-] IGNORING: {0}\n".format(root))
      del dirs[:]
      totals["total"] += 1
      continue

    files.sort()
    for fn in files:
      totals["total"] += 1

      fn = join(root, fn)
      if fn[:2] == "./":
        fn = fn[2:]

      if abspath(fn) in ignore:
        if verbose:
          sys.stdout.write("[-] IGNORING: {0}\n".format(fn))
        totals["ignored"] += 1
        continue  # ignore files in ignore list

      checker_list = CHECKERS.get(splitext(fn)[1], None)
      if not checker_list:
        if verbose:
          sys.stdout.write("[-] SKIPPING: {0}\n".format(fn))
        totals["skipped"] += 1
        continue

      if verbose:
        sys.stdout.write("[-] CHECKING: {0}\n".format(fn))
      totals["checked"] += 1

      # LOGGER.debug("checking: %s", fn)

      try:
        with open(fn) as f:
          lines = list(f)
      except (UnicodeDecodeError, IOError, OSError) as err:
        # LOGGER.error("%s cannot open %s", fn, err)
        sys.stderr.write("[!] ERROR: {0}: cannot open: {1}\n".format(fn, err))
        count[4] += 1
        totals["errors"] += 1
        continue

      for _checker in checker_list:
        if _checker.falsepositives and not false_pos:
          continue
        c_sev = _checker.severity
        if c_sev >= severity:
          for n, msg in _checker(fn, lines):
            sys.stdout.write("[{0:d}] PROBLEMS: {1}:{2:d}: {3}\n".format(c_sev, fn, n, msg))
            count[c_sev] += 1

  if not count:
    if severity > 1:
      sys.stdout.write("[-] No Problems With Severity >= {0:d} Found.\n".format(severity))
    else:
      sys.stdout.write("[-] No Problems Found.\n")
  else:
    for severity in sorted(count):
      number = count[severity]
      sys.stdout.write("{0:d} Problem{1} With Severity {2:d} Found.\n".format(
        number, "s" if number > 1 else "", severity
      ))

  if verbose:
    sys.stdout.write("\n[-] Summary:\n")
    sys.stdout.write("  Total:   {0}\n".format(totals["total"]))
    sys.stdout.write("  Checked: {0}\n".format(totals["checked"]))
    sys.stdout.write("  Skipped: {0}\n".format(totals["skipped"]))
    sys.stdout.write("  Ignored: {0}\n".format(totals["ignored"]))
    sys.stdout.write("  Errors:  {0}\n".format(totals["errors"]))
    sys.stdout.write(os.linesep)
  return count


def _parse_args(argv):
  """Parse CLI Arguments.
  """
  try:
    opts, args = getopt.getopt(argv[1:], "vfs:i:")
  except getopt.GetoptError:
    sys.stderr.write(__doc__)
    return 2

  arg_d = {
    "verbose": False,
    "severity": 1,
    "ignore": ENV_DIRS,
    "false_pos": False,
  }
  for opt, val in opts:
    if opt == "-v":
      arg_d["verbose"] = True
    elif opt == "-f":
      arg_d["false_pos"] = True
    elif opt == "-s":
      arg_d["severity"] = int(val)
    elif opt == "-i":
      arg_d["ignore"].append(abspath(val))

  if len(args) == 0:
    arg_d["path"] = "."
  elif len(args) == 1:
    arg_d["path"] = args[0]
  else:
    sys.stderr.write(__doc__)
    return 2

  if not exists(arg_d["path"]):
    sys.stderr.write("[!] ERROR: path {0} does not exist\n".format(arg_d["path"]))
    return 2

  if arg_d["verbose"]:
    sys.stdout.write("[-] ARGUMENTS:\n")
    sys.stdout.write("  path: {0}\n".format(arg_d["path"]))
    sys.stdout.write("  severity: {0}\n".format(arg_d["severity"]))
    sys.stdout.write("  false positives: {0}\n".format(arg_d["false_pos"]))
    sys.stdout.write("  ignore: \n")
    for path in arg_d["ignore"]:
      sys.stdout.write("    {0}\n".format(path))
    sys.stdout.write("  verbose: {0}\n".format(arg_d["verbose"]))
    sys.stdout.write(os.linesep)

    sys.stdout.write("[-] CHECKERS:\n")
    for suffix, checkers in CHECKERS.items():
      sys.stdout.write("  {0} ({1})\n".format(suffix, len(checkers)))
      for _checker in checkers:
        sys.stdout.write("    {0}: severity={1} falsepositives={2}\n".format(
          _checker.__name__, _checker.severity, _checker.falsepositives
        ))
    sys.stdout.write(os.linesep)
  return arg_d


def main():
  """Entry Point
  """
  import signal

  logging.basicConfig(level=logging.INFO)

  def _shutdown_handler(signum, _):
    """Handle Shutdown.

    Args:
      signum (int): Signal Number,
      _ (types.FrameType): Interrupted Stack Frame.
    """
    sys.stderr.write("\b\b\n")
    LOGGER.debug("received shutdown signal: signum=%d", signum)
    sys.exit(signum)

  signal.signal(signal.SIGTERM, _shutdown_handler)
  signal.signal(signal.SIGINT, _shutdown_handler)

  if os.name == "nt":
    signal.signal(signal.SIGBREAK, _shutdown_handler)

  args_dict = _parse_args(sys.argv)
  if not isinstance(args_dict, dict):
    return args_dict

  if args_dict["verbose"]:
    logging.basicConfig(level=logging.DEBUG)

  return int(bool(lint(**args_dict)))


if __name__ == "__main__":
  sys.exit(main())
