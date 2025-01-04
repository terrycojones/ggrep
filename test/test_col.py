import re

from xgrep.cell import Cell
from xgrep.col import Col


def test_default():
    col = Col(3, False)
    assert col.numeric is True


def test_numeric():
    col = Col(3, False)
    col.append(Cell(6, re.compile("xxx")))
    assert col.numeric is True


def test_nonnumeric():
    col = Col(3, False)
    col.append(Cell("hello", re.compile("xxx")))
    assert col.numeric is False
