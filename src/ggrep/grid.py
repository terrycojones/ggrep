import re
from pathlib import Path
import polars as pl
from io import BytesIO, StringIO
from functools import partial

from ggrep.cell import Cell
from ggrep.row import Row
from ggrep.col import Col

debug = False


def int_to_excel_column_stack(column_num: int) -> str:
    # From https://blog.finxter.com/converting-integer-to-excel-column-name-in-python/
    column_chars = []
    while column_num > 0:
        column_num, remainder = divmod(column_num - 1, 26)
        column_chars.append(chr(65 + remainder))
    return "".join(reversed(column_chars))


class Grid:
    def __init__(
        self,
        source: Path | StringIO | BytesIO,
        filename: str | None = None,
        header: bool = True,
        skip: int = 0,
    ) -> None:
        """
        Read the input source.
        """
        self.header = header
        self.skip = skip
        if isinstance(source, Path):
            if filename:
                raise ValueError("If you pass a Path, you cannot also give a filename.")
            self.filename = str(source)
            suffix = source.suffix
        else:
            if not filename:
                raise ValueError("If you don't pass a Path, you must give a filename.")

            self.filename = filename
            fields = filename.split(".")
            suffix = f".{fields[-1]}" if len(fields) > 1 else ""

        match suffix := suffix.lower():
            case ".xlsx":
                if filename:
                    assert isinstance(source, BytesIO)
                    rows = pl.read_excel(source)
                else:
                    assert isinstance(source, Path)
                    with open(source, "rb") as fp:
                        rows = pl.read_excel(fp)

            case ".csv" | ".tsv":
                read_csv = partial(
                    pl.read_csv,
                    missing_utf8_is_empty_string=True,
                    separator="," if suffix == ".csv" else "\t",
                    has_header=header,
                    skip_rows=skip,
                )
                if filename:
                    assert isinstance(source, StringIO)
                    rows = read_csv(source)
                else:
                    assert isinstance(source, Path)
                    with open(source) as fp:
                        rows = read_csv(fp)
            case _:
                exit(f"Unknown file suffix: {suffix!r}.")

        self.col_names = rows.columns
        self.rows = [list(map(str, row)) for row in rows.iter_rows()]

    def match(self, pattern: str | re.Pattern) -> "Match":
        """
        Match a pattern
        """
        return Match(self, pattern)


class Match:
    """
    Manage a match.
    """

    def __init__(self, grid: Grid, pattern: str | re.Pattern):
        self.grid = grid
        self.matched = False
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        self.rows = []
        self.cols = []

        for row_index, row_data in enumerate(self.grid.rows):
            if debug:
                print(f"Examining {row_data}")
            row = Row(row_index)
            self.rows.append(row)
            for col_index, value in enumerate(row_data):
                try:
                    col = self.cols[col_index]
                except IndexError:
                    col = Col(col_index)
                    self.cols.append(col)
                cell = Cell(value, pattern)
                row.append(cell)
                col.append(cell)
                if cell.matched:
                    self.matched = True

    def __bool__(self):
        return self.matched

    def format(
        self,
        count: bool,
        filenames: bool,
        missing: str | None,
        color: str,
        row_numbers: bool,
        col_numbers: bool,
    ) -> str:
        result = []
        row_inc = 1 + self.grid.skip + self.grid.header

        if col_numbers:
            result.append(
                list(map(int_to_excel_column_stack, range(1, len(self.grid.col_names))))
            )
            if row_numbers:
                result[-1].insert(0, "")

        if self.grid.header:
            result.append(self.grid.col_names)
            if row_numbers:
                result[-1].insert(0, str(1 + self.grid.skip))

        for row in self.rows:
            if row.matched:
                line = [cell.format(missing, color) for cell in row]
                if row_numbers:
                    line.insert(0, str(row.index + row_inc))
                if line:
                    result.append(line)

        if count:
            return str(len(result))
        else:
            if filenames:
                for line in result:
                    line.insert(0, self.grid.filename)
            return "\n".join("\t".join(line) for line in result)

    def write(self, out: Path) -> None:
        print(f"Wrote to {str(out)!r}.")
