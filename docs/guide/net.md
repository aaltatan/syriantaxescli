# Net to gross

```text
sytax net TARGET [-r SHARE] [output options]
```

`net` answers the question HR and candidates actually ask: **what gross pays this
net?** It finds the gross salary (and compensations) whose net is the target.

```console
$ sytax net 1500000
             Net Salary
┌────────────────────┬──────────────┐
│ Item               │       Amount │
├────────────────────┼──────────────┤
│ Salary             │ 1,610,505.00 │
│ Compensation       │         0.00 │
│ Total              │ 1,610,505.00 │
│ Social Security    │         0.00 │
│ Salary Tax         │   110,500.00 │
│ Compensation Tax   │         0.00 │
│ Taxes              │   110,500.00 │
│ Deductions         │   110,500.00 │
│ Net                │ 1,500,005.00 │
│ Compensation Ratio │        0.00% │
└────────────────────┴──────────────┘
```

## Why the net is a little above the target

Taxes are rounded to the nearest 100, so not every net can be reached exactly. sytax
finds the **smallest gross whose net is at least the target**: here 1,610,505 gives
1,500,005, five pounds more than asked. The net is never below the target.

## Paying part as compensations

`-r, --compensations-rate` pays that share of the net as compensations, and the rest as
salary. Compensations are taxed at a flat 5%, less than the top brackets, so the same
net costs less:

```console
$ sytax net 1500000 -r 0.25
             Net Salary
┌────────────────────┬──────────────┐
│ Item               │       Amount │
├────────────────────┼──────────────┤
│ Salary             │ 1,169,329.00 │
│ Compensation       │   394,700.00 │
│ Total              │ 1,564,029.00 │
│ Social Security    │         0.00 │
│ Salary Tax         │    44,300.00 │
│ Compensation Tax   │    19,700.00 │
│ Taxes              │    64,000.00 │
│ Deductions         │    64,000.00 │
│ Net                │ 1,500,029.00 │
│ Compensation Ratio │       25.24% │
└────────────────────┴──────────────┘
```

| `-r` | Gross for 1,500,000 net | Taxes |
|------|-------------------------|-------|
| `0` (default) | 1,610,505 | 110,500 |
| `0.25` | 1,564,029 | 64,000 |

The share is of the **net**: 25% of the 1,500,000 is paid as compensations after their
tax. The ratio of the gross (25.24%) is a little higher, because compensations are
grossed up by their 5% tax.

!!! note "The salary never goes below the minimum"
    When the salary part would fall below the minimum salary (837,000), the salary is kept
    at the minimum, and the rest is paid as compensations:

    ```console
    $ sytax net 1000000 -r 0.25 -o json
    {
        "salary": 837000,
        "compensation": 171600,
        "total": 1008600,
        "social_security": 0,
        "salary_tax": 0,
        "compensation_tax": 8600,
        "taxes": 8600,
        "deductions": 8600,
        "net": 1000000,
        "compensation_ratio": 0.1701368233194527
    }
    ```

    Here 75% of 1,000,000 would be 750,000, below the minimum, so the salary is 837,000.

The default share comes from the setting `net.compensation_share` (0 in the preset).
Set it once in a config file when your company always pays a quarter as compensations:
see [Configuration](configuration.md).

## Limits

The target must be at least the minimum salary:

```console
$ sytax net 800000
Invalid value for 'TARGET': Can't be calculated for salary less than 837000.
```

and the share between 0 and 1:

```console
$ sytax net 1500000 -r 1.5
Invalid value: compensation_share must be between 0 and 1, got 1.5
```

## Social security

With social security on, `net` finds the gross whose net is the target **after** social
security too, so the gross is higher:

```console
$ sytax --ss net 1500000 -o json --json-indent 0
{"salary": 1731726, "compensation": 0, "total": 1731726, "social_security": 121221, "salary_tax": 110500, "compensation_tax": 0, "taxes": 110500, "deductions": 231721, "net": 1500005, "compensation_ratio": 0}
```

`net` bases social security on the salary it finds. When the insured salary differs,
check the package with [`gross --insured-salary`](gross.md#social-security).
