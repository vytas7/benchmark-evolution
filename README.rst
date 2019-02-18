*******************
Benchmark Evolution
*******************

An uncomplicated tool to graph benchmark evolution across recent Git revisions
of the given project.


Requirements
============

The tool was developed and tested mostly under CPython 3.7.
CPython 3.4+ and PyPy3 should work too (untested).

In addition, `matplotlib <https://matplotlib.org>`_ is required. You can
install this (and other) dependency in your environment using::

  pip install -r requirements.txt


Usage
=====

Brief description of usage and supported options can be shown using::

  ./benchmark.py --help

The default command just counts the amount of code lines for last (up to) 100
commits in the provided repository::

  ./benchmark.py path/to/your/git/repository

By default, output will be saved as ``evolution.png`` in the current directory,
but the destination is customizable.


To Do / Exercise for the Reader
===============================

* Provided there is interest, I could package this and upload to
  `PyPi <https://pypi.org>`_
* More fluid Matplotlib layouts (as opposed to just hardcoding everything for
  now)
* Support for Git branches, tags, custom revision ranges etc
* (Insert another cool feature)
