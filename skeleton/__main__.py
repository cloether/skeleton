#!/usr/bin/env python
# -*- coding: utf8 -*-
"""__main__.py

Command Line Interface (CLI) Entry Point
"""

if __name__ == "__main__":
  import os
  import signal
  import sys

  from .cli import _shutdown_handler, main

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
  except SystemExit:
    raise
  except Exception:
    sys.stderr.write("""\
ERROR: {{
  type:     {0}
  message:  {1}
  file:     File "{2}", line {3}, in {4}
}}
""".format(
        sys.exc_info()[0].__name__,
        sys.exc_info()[1],
        sys.exc_info()[-1].tb_frame.f_code.co_filename,
        sys.exc_info()[-1].tb_lineno,
        sys.exc_info()[-1].tb_frame.f_code.co_name)
    )
    sys.stderr.flush()
    sys.exit(1)
  except:  # noqa
    import traceback

    traceback.print_exc()
    sys.exit(-1)
  else:
    sys.exit(status)
