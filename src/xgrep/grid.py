import sys
from pathlib import Path
import polars as pl
from io import BytesIO, StringIO
from functools import partial
from dataclasses import dataclass


@dataclass
class Grid:
    col_names: list[str]
    rows: tuple[tuple[str, ...], ...]
    filename: str
    header: bool
    skip: int


def grid_reader(
    source: Path | StringIO | BytesIO,
    header: bool = True,
    basename: bool = False,
    skip: int = 0,
    sheet_name: tuple[str, ...] | str | None = None,
    sheet_id: tuple[int, ...] | int | None = None,
    sheet_separator: str = ":",
    ignore_missing_sheets: bool = False,
    quiet: bool = False,
    filename: str | None = None,
):
    """
    Read a grid (or several, in the case of Excel sheets) from a source and yield
    Grid instances.
    """
    if isinstance(source, Path):
        if filename is not None:
            raise ValueError("If you pass a Path, you cannot also give a filename.")
        path = source
    else:
        if filename is None:
            raise ValueError("If you don't pass a Path, you must give a filename.")
        assert isinstance(filename, str)
        path = Path(filename)

    output_filename = str(path.name if basename else path)

    match suffix := path.suffix.lower():
        case ".xlsx":
            options: dict[str, int | dict[str, int]] = dict(has_header=header)
            if header:
                options["read_options"] = dict(header_row=skip)

            read_excel = partial(
                pl.read_excel, sheet_name=sheet_name, sheet_id=sheet_id, **options
            )
            try:
                if filename:
                    assert isinstance(source, BytesIO)
                    worksheet = read_excel(source)
                else:
                    assert isinstance(source, Path)
                    with open(source, "rb") as fp:
                        worksheet = read_excel(fp)
            except ValueError as e:
                if "no matching sheet found" in str(e) and ignore_missing_sheets:
                    if not quiet:
                        assert sheet_name is not None
                        print(
                            f"Sheet{'' if len(sheet_name) == 1 else 's'} named "
                            f"{', '.join(sheet_name)} not found in {str(path)!r}.",
                            file=sys.stderr,
                        )
                else:
                    raise
            else:
                if isinstance(worksheet, pl.DataFrame):
                    worksheets = {None: worksheet}
                else:
                    assert isinstance(worksheet, dict)
                    worksheets = worksheet

                for this_sheet_name, worksheet in worksheets.items():
                    name = (
                        output_filename
                        if this_sheet_name is None
                        else f"{output_filename}{sheet_separator}{this_sheet_name}"
                    )
                    col_names = worksheet.columns
                    rows = tuple(tuple(row) for row in worksheet.iter_rows())
                    yield Grid(col_names, rows, name, header, skip)

        case ".csv" | ".tsv":
            read_csv = partial(
                pl.read_csv,
                missing_utf8_is_empty_string=True,
                separator="," if suffix == ".csv" else "\t",
                has_header=header,
                skip_rows=skip,
                infer_schema=False,
            )
            if filename:
                assert isinstance(source, StringIO)
                rows = read_csv(source)
            else:
                assert isinstance(source, Path)
                with open(source) as fp:
                    rows = read_csv(fp)

            col_names = rows.columns
            rows = tuple(tuple(row) for row in rows.iter_rows())

            yield Grid(col_names, rows, output_filename, header, skip)

        case _:
            raise ValueError(f"Unknown file suffix: {suffix!r}")
