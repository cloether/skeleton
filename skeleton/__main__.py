# coding=utf8
"""__main__.py

Command Line Interface (CLI) Entry Point
"""
from __future__ import absolute_import, print_function, unicode_literals

import os

# Force absolute path on Python 2.
# https://github.com/microsoft/debugpy/blob/master/src/debugpy/__main__.py
__file__ = os.path.abspath(__file__)  # noqa

if __name__ == "__main__":
  import signal
  import sys

  from .cli import main

  def _shutdown_handler(signum, _):
    """Handle Shutdown.

    Args:
      signum (int): Signal Number,
      _ (types.FrameType): Interrupted Stack Frame.

    Raises:
      (SystemExit): Calls sys.exit(), which raises s SystemExit exception.
    """
    sys.stderr.write("\b\b\b\bshutdown handler called, signal=%d" % signum)
    sys.exit(signum)

  signal.signal(signal.SIGTERM, _shutdown_handler)
  signal.signal(signal.SIGINT, _shutdown_handler)
  if os.name == 'nt':
    signal.signal(signal.SIGBREAK, _shutdown_handler)

  # noinspection PyBroadException
  try:
    status = main()
  except NotImplementedError as exc:
    sys.stderr.write("%s\n" % exc)
    sys.exit(0)
  except KeyboardInterrupt as e:
    sys.exit(e)
  except Exception as e:
    sys.stderr.write("{0!r}".format(e))
    sys.stderr.flush()
    sys.exit(1)
  except:  # noqa
    import traceback

    traceback.print_last()
    sys.exit(-1)
  else:
    sys.exit(status)
