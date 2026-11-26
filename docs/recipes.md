# Recipes

Real-world payroll jobs. Commands shown with their output are run by the test suite.

## A salary offer

**Job:** a candidate asks for 1,500,000 net a month. What does it cost the company, and
what goes on the contract?

```console
$ sytax net 1500000
...
│ Salary             │ 1,610,505.00 │
...
│ Net                │ 1,500,005.00 │
...
```

Paying a quarter of it as compensations lowers the cost by about 46,000 a month:

```console
$ sytax net 1500000 -r 0.25
...
│ Salary             │ 1,169,329.00 │
│ Compensation       │   394,700.00 │
│ Total              │ 1,564,029.00 │
...
│ Net                │ 1,500,029.00 │
...
```

Put the salary and the compensation on the contract, and check them the other way:

```console
$ sytax gross 1169329 394700 -o json
...
    "net": 1500029,
...
```

## A salary scale for HR

**Job:** HR wants the gross for every net from 1,000,000 to 3,000,000, in steps of
100,000, with a quarter as compensations, as an Excel file.

```bash
sytax range 1000000 3000000 100000 -r 0.25 -e scale.xlsx
```

The sheet has one row per net, with every column: salary, compensation, total, social
security, salary tax, compensation tax, taxes, deductions, net and compensation ratio.
Sort or filter it in Excel, or join it with the employee list by net.

When the company always pays a quarter as compensations, put it in the payroll folder's
`sytax.toml` once, and drop `-r`:

```toml
[net]
compensation_share = 0.25
```

## Insured employees

**Job:** every employee on this payroll is insured, on the salary or on a lower
insured amount.

For the whole payroll folder, turn social security on in `sytax.toml`, as in
[`social-security.toml`](https://github.com/aaltatan/syriantaxescli/blob/main/examples/social-security.toml):

```toml
[tax.social_security]
enabled = true
```

```console
$ sytax --config social-security.toml gross 1000000 -o json
{
    "salary": 1000000,
    "compensation": 0,
    "total": 1000000,
    "social_security": 70000,
    "salary_tax": 11800,
    "compensation_tax": 0,
    "taxes": 11800,
    "deductions": 81800,
    "net": 918200,
    "compensation_ratio": 0
}
```

For one employee insured on 750,000:

```bash
sytax gross 1000000 100000 --insured-salary 750000
```

## Compare a draft law

**Job:** a new law is announced. How does it change each salary?

Write the new rules in a file, like
[`draft-law.toml`](https://github.com/aaltatan/syriantaxescli/blob/main/examples/draft-law.toml),
and run the same command with and without it:

```console
$ sytax gross 1500000 -o json
...
    "net": 1406100,
...
$ sytax --config draft-law.toml gross 1500000 -o json
...
    "net": 1450000,
...
```

For a whole scale, export both and compare them side by side:

```bash
sytax range 1000000 3000000 250000 -e current.xlsx
sytax --config draft-law.toml range 1000000 3000000 250000 -e draft.xlsx
```

See [Presets and law changes](guide/presets.md).

## The payroll for a list of employees

**Job:** a CSV of employees with their salaries and compensations; compute each net.

`employees.csv`:

```text
name,salary,compensation
Rama,1000000,100000
Omar,1500000,250000
```

=== "PowerShell"

    ```powershell
    Import-Csv employees.csv | ForEach-Object {
        $r = sytax gross $_.salary $_.compensation -o json | ConvertFrom-Json
        [pscustomobject]@{ Name = $_.name; Taxes = $r.taxes; Net = $r.net }
    } | Export-Csv payroll.csv -NoTypeInformation
    ```

=== "bash"

    ```text
    tail -n +2 employees.csv | while IFS=, read -r name salary compensation; do
      echo "$name,$(sytax gross "$salary" "$compensation" -o json | jq -r '.net')"
    done > payroll.csv
    ```

=== "Python"

    ```python
    import csv
    import json
    import subprocess

    with open("employees.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out = subprocess.check_output(
                ["sytax", "gross", row["salary"], row["compensation"], "-o", "json"]
            )
            print(row["name"], json.loads(out)["net"])
    ```

For a large payroll, call the [syriantaxes](https://pypi.org/project/syriantaxes/)
library from Python directly instead of starting `sytax` once per employee.

## The same numbers on every machine

**Job:** the payroll is run by several people, and in CI. Everyone must get the same
numbers.

1. Put the company's settings in a `sytax.toml` at the root of the payroll repository
   or shared folder. Every run from inside it uses them.
2. Pin the preset: `preset = "syria-2024"`. A newer sytax with a newer default preset
   then keeps computing last year's payroll the same way.
3. In CI, check what is in use before computing:

    ```bash
    sytax config show --sources
    sytax rules -o json
    ```

## Round to the pound

**Job:** a report needs the exact tax, before the law's rounding to 100.

```console
$ sytax --taxes-round-to-nearest 1 gross 1000000 -o json
...
    "salary_tax": 20930,
...
```
