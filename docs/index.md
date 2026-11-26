---
hide:
  - navigation
---

# sytax

**Syrian salary and compensation taxes, from the command line.**

`sytax` works out the taxes, social security and net of a gross salary, finds the gross
that pays a wanted net, and builds whole salary scales, under the rules of the Syrian
salary tax law. The rules come from a bundled **preset**, so out of the box you
configure nothing, and when the law or your company differs, you change only that value.

```console
$ sytax gross 1000000 100000
            Gross Salary
┌────────────────────┬──────────────┐
│ Item               │       Amount │
├────────────────────┼──────────────┤
│ Salary             │ 1,000,000.00 │
│ Compensation       │   100,000.00 │
│ Total              │ 1,100,000.00 │
│ Social Security    │         0.00 │
│ Salary Tax         │    20,900.00 │
│ Compensation Tax   │     5,000.00 │
│ Taxes              │    25,900.00 │
│ Deductions         │    25,900.00 │
│ Net                │ 1,074,100.00 │
│ Compensation Ratio │        9.09% │
└────────────────────┴──────────────┘
```

Built on the [syriantaxes](https://pypi.org/project/syriantaxes/) library.

## Why sytax

<div class="grid cards" markdown>

-   :material-arrow-right-bold: **Gross to net**

    ---

    Salary tax by brackets, the flat tax on compensations, and social security, for any
    gross salary and compensations.

-   :material-arrow-left-bold: **Net to gross**

    ---

    "What gross pays 1,500,000 net, a quarter as compensations?" Answered exactly, with
    taxes rounded the way the law rounds them.

-   :material-table-large: **Salary scales**

    ---

    The gross for every net from START to STOP, as a table, JSON, or an Excel file
    ready for HR.

-   :material-tune-variant: **Rules you can change**

    ---

    Brackets, rates, minimum salary, rounding and social security, from a config file,
    an environment variable or one option.

-   :material-layers-outline: **Layered configuration**

    ---

    The law, your company, one payroll folder, a script: each layer overrides only what
    it sets, and `config show --sources` tells you who set what.

-   :material-file-export-outline: **Tables, JSON, Excel, CSV**

    ---

    Print a table or JSON, or export `.xlsx`, `.csv`, `.json` and `.jsonl` for
    spreadsheets and scripts.

</div>

## A taste

=== "Gross to net"

    ```bash
    sytax gross 1000000 100000
    ```

=== "Net to gross"

    ```bash
    # what gross pays 1,500,000 net, a quarter of it as compensations?
    sytax net 1500000 -r 0.25
    ```

=== "A salary scale in Excel"

    ```bash
    sytax range 1000000 2000000 100000 -r 0.25 -e scale.xlsx
    ```

=== "JSON for scripts"

    ```bash
    sytax gross 1000000 -o json
    ```

## Where to go next

- New here? [Install it](install.md), then follow the [user guide](guide/index.md).
- Have a job to do? See the [recipes](recipes.md): a salary offer, a salary scale for
  HR, insured employees, comparing a draft law, payroll scripts.
- Looking something up? The [reference](reference/index.md) lists every command,
  option, setting, environment variable and error.

!!! warning "Check the rules"
    sytax computes what its preset says the law is. Laws change: run `sytax rules`, and
    compare it with the current decree before relying on the numbers.
