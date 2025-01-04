import re
import pytest

from xgrep.cell import Cell
from xgrep.row import Row


@pytest.mark.parametrize("index, invert", ((3, True), (4, False)))
def test_attrs(index, invert):
    row = Row(index, invert)
    assert row.index == index
    assert row.invert is invert


ll, xx, yy = map(re.compile, "ll xx yy".split())


def test_unmatched():
    row = Row(3, False)
    row.append(Cell("hello", xx))
    assert row.matched is False


def test_matched():
    row = Row(3, False)
    row.append(Cell("hello", ll))
    assert row.matched is True


def test_matched_when_inverted_and_there_was_a_match_1():
    row = Row(3, True)
    row.append(Cell("hello", ll))
    assert row.matched is False


def test_matched_when_inverted_and_there_was_a_match_2():
    row = Row(3, True)
    row.append(Cell("hello", ll))
    row.append(Cell("hello", xx))
    assert row.matched is False


def test_matched_when_inverted_and_there_was_no_match_1():
    row = Row(3, True)
    row.append(Cell("hello", xx))
    assert row.matched is True


def test_matched_when_inverted_and_there_was_no_match_2():
    row = Row(3, True)
    row.append(Cell("hello", xx))
    row.append(Cell("hello", yy))
    assert row.matched is True
