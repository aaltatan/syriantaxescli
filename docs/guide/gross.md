# Gross to net

```text
sytax gross SALARY [COMPENSATION] [-i INSURED_SALARY] [output options]
```

`gross` takes a gross salary, and optionally compensations, and works out every
deduction and the net.

```console
$ sytax gross 1000000
            Gross Salary
┌────────────────────┬──────────────┐
│ Item               │       Amount │
├────────────────────┼──────────────┤
│ Salary             │ 1,000,000.00 │
│ Compensation       │         0.00 │
│ Total              │ 1,000,000.00 │
│ Social Security    │         0.00 │
│ Salary Tax         │    20,900.00 │
│ Compensation Tax   │         0.00 │
│ Taxes              │    20,900.00 │
│ Deductions         │    20,900.00 │
│ Net                │   979,100.00 │
│ Compensation Ratio │        0.00% │
└────────────────────┴──────────────┘
```

## How the salary tax is worked out

The salary is taxed **by brackets**: each part of the salary is taxed at its bracket's
rate. With the preset `syria-2024`:

| Bracket | Rate | Part of 1,000,000 | Tax |
|---------|------|-------------------|-----|
| 0 to 837,000 | 0% | 837,000 | 0 |
| 837,000 to 850,000 | 11% | 13,000 | 1,430 |
| 850,000 to 1,100,000 | 13% | 150,000 | 19,500 |
| 1,100,000 and above | 15% | 0 | 0 |
| | | **Total** | **20,930** |

The tax is then **rounded half up to the nearest 100**: 20,930 becomes **20,900**.

A salary up to the minimum (837,000) pays no salary tax:

```console
$ sytax gross 500000 -o json
{
    "salary": 500000,
    "compensation": 0,
    "total": 500000,
    "social_security": 0,
    "salary_tax": 0,
    "compensation_tax": 0,
    "taxes": 0,
    "deductions": 0,
    "net": 500000,
    "compensation_ratio": 0
}
```

Just above it, only the part above is taxed: 3,000 × 11% = 330, rounded to 300:

```console
$ sytax gross 840000 -o json
...
    "salary_tax": 300,
...
    "net": 839700,
```

## Compensations

Compensations are taxed at a **flat 5%**, with no brackets:

```console
$ sytax gross 1000000 100000 -o json
{
    "salary": 1000000,
    "compensation": 100000,
    "total": 1100000,
    "social_security": 0,
    "salary_tax": 20900,
    "compensation_tax": 5000,
    "taxes": 25900,
    "deductions": 25900,
    "net": 1074100,
    "compensation_ratio": 0.09090909090909091
}
```

This is why paying part of a package as compensations lowers the taxes: see
[Net to gross](net.md#paying-part-as-compensations).

## Social security

Social security is **off** in the preset. Turn it on for an employee who is insured:

=== "the salary is insured"

    `--ss` deducts 7% of the salary before taxing it:

    ```console
    $ sytax --ss gross 1000000 -o json
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

    The tax is worked out on 1,000,000 − 70,000 = 930,000: 1,430 + 80,000 × 13% =
    11,830, rounded to 11,800.

=== "a different insured salary"

    Often the insured salary is not the whole salary. `-i, --insured-salary` gives it,
    and turns social security on by itself:

    ```console
    $ sytax gross 1000000 100000 --insured-salary 750000
                Gross Salary
    ┌────────────────────┬──────────────┐
    │ Item               │       Amount │
    ├────────────────────┼──────────────┤
    │ Salary             │ 1,000,000.00 │
    │ Compensation       │   100,000.00 │
    │ Total              │ 1,100,000.00 │
    │ Social Security    │    52,500.00 │
    │ Salary Tax         │    14,100.00 │
    │ Compensation Tax   │     5,000.00 │
    │ Taxes              │    19,100.00 │
    │ Deductions         │    71,600.00 │
    │ Net                │ 1,028,400.00 │
    │ Compensation Ratio │        9.09% │
    └────────────────────┴──────────────┘
    ```

    7% of 750,000 is 52,500.

| Setting | Preset | Option |
|---------|--------|--------|
| On or off | off | `--ss` / `--no-ss` |
| Rate | 7% | `--ss-deduction-rate` |
| Minimum insured salary | 750,000 | `--min-ss-allowed-salary` |
| Rounding | half up to 1 | `--ss-rounding-method`, `--ss-round-to-nearest` |

For a whole payroll of insured employees, set it once in a config file instead: see
[Configuration](configuration.md) and
[`social-security.toml`](https://github.com/aaltatan/syriantaxescli/blob/main/examples/social-security.toml).

## The result

| Row | Meaning |
|-----|---------|
| Salary, Compensation | What you gave |
| Total | Salary + compensation |
| Social Security | 0 unless social security is on |
| Salary Tax | By brackets, on the salary minus social security, rounded |
| Compensation Tax | Flat rate on the compensations, rounded |
| Taxes | Salary tax + compensation tax |
| Deductions | Social security + taxes |
| Net | Total − deductions |
| Compensation Ratio | Compensation ÷ total |

Negative amounts are refused:

```console
$ sytax gross -- -5
Invalid value for 'salary': '-5' must not be negative.
```
