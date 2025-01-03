import sys
import click
from click_option_group import optgroup, MutuallyExclusiveOptionGroup
import re
from pathlib import Path
from rich import print as rprint

from ggrep.grid import Grid
from ggrep.match import Match


def check_args(
    filenames: list[Path],
    pattern: str,
    ignore_case: bool,
    format_: str,
    out: Path | None,
) -> re.Pattern:
    try:
        regex = re.compile(pattern, re.I if ignore_case else 0)
    except re.PatternError:
        raise click.BadParameter(
            "must be a valid regular expression.",
            param_hint="--pattern",
        )

    if len(filenames) > 1 and out:
        print(
            "If you specify multiple files to match, you cannot also use --out.",
            file=sys.stderr,
        )
        sys.exit(-1)

    if format_ == "excel" and out is None:
        print(
            "For Excel output you must use --out to give a filename.",
            file=sys.stderr,
        )
        sys.exit(-1)

    return regex


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
@click.option("--out", type=click.Path(dir_okay=False, path_type=Path))
@click.option(
    "--header/--no-header",
    default=True,
    help=(
        "Don't look for a header line. In this case, text in what would otherwise "
        "be considered a header can also be matched by the grep pattern."
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
    default="tsv",
    help="The output format.",
)
@click.option(
    "-c", "--count", is_flag=True, help="Only print the number of matching lines."
)
@click.option("--width", type=int, help="The width to use for --format rich tables.")
@click.option("-v", "--invert", is_flag=True, help="Print non-matching lines.")
@click.option(
    "--only-matching-cols",
    is_flag=True,
    help="Only show columns that have a matching cell.",
)
@click.option("-i", "--ignore-case", is_flag=True, help="Ignore case while matching.")
@click.option("--color", default="green", help="The highlight color.")
@click.option(
    "--missing",
    help=(
        "The string to show for cells whose values do not match. If not given, "
        "non-matching cells are shown with their value (in which case you will need "
        "to use the output color to see matches)."
    ),
)
@click.option("--row-numbers", is_flag=True, help="Show row numbers.")
@click.option("--col-numbers", is_flag=True, help="Show column numbers.")
@click.option(
    "--excel-cols", is_flag=True, help="Add Excel column labels to column names."
)
@optgroup.group(
    "Filenames",
    cls=MutuallyExclusiveOptionGroup,
    help="Whether to display names of matching files.",
)
@optgroup.option(
    "-H",
    "--filenames_always",
    is_flag=True,
    help="Always print the name of matching files (like grep -H)",
)
@optgroup.option(
    "-h",
    "--no-filename",
    is_flag=True,
    help="Never print the name of matching files (like grep -h)",
)
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
    only_matching_cols: bool,
    ignore_case: bool,
    color: str,
    missing: str | None,
    row_numbers: bool,
    col_numbers: bool,
    excel_cols: bool,
    filenames_always: bool,
    no_filename: bool,
) -> None:
    regex = check_args(filenames, pattern, ignore_case, format_, out)
    any_match = False

    for path in filenames:
        try:
            grid = Grid(path, header=header, skip=skip)
        except BaseException as e:
            rprint(f"Could not read {str(path)!r}: {e}.", file=sys.stderr)
            sys.exit(-1)

        if match := Match(grid, regex, invert):
            any_match = True
            if len(filenames) == 1:
                print_filenames = not no_filename and filenames_always
            else:
                print_filenames = not no_filename

            result = match.format(
                format_=format_,
                count=count,
                width=width,
                only_matching_cols=only_matching_cols,
                filenames=print_filenames,
                missing=missing,
                color=color,
                row_numbers=row_numbers,
                col_numbers=col_numbers,
                excel_cols=excel_cols,
                out=out,
            )

            if not out:
                assert isinstance(result, str)
                p = print if format_ == "rich" else rprint
                p(result, end="")
        else:
            if out:
                rprint(f"No matches, {str(out)!r} not written to.", file=sys.stderr)

    sys.exit(int(not any_match))
