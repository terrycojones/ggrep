import pytest
import re

from ggrep.cell import Cell


def test_unmatched():
    assert not Cell("hello", re.compile("xxx")).matched


def test_unmatched_str():
    cell = Cell("hello", re.compile("xxx"))
    assert str(cell) == "<Cell value='hello' matched=False>"


def test_matched():
    assert Cell("hello", re.compile("ll")).matched


def test_matched_str():
    cell = Cell("hello", re.compile("ll"))
    assert str(cell) == "<Cell value='hello' matched='ll'>"


def test_matched_format():
    cell = Cell("hello", re.compile("ll"))
    assert cell.format(None, None) == "hello"


def test_matched_color_format():
    cell = Cell("hello", re.compile("ll"))
    assert cell.format(None, "red") == "he[red]ll[/red]o"


def test_unmatched_format():
    cell = Cell("hello", re.compile("xxx"))
    assert cell.format(None, None) == "hello"


def test_unmatched_color_format():
    cell = Cell("hello", re.compile("xxx"))
    assert cell.format(None, "red") == "hello"


def test_unmatched_missing_format():
    cell = Cell("hello", re.compile("xxx"))
    assert cell.format(".", None) == "."


def test_unmatched_missing_color_format():
    cell = Cell("hello", re.compile("xxx"))
    assert cell.format(".", "red") == "."
