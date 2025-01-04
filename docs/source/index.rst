.. ggrep documentation master file, created by
   sphinx-quickstart on Sat Jan  4 12:26:11 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ggrep documentation
===================

``ggrep`` (grid-grep) is a ``grep``-like script that searches for pattern in
files with grid-like data. It is most useful for finding matches in Excel
files, but can also read CSV and TSV files.

The main use case is to find patterns in Excel files without having to
manually open Excel and use its (plain text) search to find cells
one-by-one. Instead, you can use ``ggrep`` on the command line to quickly
identify which Excel files match a regular expression and extract the
matching rows (and, optionally, only the matching columns).

.. note::

   ``ggrep`` is under active development.

.. toctree::
   :maxdepth: 2
   :caption: Contents:
