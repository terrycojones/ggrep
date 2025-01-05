import pytest
from io import StringIO
from itertools import product

from xgrep.grid import grid_reader
from xgrep.match import Match


class CSV:
    def __init__(self, rows, sep):
        self.rows = rows
        self.sep = sep
        self.format_ = "csv" if sep == "," else "tsv"

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.sep.join(self.rows[item])
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


def basic_grid(data, **kwargs):
    return list(
        grid_reader(
            StringIO(data()), filename=f"test-data.{data.format_}", **kwargs)
    )[0]


class TestMatch:
    """
    Simple initial tests for the Match class.
    """

    @pytest.mark.parametrize("data", (BASIC_CSV, BASIC_TSV))
    def test_no_match(self, data) -> None:
        "If there are no matches, we must get the empty string back."
        g = basic_grid(data, header=False)
        m = Match(g, "xxx")
        assert m.format() == ""

    @pytest.mark.parametrize("data", (BASIC_CSV, BASIC_TSV))
    def test_header(self, data) -> None:
        "With a header in the CSV, we must not match its first line."
        g = basic_grid(data, header=True)
        m = Match(g, "name")
        assert m.format() == ""

    @pytest.mark.parametrize("data", (BASIC_CSV, BASIC_TSV))
    def test_no_header(self, data) -> None:
        "With no header in the basic CSV, we must be able to match its first line."
        g = basic_grid(data, header=False)
        m = Match(g, "name")
        assert m.format(format_=data.format_) == data[0]

    @pytest.mark.parametrize("data", (BASIC_CSV, BASIC_TSV))
    def test_match_cyril(self, data) -> None:
        "We must be able to match the cell containing 'cyril'."
        g = basic_grid(data, header=False)
        m = Match(g, "cyril")
        assert m.format(format_=data.format_) == data[1]

    @pytest.mark.parametrize("data", (BASIC_CSV, BASIC_TSV))
    def test_match_cyril_count(self, data) -> None:
        "We must be able to match the cell containing 'cyril'. and get a count of 1."
        g = basic_grid(data, header=False)
        m = Match(g, "cyril")
        assert m.format(format_=data.format_, count=True) == "1"

    @pytest.mark.parametrize("data", (BASIC_CSV, BASIC_TSV))
    def test_match_both_count(self, data) -> None:
        "We must be able to match both rows and get a count of 2."
        g = basic_grid(data, header=False)
        m = Match(g, "cyril|maria")
        assert m.format(format_=data.format_, count=True) == "2"

    @pytest.mark.parametrize("data", (BASIC_CSV, BASIC_TSV))
    def test_cyril_only_matching_cols(self, data) -> None:
        "We must be able to match a cell and ask to not receive non-matching cols."
        g = basic_grid(data, header=False)
        m = Match(g, "cyril")
        assert m.format(format_=data.format_, only_matching_cols=True) == data[1, 0]

    @pytest.mark.parametrize(
        "data, color", product((BASIC_CSV, BASIC_TSV), ("red", "blue"))
    )
    def test_cyril_colored(self, data, color) -> None:
        """
        We must be able to match a cell with a color.
        """
        g = basic_grid(data, header=False)
        m = Match(g, "cyril")
        assert (
            m.format(format_=data.format_, color=color)
            == f"[{color}]{data[1, 0]}[/{color}]{data.sep}{data[1, 1]}"
        )

    @pytest.mark.parametrize(
        "data, color", product((BASIC_CSV, BASIC_TSV), ("red", "blue"))
    )
    def test_cyril_colored_only_matching_cols(self, data, color) -> None:
        """
        We must be able to match a cell with a color and ask to not receive
        non-matching cols.
        """
        g = basic_grid(data, header=False)
        m = Match(g, "cyril")
        assert (
            m.format(format_=data.format_, only_matching_cols=True, color=color)
            == f"[{color}]{data[1, 0]}[/{color}]"
        )

    @pytest.mark.parametrize("data", (BASIC_CSV, BASIC_TSV))
    def test_match_i(self, data) -> None:
        "We must be able to match the cells containing 'i'."
        g = basic_grid(data, header=False)
        m = Match(g, "i")
        assert m.format(format_=data.format_) == data[1] + "\n" + data[2]

    @pytest.mark.parametrize("data", (BASIC_CSV, BASIC_TSV))
    def test_match_regex_both_names(self, data) -> None:
        "We must be able to match both rows with a regex on the names."
        g = basic_grid(data, header=False)
        m = Match(g, "cyril|maria")
        assert m.format(format_=data.format_) == data[1] + "\n" + data[2]

    @pytest.mark.parametrize("data", (BASIC_CSV, BASIC_TSV))
    def test_match_regex_both_ages(self, data) -> None:
        "We must be able to match both rows with a regex on the ages."
        g = basic_grid(data, header=False)
        m = Match(g, "3|8")
        assert m.format(format_=data.format_) == data[1] + "\n" + data[2]

    @pytest.mark.parametrize("data", (BASIC_CSV, BASIC_TSV))
    def test_match_regex_both_names_only_matching_cols(self, data) -> None:
        "We must be able to match both rows with a regex on the names."
        g = basic_grid(data, header=False)
        m = Match(g, "cyril|maria")
        assert (
            m.format(format_=data.format_, only_matching_cols=True)
            == data[1, 0] + "\n" + data[2, 0]
        )

    @pytest.mark.parametrize("data", (BASIC_CSV, BASIC_TSV))
    def test_match_regex_both_ages_only_matching_cols(self, data) -> None:
        "We must be able to match both rows with a regex on the ages."
        g = basic_grid(data, header=False)
        m = Match(g, "3|8")
        assert (
            m.format(format_=data.format_, only_matching_cols=True)
            == data[1, 1] + "\n" + data[2, 1]
        )


