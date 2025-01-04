from pathlib import Path
import polars as pl
from io import BytesIO, StringIO
from functools import partial


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
            if filename is not None:
                raise ValueError("If you pass a Path, you cannot also give a filename.")
            self.filename = str(source)
            suffix = source.suffix
        else:
            if filename is None:
                raise ValueError("If you don't pass a Path, you must give a filename.")

            self.filename = filename
            fields = filename.split(".")
            suffix = f".{fields[-1]}" if len(fields) > 1 else ""

        match suffix := suffix.lower():
            case ".xlsx":
                options: dict[str, int | dict[str, int]] = dict(has_header=header)
                if header:
                    options["read_options"] = dict(header_row=skip)
                read_excel = partial(pl.read_excel, **options)
                if filename:
                    assert isinstance(source, BytesIO)
                    rows = read_excel(source)
                else:
                    assert isinstance(source, Path)
                    with open(source, "rb") as fp:
                        rows = read_excel(fp)

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
            case _:
                raise ValueError(f"Unknown file suffix: {suffix!r}")

        self.col_names = rows.columns
        self.rows = tuple(tuple(row) for row in rows.iter_rows())
