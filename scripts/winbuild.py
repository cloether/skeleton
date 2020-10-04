# coding=utf8
"""winbuild.py
"""
from __future__ import print_function, unicode_literals

import os
import subprocess
from distutils import msvc9compiler  # noqa


def win_compile(filename, output_filename, arch='x86', vc_ver=None):
  """Compile Windows Program

  Args:
    filename (str): Filename
    output_filename (str): Output filename
    arch (str): Architecture
    vc_ver (str): Compiler Version
  """
  if vc_ver is None:
    vc_ver = (
        float(os.getenv('MSVCVER'))
        if os.getenv('MSVCVER')
        else msvc9compiler.get_build_version()
    )

  vcvars = msvc9compiler.find_vcvarsall(vc_ver)

  if not vcvars:
    # VS 2008 Standard Edition doesn't have vcvarsall.bat
    vs_base = msvc9compiler.VS_BASE % vc_ver
    reg_path = r"{0}\Setup\VC".format(vs_base)

    product_dir = msvc9compiler.Reg.get_value(reg_path, "productdir")

    bat = 'vcvars%d.bat' % (arch == 'x86' and 32 or 64)
    vcvars = os.path.join(product_dir, 'bin', bat)

  path = os.path.splitext(output_filename)
  obj_filename = '{0}.obj'.format(path[0])
  p = subprocess.Popen(
      '"{0}" {1} & cl {2} /Fe{3} /Fo{4}'.format(
          vcvars,
          arch,
          filename,
          output_filename,
          obj_filename
      ),
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE
  )

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
