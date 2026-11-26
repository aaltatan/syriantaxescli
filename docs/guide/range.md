# Salary scales

```text
sytax range START [STOP] [STEP] [-r SHARE] [output options]
```

`range` runs [`net`](net.md) for every net total from START to STOP (inclusive), every
STEP: a **salary scale** (سلم رواتب), showing what each net costs in gross.

```console
$ sytax range 1500000 2000000 250000 -r 0.25
                                                   Salary Scale
┌───┬──────────────┬──────────────┬──────────────┬─────────────────┬────────────┬──────────────────┬──────────────┐
│ # │       Salary │ Compensation │        Total │ Social Security │ Salary Tax │ Compensation Tax │          Net │
├───┼──────────────┼──────────────┼──────────────┼─────────────────┼────────────┼──────────────────┼──────────────┤
│ 1 │ 1,169,329.00 │   394,700.00 │ 1,564,029.00 │            0.00 │  44,300.00 │        19,700.00 │ 1,500,029.00 │
│ 2 │ 1,389,917.00 │   460,500.00 │ 1,850,417.00 │            0.00 │  77,400.00 │        23,000.00 │ 1,750,017.00 │
│ 3 │ 1,610,505.00 │   526,300.00 │ 2,136,805.00 │            0.00 │ 110,500.00 │        26,300.00 │ 2,000,005.00 │
└───┴──────────────┴──────────────┴──────────────┴─────────────────┴────────────┴──────────────────┴──────────────┘
```

The table leaves out Taxes and Deductions, which the other columns already add up to.
JSON and exported files have every column.

## STOP and STEP

Both are optional:

| Argument | Default | With START = 1,000,000 |
|----------|---------|------------------------|
| `STOP` | START × 10 (`range.stop_factor`) | 10,000,000 |
| `STEP` | START ÷ 10 (`range.step_divisor`) | 100,000 |

So `sytax range 1000000` builds 91 rows, from 1,000,000 to 10,000,000 every 100,000.
Give STOP alone to keep the default step:

```console
$ sytax range 1000000 1100000
...
│ 1 │ 1,024,100.00 │         0.00 │ 1,024,100.00 │            0.00 │  24,100.00 │             0.00 │ 1,000,000.00 │
│ 2 │ 1,139,917.00 │         0.00 │ 1,139,917.00 │            0.00 │  39,900.00 │             0.00 │ 1,100,017.00 │
```

## Size limit

A range has at most **1,000 rows** (`range.max_size`), so a typo does not run for
minutes:

```console
$ sytax range 1000000 1000000000 1
Invalid value: the range has 999,000,001 amounts but at most 1,000 are allowed; use a bigger step or a smaller range
```

STOP must not be below START:

```console
$ sytax range 1000000 900000
Invalid value: stop (900000) must not be less than start (1000000)
```

## For HR

A salary scale is usually handed over as a spreadsheet:

```bash
sytax range 1000000 3000000 100000 -r 0.25 -e scale.xlsx
```

See [Output and export](output.md), and the
[salary scale recipe](../recipes.md#a-salary-scale-for-hr).
