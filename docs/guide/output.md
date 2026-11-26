# Output and export

`gross`, `net` and `range` print a table by default. They can print JSON, or write a
file instead.

| Option | Meaning |
|--------|---------|
| `-o, --output table\|json` | Print a table or JSON (default: setting `output.format`, `table`) |
| `--json-indent N` | JSON indentation; `0` prints one line (default: `output.json_indent`, 4) |
| `-e, --export PATH` | Write a `.xlsx`, `.csv`, `.json` or `.jsonl` file instead of printing |
| `--overwrite` | Replace the export file if it exists |

## Tables

`gross` and `net` print a card of every amount; `range` prints one row per net. Amounts
have thousands separators and two decimals, and the ratio is a percentage.

## JSON

```console
$ sytax gross 1000000 -o json --json-indent 0
{"salary": 1000000, "compensation": 0, "total": 1000000, "social_security": 0, "salary_tax": 20900, "compensation_tax": 0, "taxes": 20900, "deductions": 20900, "net": 979100, "compensation_ratio": 0}
```

- Every field of the result, under its key: `salary`, `compensation`, `total`,
  `social_security`, `salary_tax`, `compensation_tax`, `taxes`, `deductions`, `net`,
  `compensation_ratio`.
- Amounts are plain numbers: no separators, and whole numbers without decimals.
- `range` prints a list of these objects.

Read it from a script:

=== "PowerShell"

    ```powershell
    $r = sytax gross 1000000 -o json | ConvertFrom-Json
    $r.net    # 979100
    ```

=== "bash"

    ```text
    sytax gross 1000000 -o json | jq .net    # 979100
    ```

=== "Python"

    ```python
    import json
    import subprocess

    result = json.loads(subprocess.check_output(["sytax", "gross", "1000000", "-o", "json"]))
    print(result["net"])  # 979100
    ```

## Export

`-e, --export` writes a file; the format comes from the extension:

| Extension | Content |
|-----------|---------|
| `.xlsx` | An Excel sheet, a header row and one row per result |
| `.csv` | The same, comma separated |
| `.json` | A JSON list of results |
| `.jsonl` | One compact JSON object per line |

```bash
sytax range 1000000 -e scale.xlsx
sytax gross 1000000 100000 -e employee.csv
sytax net 1500000 -r 0.25 -e offer.json
```

```console
$ sytax range 1000000 -e scale.csv
Exported 91 row(s) to ...
```

A `.csv` has the same keys as the JSON as its header:

```text
salary,compensation,total,social_security,salary_tax,compensation_tax,taxes,deductions,net,compensation_ratio
1000000,0,1000000,0,20900,0,20900,20900,979100,0
```

An existing file is never replaced without `--overwrite`, and other extensions are
refused:

```console
$ sytax gross 1000000 -e out.txt
Invalid value for '-e' / '--export': Can't export to '.txt' files; use one of: .xlsx, .csv, .json, .jsonl
```

## JSON by default

To always get JSON (for a script, say), set it once instead of passing `-o json`:

```console
$ sytax -s output.format=json gross 1000000
{
    "salary": 1000000,
...
    "net": 979100,
```

or in a config file, `format = "json"` under `[output]`. See
[Configuration](configuration.md).
