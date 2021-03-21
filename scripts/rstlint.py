#!/usr/bin/env python
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

# TODO:
#  Wrong versions in versionadded/changed.
#  Wrong markup after versionchanged directive.

LOGGER = logging.getLogger(__name__)

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


def checker(*suffixes, **kwargs):
  """Decorator to register a function as a checker.
  """

  def _deco(func):
    for suffix in suffixes:
      CHECKERS.setdefault(suffix, []).append(func)
    for prop in CHECKER_PROPS:
      setattr(func, prop, kwargs.get(prop, CHECKER_PROPS[prop]))
    return func

  return _deco


@checker(".py", severity=4)
def check_syntax(fn, lines):
  """Check Python examples for valid syntax.

  Yields:
    tuple[int,str]: Line Number and Message.
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
  """Check for suspicious reST constructs.

  Yields:
    tuple[int,str]: Line Number and Message.
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
  """Check for line length; this checker is not _run by default.

  Yields:
    tuple[int,str]: Line Number and Message.
  """
  for lno, line in enumerate(lines):
    if len(line) > 81:
      # do not complain about tables, links or function signatures
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
    tuple[int,str]: Line Number and Message.
  """
  for lno, line in enumerate(lines):
    if LEAKED_MARKDOWN_RE.search(line):
      yield lno + 1, "possibly leaked markup: {0!r}".format(line)


def rstlint(path, false_pos=False, ignore=None, severity=1, verbose=False):
  """Check for stylistic and formal issues in .rst and .py files
  included in the documentation.

  Args:
    path (str): Path to search for files.
    false_pos (bool): Enable checkers that yield many false positives
    ignore (list): Ignore subdir or file path
    severity (int): Only show problems with severity >= sev
    verbose (bool): Verbose (print all checked file names)

  Returns:
    defaultdict[int,int]: Severity and Error Hit Count.
  """
  count = defaultdict(int)
  for root, dirs, files in os.walk(path):
    # ignore subdirectories in ignore list
    if abspath(root) in ignore:
      del dirs[:]
      continue

    for fn in files:
      fn = join(root, fn)
      if fn[:2] == "./":
        fn = fn[2:]

      if abspath(fn) in ignore:
        continue  # ignore files in ignore list

      checker_list = CHECKERS.get(splitext(fn)[1], None)
      if not checker_list:
        continue

      if verbose:
        sys.stdout.write("[-] CHECKING: {0}...\n".format(fn))

      try:
        with open(fn) as f:
          lines = list(f)
      except (UnicodeDecodeError, IOError, OSError) as err:
        sys.stderr.write("[!] ERROR: {0}: cannot open: {1}\n".format(fn, err))
        count[4] += 1
        continue

      for _checker in checker_list:
        if _checker.falsepositives and not false_pos:
          continue

        c_sev = _checker.severity
        if c_sev >= severity:
          for n, msg in _checker(fn, lines):
            sys.stdout.write(
                "[{0:d}] PROBLEMS: {1}:{2:d}: {3}\n".format(c_sev, fn, n, msg)
            )
            count[c_sev] += 1

  if not count:
    if severity > 1:
      sys.stdout.write(
          "No Problems With Severity >= {0:d} Found.\n".format(severity)
      )
    else:
      sys.stdout.write("No Problems Found.\n")
  else:
    for severity in sorted(count):
      number = count[severity]
      sys.stdout.write("{0:d} Problem{1} With Severity {2:d} Found.\n".format(
          number, "s" if number > 1 else "", severity
      ))
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
      "ignore": [],
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
    sys.stderr.write("ERROR: path {0} does not exist\n".format(arg_d["path"]))
    return 2
  return arg_d


def main():
  """Entry Point
  """
  import signal

  def _shutdown_handler(signum, _):
    """Handle Shutdown.

    Args:
      signum (int): Signal Number,
      _ (types.FrameType): Interrupted Stack Frame.
    """
    sys.stderr.write("\b\b\n")
    LOGGER.debug("Received Shutdown Signal: signum=%d", signum)
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
  return int(bool(rstlint(**args_dict)))


if __name__ == "__main__":
  sys.exit(main())
