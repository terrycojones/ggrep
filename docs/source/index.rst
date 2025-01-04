.. xgrep documentation master file, created by
   sphinx-quickstart on Sat Jan  4 12:26:11 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

xgrep documentation
===================

``xgrep`` is a ``grep``-like script to search for a pattern in Excel
files. It can also read CSV and TSV files. By default, output is written as a
``rich`` table, but can also be saved as CSV, TSV, or Excel.

The main use case is to find patterns in Excel files without having to
manually open Excel and use its (plain text) search to find cells
one-by-one. Instead, you can use ``xgrep`` on the command line to quickly
identify which Excel files match a regular expression and extract the
matching rows (and, optionally, only the matching columns).

.. note::

   ``xgrep`` is under active development.

.. toctree::
   :maxdepth: 2
   :caption: Contents:
