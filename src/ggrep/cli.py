import sys
import click
from click_option_group import optgroup, MutuallyExclusiveOptionGroup
import re
from pathlib import Path
from rich import print

from ggrep.grid import Grid


@click.command()
@click.argument("pattern", nargs=1, required=True)
@click.argument(
    "filenames",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    nargs=-1,
)
@click.option("--out", type=click.Path(dir_okay=False, path_type=Path))
@click.option("--header/--no-header", default=True)
@click.option("--skip", type=click.IntRange(0), default=0)
@click.option("-c", "--count", is_flag=True)
@click.option("-i", "--ignore-case", is_flag=True)
@click.option("--color", default="green", help="The highlight color.")
@click.option(
    "--missing",
    help=(
        "The string to show for cells whose values do not match. If not given, "
        "non-matching cells are shown with their value (in which case you will need "
        "to use the output color to see matches)."
    )
)
@click.option("--row-numbers", is_flag=True, help="Show row numbers.")
@click.option("--col-numbers", is_flag=True, help="Show column numbers.")
@optgroup.group(
    "Filenames",
    cls=MutuallyExclusiveOptionGroup,
    help="Whether to display names of matching files.",
)
@optgroup.option("-H", "--filenames_always", is_flag=True)
@optgroup.option("-h", "--no-filename", is_flag=True)
def cli(
    pattern: re.Pattern,
    filenames: list[Path],
    out: Path | None,
    header: bool,
    skip: int,
    count: bool,
    ignore_case: bool,
    color: str,
    missing: str | None,
    row_numbers: bool,
    col_numbers: bool,
    filenames_always: bool,
    no_filename: bool,
) -> None:
    if len(filenames) > 1 and out:
        exit("If you specify multiple files to match, you cannot also use --out")

    try:
        regex = re.compile(pattern, re.I if ignore_case else 0)
    except re.PatternError:
        raise click.BadParameter(
            "must be a valid regular expression.",
            param_hint="--pattern",
        )

    for path in filenames:
        if not path.exists():
            raise FileNotFoundError(str(path))

        try:
            grid = Grid(path, header=header, skip=skip)
        except BaseException as e:
            exit(f"Could not read {str(path)!r}: {e}.")

        match = grid.match(regex)
        if out:
            if match:
                match.write(out)
            else:
                print(f"No matches, {str(out)!r} not written to.", file=sys.stderr)
        else:
            if match:
                if len(filenames) == 1:
                    print_filenames = not no_filename and filenames_always
                else:
                    print_filenames = not no_filename
                print(
                    match.format(
                        count=count,
                        filenames=print_filenames,
                        missing=missing,
                        color=color,
                        row_numbers=row_numbers,
                        col_numbers=col_numbers,
                    )
                )
