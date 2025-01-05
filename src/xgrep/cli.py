import sys
import click
from click_option_group import optgroup, MutuallyExclusiveOptionGroup
import re
from pathlib import Path
from rich.console import Console

from xgrep.excel import ExcelWriter
from xgrep.grid import grid_reader
from xgrep.match import Match


def check_args(
    format_: str,
    out: Path | None,
    sheet_id: tuple[int, ...] | int | None,
    sheet_name: tuple[str, ...] | str | None,
) -> None:
    """
    Make sure the command-line args are sane.
    """
    if format_ == "excel":
        if out is None:
            click.echo(
                "For Excel output you must use --out to give a filename.", err=True
            )
            sys.exit(-1)

        if sheet_id and sheet_name:
            click.echo(
                "You cannot use both --sheet-id and --sheet-name to select Excel "
                "sheets.",
                err=True,
            )
            sys.exit(-1)


def get_regex(pattern: str, ignore_case: bool) -> re.Pattern:
    """
    Compile the regular expression pattern.
    """
    try:
        return re.compile(pattern, re.I if ignore_case else 0)
    except re.PatternError:
        raise click.BadParameter(
            "must be a valid regular expression.",
            param_hint="--pattern",
        )


@click.command()
@click.argument(
    "pattern",
    nargs=1,
    required=True,
)
@click.argument(
    "filenames",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    nargs=-1,
)
@click.option(
    "-o",
    "--out",
    type=click.Path(dir_okay=False, path_type=Path),
    help=(
        "The output file. If not given, output is written to standard out. "
        "Note that if the --quiet (-q) option is also given, no output will be written "
        "to the output file."
    ),
)
@click.option(
    "--header/--no-header",
    default=True,
    help=(
        "Don't look for a header line in input files. In this case, text in what "
        "would otherwise be considered a header can also be matched by the grep pattern."
    ),
)
@click.option(
    "--skip",
    type=click.IntRange(0),
    default=0,
    help="Skip this many rows at the start of the input file(s).",
)
@click.option(
    "--format",
    "format_",
    type=click.Choice(["csv", "excel", "rich", "tsv"], case_sensitive=False),
    default="rich",
    help=(
        "The output format. The 'rich' format produces a rich Table (see "
        "https://rich.readthedocs.io/en/stable/tables.html)."
    ),
)
@click.option(
    "-c",
    "--count",
    is_flag=True,
    help="Only print the number of matching lines (like grep -c).",
)
@click.option("--width", type=int, help="The width to use for --format rich tables.")
@click.option(
    "-v",
    "--invert",
    is_flag=True,
    help="Only output rows that do not match (like grep -v).",
)
@click.option(
    "-q",
    "--quiet",
    "--silent",
    is_flag=True,
    help=(
        "Do not show any output, just exit with a status indicating whether a match "
        "was found (0) or not (1) (like grep -q)."
    ),
)
@click.option(
    "--ignore-missing-sheets",
    "--ims",
    is_flag=True,
    help=(
        "Do not exit if a requested sheet cannot be found in an input Excel file. "
        "A warning will be printed unless --quiet is used."
    ),
)
@click.option(
    "--only-matching-cols",
    "--omc",
    "--mco",
    is_flag=True,
    help="Only show columns that have a matching cell.",
)
@click.option(
    "-i",
    "--ignore-case",
    is_flag=True,
    help="Ignore case while matching (like grep -i).",
)
@click.option("--color", default="green", help="The highlight color.")
@click.option(
    "-u",
    "--unmatched",
    help=(
        "The string to show for cells whose values do not match. If not given, "
        "non-matching cells are shown with their value (in which case you will need "
        "to use the output color to see matches)."
    ),
)
@click.option(
    "-n",
    "--row-numbers",
    "--rn",
    "--line-number",
    is_flag=True,
    help="Show row numbers (like grep -n).",
)
@click.option(
    "--col-numbers",
    "--cn",
    is_flag=True,
    help=(
        "Show numeric column numbers. For alphabetic Excel column labels, use "
        "--excel-cols."
    ),
)
@click.option(
    "--excel-cols",
    "--ec",
    is_flag=True,
    help="Add Excel column labels to column names.",
)
@click.option(
    "-b",
    "--basename",
    is_flag=True,
    help=(
        "Only show basenames of input files in the output (and in Excel sheet names, "
        "in the case of --format excel)."
    ),
)
@click.option(
    "--save-empty-output",
    "--seo",
    is_flag=True,
    default=False,
    help=(
        "If there are no matches in a file (or Excel sheet), nothing will be written "
        "to the output file (so the output file will not exist after xgrep exits). Use "
        "this option to force the writing of empty output files (and creation of empty "
        "Excel worksheets in the case of --format excel)."
    ),
)
@optgroup.group(
    "Filenames",
    cls=MutuallyExclusiveOptionGroup,
    help="Whether to display names of matching files.",
)
@optgroup.option(
    "-H",
    "--filenames-always",
    "--fa",
    is_flag=True,
    help="Always print the name of matching files (like grep -H).",
)
@optgroup.option(
    "-h",
    "--no-filename",
    "--nf",
    is_flag=True,
    help="Never print the name of matching files (like grep -h).",
)
@optgroup.option(
    "--only-filename",
    "--of",
    is_flag=True,
    help="Only print the names of matching files, not their matched content.",
)
@click.option(
    "--sheet-name",
    "--sn",
    multiple=True,
    help=(
        "The name(s) of the sheet(s) to read. May be repeated. Cannot be used with "
        "--sheet-id."
    ),
)
@click.option(
    "--sheet-id",
    "--si",
    type=int,
    multiple=True,
    help=(
        "The numeric number(s) of the sheet(s) to read. The default is to search all "
        "workbook sheets in all Excel files (this is equivalent to --sheet-id 0). "
        "Individual sheet numbering starts from 1. May be repeated. Cannot be used with "
        "--sheet-name."
    ),
)
@click.option(
    "--sheet-separator",
    "--ss",
    default="+",
    help=(
        "The string used to separate filenames from sheet names when --format excel "
        "is used and multiple files are being searched. Note that Excel does not allow "
        "some characters (e.g., ':') in sheet names."
    ),
)
@click.version_option()
def cli(
    pattern: str,
    filenames: list[Path],
    out: Path | None,
    header: bool,
    skip: int,
    format_: str,
    count: bool,
    width: int,
    invert: bool,
    quiet: bool,
    ignore_missing_sheets: bool,
    only_matching_cols: bool,
    ignore_case: bool,
    color: str,
    unmatched: str | None,
    row_numbers: bool,
    col_numbers: bool,
    excel_cols: bool,
    basename: bool,
    save_empty_output: bool,
    filenames_always: bool,
    no_filename: bool,
    only_filename: bool,
    sheet_name: tuple[str, ...] | str | None,
    sheet_id: tuple[int, ...] | int | None,
    sheet_separator: str,
) -> None:
    """
    Command-line interface.
    """
    check_args(format_, out, sheet_id, sheet_name)

    # Set empty sheet-specifying tuples to be None to avoid an error from pl.read_excel.
    sheet_name = sheet_name or None
    sheet_id = sheet_id or None
    # Sheet id 0 cannot be passed in a tuple. Also, set sheet_id to 0 if we
    # have not been told otherwise. I.e., seaching all sheets is the default.
    if (sheet_name is None and sheet_id is None) or sheet_id == (0,):
        sheet_id = 0

    regex = get_regex(pattern, ignore_case)
    any_match = False

    out_fp = excel_writer = None
    if out is None:
        out_fp = sys.stdout
    else:
        if format_ == "excel":
            excel_writer = ExcelWriter(
                out,
                save_empty_output,
                sheet_separator,
                drop_filenames=len(filenames) == 1,
                quiet=quiet,
            )
        else:
            out_fp = open(out, "w")

    for path in filenames:
        try:
            grids = grid_reader(
                path,
                header,
                basename,
                skip,
                sheet_name,
                sheet_id,
                sheet_separator,
                ignore_missing_sheets,
                quiet,
                None,
            )
        except BaseException as e:
            click.echo(f"Could not read {str(path)!r}: {e}.", err=True)
            sys.exit(-1)

        for grid in grids:
            if match := Match(grid, regex, invert):
                any_match = True

                if quiet:
                    # No need to process any more files. The exit status will
                    # be 0 since a match exists in this file.
                    break

                print_filenames = not no_filename
                if len(filenames) == 1:
                    print_filenames = print_filenames and filenames_always

                result = match.format(
                    format_=format_,
                    only_filename=only_filename,
                    count=count,
                    width=width,
                    only_matching_cols=only_matching_cols,
                    filenames=print_filenames,
                    unmatched=unmatched,
                    color=color,
                    row_numbers=row_numbers,
                    col_numbers=col_numbers,
                    excel_cols=excel_cols,
                    out=out,
                    excel_writer=excel_writer,
                )

                if excel_writer is None:
                    # Unless the Excel writer has taken care of saving the
                    # match, there must be some kind of result, since 'match'
                    # is true, above.
                    assert result
                    assert out_fp
                    console = Console(file=out_fp, width=width, highlight=False)
                    console.print(result)

    if out is not None:
        if out_fp is None:
            assert excel_writer
            excel_writer.close()
        else:
            assert excel_writer is None
            out_fp.close()

    sys.exit(int(not any_match))
