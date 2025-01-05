import sys
import polars as pl
import xlsxwriter

from pathlib import Path


def int_to_excel_column(column_num: int) -> str:
    assert column_num > 0
    # From https://blog.finxter.com/converting-integer-to-excel-column-name-in-python/
    column_chars = []
    while column_num > 0:
        column_num, remainder = divmod(column_num - 1, 26)
        column_chars.append(chr(65 + remainder))
    return "".join(reversed(column_chars))


class ExcelWriter:
    """
    Manage an Excel workbook.
    """

    def __init__(
        self,
        path: Path,
        save_empty_output: bool,
        sheet_separator: str,
        drop_filenames: bool,
        quiet: bool,
    ) -> None:
        self.path = path
        self.save_empty_output = save_empty_output
        self.sheet_separator = sheet_separator
        self.drop_filenames = drop_filenames
        self.empty = True
        self.workbook = xlsxwriter.Workbook(str(path), dict(strings_to_numbers=True))
        self.quiet = quiet
        self.sheet_names = {}

    def new_sheet_name(self, name: str) -> str:
        """
        Find a sheet name that does not conflict with those already in use.
        """
        i = 0
        candidate = name
        shortened = False

        while candidate in self.sheet_names:
            i += 1
            candidate = f"{name} {i}"
            if len(candidate) > 31:
                candidate = name[-31:]
                shortened = True

        if shortened and not self.quiet:
            print(
                f"The name {name!r} is too long to use as an Excel sheet. "
                f"Shortened to {candidate!r}.",
                file=sys.stderr,
            )

        return candidate

    def write(self, df: pl.DataFrame, name: str | None = None):
        if len(df) or self.save_empty_output:
            if name is not None:
                try:
                    filename, sheet_name = name.rsplit(self.sheet_separator, maxsplit=1)
                except ValueError:
                    filename, sheet_name = name, "Sheet"

                if self.drop_filenames:
                    name = sheet_name

                name = self.new_sheet_name(name)
                self.sheet_names[name] = filename

            df.write_excel(self.workbook, worksheet=name)
            self.empty = False

    def close(self):
        self.workbook.close()

        if self.empty and not self.save_empty_output:
            # If we have not written anything, the file should be empty.
            try:
                pl.read_excel(self.path)
            except pl.exceptions.NoDataError:
                # As expected.
                self.path.unlink()
            else:
                raise Exception(
                    f"Expected output Excel file {str(self.path)!r} to be empty, but "
                    "it is not. This is weird - please investigate!"
                )
