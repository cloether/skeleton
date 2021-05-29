..
  https://docutils.sourceforge.io/docs/user/rst/quickref.html
  https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet

Skeleton
========

``skeleton`` is a template used for creating Python modules.

The official repo is `here`_.

  .. note:: This library is under active development.

Installation
------------
To install the library into the current virtual environment::

    $ pip install skeleton

or::

    $ python -m pip install skeleton

Running the Tests
-----------------
Install test dependencies and run `tox`::

    $ pip install skeleton[tests]
    $ tox

Building the Docs
-----------------
Install documentation dependencies and build::

    $ pip install skeleton[docs]
    $ python setup.py docs

Requirements
------------
- six

Support
-------
- Submit an `Issue`_.
- Submit a `Bug Report`_.
- Submit a `Feature Request`_.
- Ask a `Question`_.
- Request `Assistance`_.

License
-------
MIT - See `LICENSE`_ for more information.

Copyright
---------
Copyright (c) 2021 Chad Loether

.. _here: https://github.com/cloether/skeleton
.. _Issue: https://github.com/cloether/skeleton/issues/new?template=blank-issue.md
.. _Bug Report: https://github.com/cloether/skeleton/issues/new?template=bug-report.md&labels=bug
.. _Feature Request: https://github.com/cloether/skeleton/issues/new?template=feature-request.md&labels=enhancement
.. _Question: https://github.com/cloether/skeleton/issues/new?template=question.md&labels=question
.. _Assistance: https://github.com/cloether/skeleton/issues/new?template=need-help.md&labels=help+wanted
.. _LICENSE: https://github.com/cloether/skeleton/blob/master/LICENSE.txt

Reference
=========
``skeleton`` module reference.

..  toctree::
    :maxdepth: 3

    modules

Indices and tables
------------------
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