class TestMatchWithFileHeaderClash:
    """
    Simple initial tests for the Match class when the data "File" header clashes
    with a column name that xgrep would add.
    """

    def test_file_column_no_conflict(self) -> None:
        """
        The code must correctly deal with data that has a "File" column.
        when we are not asking for filenames.
        """
        data = (
            ("File", "name", "age"),
            ("a.txt", "cyril", "32"),
            ("b.txt", "maria", "81"),
        )

        csv = CSV(data, sep=",")
        g = basic_grid(csv)
        m = Match(g, "maria")
        assert m.format(format_="csv") == "File,name,age\nb.txt,maria,81"

    def test_file_column_one_conflict(self) -> None:
        """
        The code must correctly deal with data that has a "File" column.
        when we ask for the filename to be included in the result.
        """
        data = (
            ("File", "name", "age"),
            ("a.txt", "cyril", "32"),
            ("b.txt", "maria", "81"),
        )

        csv = CSV(data, sep=",")
        g = basic_grid(csv)
        m = Match(g, "maria")
        assert m.format(format_="csv", filenames=True) == (
            "File (2),File,name,age\ntest-data.csv,b.txt,maria,81"
        )

    def test_file_column_two_conflicts(self) -> None:
        """
        The code must correctly deal with data that has "File" and "File (2)"
        columns. when we ask for the filename to be included in the result.
        """
        data = (
            ("File",  "File (2)",  "name", "age"),
            ("a.txt", "c.txt", "cyril", "32"),
            ("b.txt", "d.txt", "maria", "81"),
        )

        csv = CSV(data, sep=",")
        g = basic_grid(csv)
        m = Match(g, "maria")
        assert m.format(format_="csv", filenames=True) == (
            "File (3),File,File (2),name,age\ntest-data.csv,b.txt,d.txt,maria,81"
        )


class TestMatchWithRowHeaderClash:
    """
    Simple initial tests for the Match class when the data "Row" header clashes
    with a column name that xgrep would add.
    """

    def test_row_column_no_conflict(self) -> None:
        """
        The code must correctly deal with data that has a "Row" column.
        when we are not asking for filenames.
        """
        data = (
            ("Row", "name", "age"),
            ("1", "cyril", "32"),
            ("2", "maria", "81"),
        )

        csv = CSV(data, sep=",")
        g = basic_grid(csv)
        m = Match(g, "maria")
        assert m.format(format_="csv") == "Row,name,age\n2,maria,81"

    def test_row_column_one_conflict(self) -> None:
        """
        The code must correctly deal with data that has a "Row" column.
        when we ask for the filename to be included in the result.
        """
        data = (
            ("Row", "name", "age"),
            ("1", "cyril", "32"),
            ("2", "maria", "81"),
        )

        csv = CSV(data, sep=",")
        g = basic_grid(csv)
        m = Match(g, "maria")
        assert m.format(format_="csv", row_numbers=True) == (
            "Row (2),Row,name,age\n3,2,maria,81"
        )

    def test_row_column_two_conflicts(self) -> None:
        """
        The code must correctly deal with data that has "Row" and "Row (2)"
        columns. when we ask for the filename to be included in the result.
        """
        data = (
            ("Row", "Row (2)", "name", "age"),
            ("1", "3", "cyril", "32"),
            ("2", "4", "maria", "81"),
        )

        csv = CSV(data, sep=",")
        g = basic_grid(csv)
        m = Match(g, "maria")
        assert m.format(format_="csv", row_numbers=True) == (
            "Row (3),Row,Row (2),name,age\n3,2,4,maria,81"
        )
