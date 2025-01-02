import pytest
from pathlib import Path
from unittest.mock import patch
from io import StringIO

from ggrep.grid import Grid

BASIC_CSV = """\
name,age
cyril,32
maria,81
"""


def basic_grid(**kwargs):
    return Grid(StringIO(BASIC_CSV), filename="test-data.csv", **kwargs)


class Test_Grid:
    """
    Test the Grid class
    """

    def test_nonexistent_path(self) -> None:
        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = False
            with pytest.raises(FileNotFoundError):
                Grid(Path("xxx.xlsx"))

    def test_header(self) -> None:
        "With a header in the CSV, we must not match its first line."
        match = basic_grid(header=True).match("name")
        assert "" == match.format(count=False, filenames=False, missing="", color="", row_numbers=False, col_numbers=False)

    def test_no_header(self) -> None:
        "With no header in the basic CSV, we must be able to match its first line."
        match = basic_grid(header=False).match("name")
        assert "name" == match.format(count=False, filenames=False, missing="", color="", row_numbers=False, col_numbers=False)

    def test_cyril(self) -> None:
        "We must be able to match a cell"
        match = basic_grid().match("cyril")
        assert "cyril" == match.format(count=False, filenames=False, missing="", color="", row_numbers=False, col_numbers=False)
