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

Running the Tests
-----------------
Install test dependencies and run `tox`::

    $ pip install skeleton[tests]
    $ tox

Building the Docs
-----------------
Install dependencies and build::

    $ pip install skeleton[docs]
    $ python setup.py docs

Requirements
------------
- six

License
-------
MIT - See `LICENSE`_ for more information.

Copyright
---------
Copyright (c) 2021 Chad Loether

.. _here: https://github.com/cloether/skeleton
.. _LICENSE: https://github.com/cloether/skeleton/blob/master/LICENSE.txt
