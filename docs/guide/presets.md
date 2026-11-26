# Presets and law changes

A **preset** is a TOML file bundled with sytax that describes one version of the law,
with **every** setting. It is the lowest configuration layer, and the only place
defaults live.

```console
$ sytax config presets
...
│ syria-2024 │   yes   │
...
```

The newest preset is the default. `--preset` (or `SYRIANTAXES_PRESET`, or `preset = ...`
in a config file) picks another:

```bash
sytax --preset syria-2024 gross 1000000 100000
```

## The preset `syria-2024`

```toml
# Syrian salary tax rules. Every setting must be here: presets are the only defaults.
# Config files, environment variables and options override any of these values.

[tax]
# Net targets below the minimum salary can't be calculated.
min_salary = 837_000
# Flat tax on compensations.
compensation_tax_rate = 0.05

[tax.rounding]
method = "HALF_UP"
step = 100

# Each bracket runs from its lower bound to the next one's; the last has no top.
[[tax.brackets]]
lower = 0
rate = 0

[[tax.brackets]]
lower = 837_000
rate = 0.11

[[tax.brackets]]
lower = 850_000
rate = 0.13

[[tax.brackets]]
lower = 1_100_000
rate = 0.15

[tax.social_security]
enabled = false
rate = 0.07
min_salary = 750_000

[tax.social_security.rounding]
method = "HALF_UP"
step = 1

[net]
# Share of a net target paid as compensation when -r is not given.
compensation_share = 0

[output]
format = "table"
json_indent = 4

[range]
# The most rows a range may have, and the defaults for STOP (START x stop_factor)
# and STEP (START / step_divisor).
max_size = 1000
stop_factor = 10
step_divisor = 10
```

## When the law changes

### Before a new release: a config file

A new decree is published, and sytax has no preset for it yet. Write the changes in a
config file, and use it with `--config` (or as the project `sytax.toml`):
[`examples/draft-law.toml`](https://github.com/aaltatan/syriantaxescli/blob/main/examples/draft-law.toml)
is a made-up example:

```toml
# A draft law to compare with the current one: a higher minimum salary
# and new brackets. Brackets are replaced as a whole list.
preset = "syria-2024"

[tax]
min_salary = 1_000_000

[[tax.brackets]]
lower = 0
rate = 0

[[tax.brackets]]
lower = 1_000_000
rate = 0.10

[[tax.brackets]]
lower = 2_000_000
rate = 0.15
```

```console
$ sytax --config draft-law.toml rules
            Salary Tax Brackets
┌───┬──────────────┬──────────────┬────────┐
│ # │         From │           To │   Rate │
├───┼──────────────┼──────────────┼────────┤
│ 1 │         0.00 │ 1,000,000.00 │  0.00% │
│ 2 │ 1,000,000.00 │ 2,000,000.00 │ 10.00% │
│ 3 │ 2,000,000.00 │    and above │ 15.00% │
└───┴──────────────┴──────────────┴────────┘
...
│ Minimum salary           │   1,000,000.00 │
...
```

Compare the two laws for the same salary:

```console
$ sytax gross 1500000 -o json
...
    "salary_tax": 93900,
...
$ sytax --config draft-law.toml gross 1500000 -o json
...
    "salary_tax": 50000,
...
```

### In sytax: a new preset

To add the law to sytax itself:

1. Copy the newest file in `src/syriantaxescli/presets/`.
2. Name it after the new law: names sort by date, and the last one is the default
   (`syria-2026.toml` comes after `syria-2024.toml`).
3. Change the values.
4. Run the tests: one of them checks that every preset is complete.

The old preset stays, so last year's payroll can still be recalculated with
`--preset syria-2024`.
