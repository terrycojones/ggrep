import re
import polars as pl
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from functools import partial
from io import StringIO
from pathlib import Path

from ggrep.cell import Cell
from ggrep.excel import int_to_excel_column
from ggrep.row import Row
from ggrep.col import Col
from ggrep.grid import Grid


class Match:
    """
    Match a pattern and provide ways to format the result.
    """

    def __init__(self, grid: "Grid", pattern: str | re.Pattern, invert: bool = False):
        self._grid = grid
        self._matched = False
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        self.rows = []
        self.cols = []

        for row_index, row_data in enumerate(self._grid.rows):
            row = Row(row_index, invert)
            self.rows.append(row)
            for col_index, value in enumerate(row_data):
                try:
                    col = self.cols[col_index]
                except IndexError:
                    col = Col(col_index, invert)
                    self.cols.append(col)
                cell = Cell(value, pattern)
                row.append(cell)
                col.append(cell)
                if cell.matched:
                    self._matched = True

    def __str__(self):
        result = []
        for i, row in enumerate(self.rows):
            result.append(
                f"Row {i} matched {row.matched()}: "
                + " ".join(["1" if cell.matched else "0" for cell in row])
            )
        return "\n".join(result)

    def __bool__(self):
        return self._matched

    def polars_df(
        self,
        row_numbers: bool,
        col_numbers: bool,
        filenames: bool,
        color: str | None,
        unmatched: str | None,
        only_matching_cols: bool,
        excel_cols: bool,
    ) -> pl.DataFrame:
        data = defaultdict(list)
        row_inc = 1 + self._grid.skip + self._grid.header

        for row in self.rows:
            if row.matched:
                if row_numbers:
                    data["Row"].append(row.index + row_inc)
                for col_index, cell in enumerate(row):
                    if only_matching_cols and not self.cols[col_index].matched:
                        continue

                    col_name = self._grid.col_names[col_index]
                    excel_col = int_to_excel_column(col_index + 1)
                    str_col = f"{col_index + 1}"

                    if self._grid.header:
                        if excel_cols:
                            key = f"{col_name} ({excel_col})"
                        elif col_numbers:
                            key = f"{col_name} ({str_col})"
                        else:
                            key = col_name
                    else:
                        key = "Column " + (excel_col if excel_cols else str_col)

                    data[key].append(cell.format(unmatched, color))

                if filenames:
                    data["File"].append(self._grid.filename)

        return pl.DataFrame(data)

    def rich_table(
        self, df: pl.DataFrame, width: int | None, out: Path | None
    ) -> Table | None:
        table = Table(title=self._grid.filename)

        for col_index, col_name in enumerate(df.columns):
            if col_name == "Row":
                assert col_index == 0
                justify = "right"
            else:
                justify = "right" if self.cols[col_index - 1].numeric else "left"

            table.add_column(col_name, justify=justify)

        for row in df.iter_rows():
            table.add_row(*map(str, row))

        if out is None:
            return table
        else:
            with open(out, "w") as fp:
                console = Console(file=fp, width=width)
                console.print(table)

    def format(
        self,
        format_: str = "tsv",
        only_filename: bool = False,
        count: bool = False,
        width: int | None = None,
        only_matching_cols: bool = False,
        filenames: bool = False,
        unmatched: str | None = None,
        color: str | None = None,
        row_numbers: bool = False,
        col_numbers: bool = False,
        excel_cols: bool = False,
        out: Path | None = None,
    ) -> str | Table | None:
        df = self.polars_df(
            row_numbers,
            col_numbers,
            filenames,
            color=None if out else color,
            unmatched=unmatched,
            only_matching_cols=only_matching_cols,
            excel_cols=excel_cols,
        )

        if count or only_filename:
            if count:
                result = f"{self._grid.filename + ':' if filenames else ''}{len(df)}"
            else:
                result = self._grid.filename

            if out:
                with open(out, "w") as fp:
                    print(result, file=fp)
                return

            return result

        if format_ in ("csv", "tsv"):
            write_csv = partial(
                df.write_csv,
                separator="," if format_ == "csv" else "\t",
                include_header=self._grid.header,
            )
            if out:
                with open(out, "w") as fp:
                    write_csv(fp)
                return

            output = StringIO()
            write_csv(output)
            # Drop the trailing newline so our caller can consistently print
            # our result without needing to selectively use print(result, end="").
            return output.getvalue().rstrip("\n")

        if format_ == "rich":
            return self.rich_table(df, width, out)

        if format_ == "excel":
            df.write_excel(out)
            return

        raise ValueError(f"Unknown output format {format_!r}.")
