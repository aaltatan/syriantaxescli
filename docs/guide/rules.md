# The tax rules

`sytax rules` shows the rules in use **right now**: the preset, plus every config file,
environment variable and option on top of it. Run it whenever a number looks surprising.

```console
$ sytax rules
            Salary Tax Brackets
┌───┬──────────────┬──────────────┬────────┐
│ # │         From │           To │   Rate │
├───┼──────────────┼──────────────┼────────┤
│ 1 │         0.00 │   837,000.00 │  0.00% │
│ 2 │   837,000.00 │   850,000.00 │ 11.00% │
│ 3 │   850,000.00 │ 1,100,000.00 │ 13.00% │
│ 4 │ 1,100,000.00 │    and above │ 15.00% │
└───┴──────────────┴──────────────┴────────┘
                  Settings
┌──────────────────────────┬────────────────┐
│ Setting                  │          Value │
├──────────────────────────┼────────────────┤
│ Minimum salary           │     837,000.00 │
│ Compensation tax rate    │          5.00% │
│ Tax rounding             │ HALF_UP to 100 │
│ Social security          │            off │
│ Social security rate     │          7.00% │
│ Minimum insured salary   │     750,000.00 │
│ Social security rounding │   HALF_UP to 1 │
└──────────────────────────┴────────────────┘
```

## The rules of the preset `syria-2024`

| Rule | Value |
|------|-------|
| Salary brackets | 0% up to 837,000; 11% to 850,000; 13% to 1,100,000; 15% above |
| Minimum salary | 837,000: a net target below it cannot be calculated |
| Compensation tax | a flat 5% |
| Tax rounding | half up, to the nearest 100 |
| Social security | **off**; when on, 7% of the insured salary, at least 750,000, rounded half up to 1 |

## Changing a rule for one command

Rule options are **global**: they go before the command.

```console
$ sytax --taxes-round-to-nearest 1 gross 1000000 -o json
...
    "salary_tax": 20930,
...
```

| Option | Setting |
|--------|---------|
| `--brackets-mins`, `--brackets-rates` | `tax.brackets` |
| `--min-allowed-salary` | `tax.min_salary` |
| `--fixed-tax-rate` | `tax.compensation_tax_rate` |
| `--taxes-rounding-method`, `--taxes-round-to-nearest` | `tax.rounding` |
| `--ss` / `--no-ss` | `tax.social_security.enabled` |
| `--ss-deduction-rate` | `tax.social_security.rate` |
| `--min-ss-allowed-salary` | `tax.social_security.min_salary` |
| `--ss-rounding-method`, `--ss-round-to-nearest` | `tax.social_security.rounding` |

Every rule can also be set in a config file or an environment variable: see
[Configuration](configuration.md) and [Environment variables](../reference/environment.md).

### Brackets

Brackets are given by their **lower bounds**: each runs up to the next one, and the last
has no top. Repeat the options once per bracket, in the same order, and always give both
lists:

```console
$ sytax --brackets-mins 0 --brackets-mins 1000000 --brackets-rates 0 --brackets-rates 0.1 rules -o json
{
    "brackets": [
        {
            "lower": 0,
            "upper": 1000000,
            "rate": 0
        },
        {
            "lower": 1000000,
            "upper": null,
            "rate": 0.1
        }
    ],
...
```

A different number of bounds and rates is refused:

```console
$ sytax --brackets-mins 0 --brackets-mins 1000000 --brackets-rates 0 gross 1
Invalid value for '--brackets-mins' / '--brackets-rates': got 2 bracket lower bound(s) but 1 rate(s); every bracket needs both
```

### Rounding

Taxes and social security are rounded to a multiple of a **step**, with a **method**
from Python's `decimal` module:

| Method | 20,930 to the nearest 100 |
|--------|---------------------------|
| `ROUND_HALF_UP` (preset) | 20,900 |
| `ROUND_CEILING` | 21,000 |
| `ROUND_FLOOR` | 20,900 |
| `ROUND_HALF_EVEN` | 20,900 |

Also `ROUND_UP`, `ROUND_DOWN`, `ROUND_HALF_DOWN` and `ROUND_05UP`.

- In config files, `-s` and environment variables, any case works, with or without
  `ROUND_`: `ceiling`, `HALF_EVEN`, `round_half_up`.
- The `--taxes-rounding-method` and `--ss-rounding-method` options need the `ROUND_` names
  (in any case): `--taxes-rounding-method round_ceiling`.

### JSON

`sytax rules -o json` prints the rules for scripts. It does not take `--json-indent`;
the indentation comes from the setting `output.json_indent`.
