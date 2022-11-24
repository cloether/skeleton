#!/usr/bin/env python3
# coding=utf8
"""winbuild.py

Compile module as a Windows executable.
"""
from __future__ import absolute_import, print_function, unicode_literals

import os
import subprocess
from distutils import msvc9compiler  # noqa

DEFAULT_ARCH = "x86"
DEFAULT_VC_VERSION = None


def win_compile(filename, output_filename, arch=DEFAULT_ARCH,
                vc_ver=DEFAULT_VC_VERSION):
  """Compile Windows Program.

  Raises:
    Exception: Raised when compilation results in a non-zero returncode.

  Args:
    filename (str): Filename
    output_filename (str): Output filename
    arch (str): Architecture
    vc_ver (str): Compiler Version
  """
  if vc_ver is None:
    msvc_ver = os.getenv("MSVCVER")
    vc_ver = float(msvc_ver) if msvc_ver else msvc9compiler.get_build_version()

  vcvars = msvc9compiler.find_vcvarsall(vc_ver)

  if not vcvars:
    # VS 2008 Standard Edition doesn't have vcvarsall.bat
    reg_path = r"{0}\Setup\VC".format(msvc9compiler.VS_BASE % vc_ver)

    vcvars = os.path.join(
        msvc9compiler.Reg.get_value(reg_path, "productdir"),
        "bin", "vcvars{0:d}.bat".format(arch == "x86" and 32 or 64)
    )

  path = os.path.splitext(output_filename)

  obj_filename = "{0}.obj".format(path[0])

  command = "\"{0}\" {1} & cl {2} /Fe{3} /Fo{4}".format(
      vcvars, arch, filename, output_filename, obj_filename
  )

  p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

  try:
    stdout, stderr = p.communicate()
    if p.wait() != 0:
      raise Exception(stderr.decode("mbcs"))
    os.remove(obj_filename)
  finally:
    p.stdout.close()
    p.stderr.close()


def _arg_parser():
  """Create Argument Parser

  Returns:
    argparse.ArgumentParser: Argument Parser
  """
  from argparse import ArgumentParser

  parser = ArgumentParser()
  parser.add_argument("filename")
  parser.add_argument("output-filename")
  parser.add_argument("--arch", default="x86")
  parser.add_argument("--vc-ver")
  return parser


def main():
  """Entry Point
  """
  parser = _arg_parser()
  args = parser.parse_args()
  try:
    win_compile(
        args.filename,
        args.output_filename,
        arch=args.arch,
        vc_ver=args.vc_ver
    )
  except Exception as e:
    sys.stderr.write("{0}\n".format(e))
    return 1
  return 0


if __name__ == '__main__':
  import sys

  sys.exit(main())
