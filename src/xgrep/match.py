import re
import polars as pl
import polars.selectors as cs
from collections import defaultdict
from rich.table import Table
from io import StringIO
from pathlib import Path

from xgrep.cell import Cell
from xgrep.excel import int_to_excel_column, ExcelWriter
from xgrep.row import Row
from xgrep.col import Col
from xgrep.grid import Grid


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
        grid_col_names = set(self._grid.col_names)

        def new_col_name(name: str) -> str:
            """
            We are going to add a column name. Find a name that does not
            conflict with the column names in the original data.
            """
            i = 1
            candidate = name
            while candidate in grid_col_names:
                i += 1
                candidate = f"{name} ({i})"
            return candidate

        if filenames:
            # This looks like a no op, but it has the side-effect of making
            # sure the new "File" column is the first thing in the 'data'
            # dict. As a result, it will appear first in the list of columns.
            col_name = new_col_name("File")
            data[col_name] = []

        for row in self.rows:
            if row.matched:
                if row_numbers:
                    col_name = new_col_name("Row")
                    # Note that this new column is numeric. All other columns
                    # are strings (because that is how we orignially read (or
                    # converted) the data out of CSV, TSV, or Excel). We make
                    # our additional "Row" column numeric in order to know
                    # that we can right justify it in rich_table. If not, we
                    # would either need to leave it left justified or think
                    # of a non-horrible way for this function to return the
                    # name of the newly-added "Row" column so the name could
                    # be passed to rich_table.
                    data[col_name].append(row.index + row_inc)
                for col_index, cell in enumerate(row):
                    if only_matching_cols and not self.cols[col_index].matched:
                        continue

                    grid_col_name = self._grid.col_names[col_index]
                    excel_col = int_to_excel_column(col_index + 1)
                    str_col = f"{col_index + 1}"

                    if self._grid.header:
                        if excel_cols:
                            col_name = f"{grid_col_name} ({excel_col})"
                        elif col_numbers:
                            col_name = f"{grid_col_name} ({str_col})"
                        else:
                            col_name = grid_col_name
                    else:
                        col_name = "Column " + (excel_col if excel_cols else str_col)

                    if col_name != grid_col_name:
                        col_name = new_col_name(col_name)

                    data[col_name].append(cell.format(unmatched, color))

                if filenames:
                    col_name = new_col_name("File")
                    data[col_name].append(self._grid.filename)

        return pl.DataFrame(data)

    def rich_table(self, df: pl.DataFrame) -> Table:
        table = Table(title=self._grid.filename)

        numeric_columns = set(df.select(cs.numeric()).columns)

        for col_index, col_name in enumerate(df.columns):
            justify = (
                "right"
                if col_name in numeric_columns or self.cols[col_index - 1].numeric
                else "left"
            )

            table.add_column(col_name, justify=justify)

        for row in df.iter_rows():
            table.add_row(*map(str, row))

        return table

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
        excel_writer: ExcelWriter | None = None,
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

        if count:
            return f"{self._grid.filename + ':' if filenames else ''}{len(df)}"

        if only_filename:
            return self._grid.filename

        if format_ in ("csv", "tsv"):
            output = StringIO()
            df.write_csv(
                output,
                separator="," if format_ == "csv" else "\t",
                include_header=self._grid.header,
            )
            # Drop the trailing newline so our caller can consistently print
            # our result without needing to selectively use print(result, end="").
            return output.getvalue().rstrip("\n")

        if format_ == "rich":
            return self.rich_table(df)

        if format_ == "excel":
            assert excel_writer is not None
            excel_writer.write(df, self._grid.filename)
            return

        raise ValueError(f"Unknown output format {format_!r}.")
