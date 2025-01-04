## xgrep

### Documentation

Can be found at [https://xgrep.readthedocs.io](https://xgrep.readthedocs.io/)

### Installation

```
$ pip install xgrep
```

Usage is similar to regular `grep`. Give a pattern and then one or more
filenames. There are various options (some with the same name and effect as
`grep` options, like `-c`, `-h`, `-H`, `-i`, `-q`, and `-v`). Run `xgrep
--help` for a full listing.

### Example usage

To give an example of using `xgrep`, suppose you have an Excel file (`example.xlsx`)) with a
sheet that looks like this:

<img src="https://github.com/terrycojones/xgrep/blob/main/docs/source/images/excel-example.png" width="600" style="border:1px solid #CCC"/>

You can download
[example.xlsx](https://github.com/terrycojones/xgrep/blob/main/docs/source/example.xlsx)
(or find it in the `docs/source` directory in the repo) if you want to try
the following commands.

#### Find cells based on a regular expression

Look for the regular expression `'Xia|radius|Jilin'`:

```sh
$ xgrep 'Xia|radius|Jilin' example.xlsx
```

<img src="https://github.com/terrycojones/xgrep/blob/main/docs/source/images/search-1.png" width="600" style="border:1px solid #CCC"/>

Note that the command-line output is all text. It is produced using the
[Table class](https://rich.readthedocs.io/en/stable/tables.html) of the
wonderful [rich](https://rich.readthedocs.io/en/stable/introduction.html)
package.

#### Display the row and column information

Add the row numbers (`--rn`) and Excel column (`--ec`) information from the
input Excel:

```sh
$ xgrep --rn --ec 'Xia|radius|Jilin' example.xlsx
```

<img src="https://github.com/terrycojones/xgrep/blob/main/docs/source/images/search-2.png" width="600" style="border:1px solid #CCC"/>

#### De-emphasize unmatched cells

If you don't care about the values in cells that were not matched, you can
give a value to show in unmatched (`-u`) cells:

```sh
$ xgrep -u . --rn --ec 'Xia|radius|Jilin' example.xlsx
```

<img src="https://github.com/terrycojones/xgrep/blob/main/docs/source/images/search-3.png" width="600" style="border:1px solid #CCC"/>

#### Only show matching columns

To exclude columns with no matching cells, you can show only matching columns
(`--omc`):

```sh
$ xgrep --omc --rn --ec 'Xia|radius|Jilin' example.xlsx
```

<img src="https://github.com/terrycojones/xgrep/blob/main/docs/source/images/search-4.png" width="600" style="border:1px solid #CCC"/>

#### Write CSV (or TSV)

The default output format is a
[rich](https://rich.readthedocs.io/en/stable/introduction.html)
[Table](https://rich.readthedocs.io/en/stable/tables.html). You can also
produce CSV, TSV, or Excel using the `--format` option:

```sh
$ xgrep --format csv 'Xia|radius|Jilin' example.xlsx
```

<img src="https://github.com/terrycojones/xgrep/blob/main/docs/source/images/search-5.png" width="600" style="border:1px solid #CCC"/>

If you use `--format excel` you will also need to give an output filename
using `--out`.

### Usage

<pre>
Usage: xgrep [OPTIONS] PATTERN FILENAMES...

  Command-line interface.

Options:
  -o, --out FILE                  The output file. If not given, output is
                                  written to standard out. Note that if the
                                  --quiet (-q) option is also given, no output
                                  will be written to the output file.
  --header / --no-header          Don't look for a header line in input files.
                                  In this case, text in what would otherwise
                                  be considered a header can also be matched
                                  by the grep pattern.
  --skip INTEGER RANGE            Skip this many rows at the start of the
                                  input file(s).  [x>=0]
  --format [csv|excel|rich|tsv]   The output format. The 'rich' format
                                  produces a rich Table (see https://rich.read
                                  thedocs.io/en/stable/tables.html).
  -c, --count                     Only print the number of matching lines
                                  (like grep -c).
  --width INTEGER                 The width to use for --format rich tables.
  -v, --invert                    Only output rows that do not match (like
                                  grep -v).
  -q, --quiet, --silent           Do not show any output, just exit with a
                                  status indicating whether a match was found
                                  (0) or not (1) (like grep -q).
  --only-matching-cols, --omc, --mco
                                  Only show columns that have a matching cell.
  -i, --ignore-case               Ignore case while matching (like grep -i).
  --color TEXT                    The highlight color.
  -u, --unmatched TEXT            The string to show for cells whose values do
                                  not match. If not given, non-matching cells
                                  are shown with their value (in which case
                                  you will need to use the output color to see
                                  matches).
  -n, --row-numbers, --rn, --line-number
                                  Show row numbers (like grep -n).
  --col-numbers, --cn             Show column numbers.
  --excel-cols, --ec              Add Excel column labels to column names.
  Filenames: [mutually_exclusive]
                                  Whether to display names of matching files.
    -H, --filenames-always, --fa  Always print the name of matching files
                                  (like grep -H).
    -h, --no-filename, --nf       Never print the name of matching files (like
                                  grep -h).
    --only-filename, --of         Only print the names of matching files, not
                                  their matched content.
  --help                          Show this message and exit.
</pre>

### Todo

1. Document `format`, `polars_df`, and `rich_table` (in `readthedocs.io`).
1. Can `click` allow a `-e` option that also can be used to specify the pattern?
1. Make it possible to specify a sheet (only works if there is one Excel file?).
1. Adjust column names "Row" and "File" in case they're already present.
1. Allow for processing multiple Excel files into individual sheets.
1. Write tests for unequal numbers of cols.
