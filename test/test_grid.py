import pytest
from unittest.mock import patch
from io import StringIO
from pathlib import Path

from ggrep.grid import Grid


class CSV:
    def __init__(self, rows, sep):
        self.rows = rows
        self.sep = sep
        self.format_ = "csv" if sep == "," else "tsv"

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.rows[item]
        elif isinstance(item, tuple):
            row, col = item
            return self.rows[row][col]
        raise ValueError(f"Unknown item {item!r}")

    def __call__(self):
        return "\n".join(self.sep.join(row) for row in self.rows) + "\n"


_BASIC_DATA = (
    ("name", "age"),
    ("cyril", "32"),
    ("maria", "81"),
)

BASIC_CSV = CSV(_BASIC_DATA, sep=",")
BASIC_TSV = CSV(_BASIC_DATA, sep="\t")


def basic_grid(data=BASIC_CSV, **kwargs):
    return Grid(StringIO(data()), filename=f"test-data.{data.format_}", **kwargs)


class TestGrid:
    """
    Simple initial tests for the Grid class.
    """

    def test_nonexistent_path(self) -> None:
        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = False
            with pytest.raises(FileNotFoundError):
                Grid(Path("xxx.xlsx"))

    @pytest.mark.parametrize("data", (BASIC_CSV, BASIC_TSV))
    def test_rows(self, data) -> None:
        "Test that the grid can read CSV and TSV data"
        g = basic_grid(data)
        assert g.rows == (data[1], data[2])
