# syriantaxescli

A command-line tool for calculating Syrian salary and compensation taxes, built with
[Typer](https://typer.tiangolo.com/) on top of the [syriantaxes](https://pypi.org/project/syriantaxes/) library.

## Features

- **Gross to net:** the taxes, social security and net of a gross salary and compensations.
- **Net to gross:** the gross salary and compensations that pay a wanted net total.
- **Salary scales:** the gross for a whole range of net totals.
- **Tax rules you can change:** brackets, rates, minimum salary, rounding and social security, from
  options or environment variables; `sytax rules` shows what is in use.
- **Output:** rich tables or JSON, or export to `.xlsx`, `.csv`, `.json` or `.jsonl`.

## Installation

```bash
pip install syriantaxescli
```

Or with uv:

```bash
uv tool install syriantaxescli
```

## Usage

```bash
sytax [GLOBAL OPTIONS] COMMAND [ARGS] [OPTIONS]
```

| Command         | Aliases    | What it does                                                      |
| --------------- | ---------- | ----------------------------------------------------------------- |
| `gross`         | `g`        | Taxes and net of a gross salary and (optional) compensations.     |
| `net`           | `n`        | Gross salary and compensations for a wanted net total.            |
| `range`         | `ar`, `r`  | A salary scale for net totals from START to STOP every STEP.      |
| `rules`         |            | The tax rules in use, after config files, env vars and options.   |
| `config`        | `cfg`      | `show`, `path`, `init`, `presets`: see [Configuration](#configuration). |

Amounts can be written as `1000000`, `1,000,000`, `1_000_000` or `1e6`.

### Examples

```bash
# 1,000,000 salary and 100,000 compensations
sytax gross 1000000 100000

# The same, with social security on an insured salary of 750,000
sytax gross 1000000 100000 --insured-salary 750000

# What gross pays 1,500,000 net, a quarter of it as compensations?
sytax net 1500000 -r 0.25

# A salary scale from 1M to 2M net, exported to Excel
sytax range 1000000 2000000 100000 -r 0.25 -e scale.xlsx

# JSON for scripts
sytax gross 1000000 -o json
```

`range` defaults STOP to START x 10 and STEP to START / 10, and allows at most 1,000 rows
(all three are settings).

### Output options

| Option                              | Description                                                         |
| ----------------------------------- | ------------------------------------------------------------------- |
| `-o`, `--output [table\|json]`      | Print a table or JSON (default: setting `output.format`).          |
| `--json-indent N`                   | JSON indentation; `0` prints one line (setting `output.json_indent`). |
| `-e`, `--export PATH`               | Write a `.xlsx`, `.csv`, `.json` or `.jsonl` file instead.          |
| `--overwrite`                       | Replace the export file if it exists (otherwise it is an error).    |

## Configuration

No value is hard-coded. Every default (brackets, rates, rounding, minimums, social security,
output format, range limits, the default compensation share) comes from a **preset**: a TOML
file bundled with sytax that describes one version of the law. Out of the box you configure
nothing. When something differs for you, override only that value, in the layer that fits:

| Precedence  | Layer                                       | Use it for                              |
| ----------- | ------------------------------------------- | --------------------------------------- |
| 1 (lowest)  | preset (`--preset`; default: the newest)    | The law itself                          |
| 2           | user file `config.toml`                     | Your company's settings, everywhere     |
| 3           | project file `sytax.toml`                   | One payroll folder (found from the current folder upward) |
| 4           | `--config FILE` / `SYRIANTAXES_CONFIG`      | A file shared by a team                 |
| 5           | `.env` and `SYRIANTAXES_*` env vars         | CI, scripts, containers                 |
| 6           | global options (`--ss`, `--fixed-tax-rate`, ...) | One-off overrides                  |
| 7 (highest) | `-s/--set KEY=VALUE`                        | Any setting, one-off                    |

Tables merge key by key; lists (brackets) are replaced as a whole. `sytax config path` shows where
the user file lives (override its folder with `SYRIANTAXES_CONFIG_HOME`).

```bash
sytax config init              # write ./sytax.toml: the preset, every key commented out
sytax config init --user       # the same, for every folder
sytax config show --sources    # every setting and the layer that set it
sytax config show -o toml      # the effective settings, as a config file
sytax config presets           # the bundled presets
```

A config file holds only what you change:

```toml
preset = "syria-2024"

[tax]
min_salary = 900_000

[net]
compensation_share = 0.25   # net and range pay a quarter as compensations unless -r says otherwise
```

One-off overrides go **before** the command:

```bash
sytax --ss gross 1000000
sytax --fixed-tax-rate 0.04 net 1500000
sytax -s tax.min_salary=900000 -s output.format=json range 1000000
sytax --preset syria-2024 gross 1000000 100000
```

### Default rules (preset `syria-2024`)

| Salary bracket          | Rate |
| ----------------------- | ---- |
| 0 – 837,000             | 0%   |
| 837,000 – 850,000       | 11%  |
| 850,000 – 1,100,000     | 13%  |
| 1,100,000 and above     | 15%  |

- Compensations are taxed at a flat 5%.
- Taxes are rounded half up to the nearest 100.
- Net targets below the 837,000 minimum salary can't be calculated.
- Social security (7%, minimum insured salary 750,000) is **off** unless you pass `--ss`,
  set `tax.social_security.enabled = true`, or give `gross` an `--insured-salary`.

### Global options and environment variables

| Global option               | Environment variable                 | Setting                               |
| --------------------------- | ------------------------------------ | ------------------------------------- |
| `--preset`                  | `SYRIANTAXES_PRESET`                 | `preset`                              |
| `--config`                  | `SYRIANTAXES_CONFIG`                 |                                       |
| `--brackets-mins`           | `SYRIANTAXES_BRACKET_TAX_MINS`       | `tax.brackets[].lower`                |
| `--brackets-rates`          | `SYRIANTAXES_BRACKET_TAX_RATES`      | `tax.brackets[].rate`                 |
| `--min-allowed-salary`      | `SYRIANTAXES_MIN_ALLOWED_SALARY`     | `tax.min_salary`                      |
| `--fixed-tax-rate`          | `SYRIANTAXES_FIXED_TAX_RATE`         | `tax.compensation_tax_rate`           |
| `--taxes-rounding-method`   | `SYRIANTAXES_TAXES_ROUNDING_METHOD`  | `tax.rounding.method`                 |
| `--taxes-round-to-nearest`  | `SYRIANTAXES_TAXES_ROUND_TO_NEAREST` | `tax.rounding.step`                   |
| `--ss/--no-ss`              | `SYRIANTAXES_SS_ENABLED`             | `tax.social_security.enabled`         |
| `--ss-deduction-rate`       | `SYRIANTAXES_SS_DEDUCTION_RATE`      | `tax.social_security.rate`            |
| `--min-ss-allowed-salary`   | `SYRIANTAXES_MIN_SS_ALLOWED_SALARY`  | `tax.social_security.min_salary`      |
| `--ss-rounding-method`      | `SYRIANTAXES_SS_ROUNDING_METHOD`     | `tax.social_security.rounding.method` |
| `--ss-round-to-nearest`     | `SYRIANTAXES_SS_ROUND_TO_NEAREST`    | `tax.social_security.rounding.step`   |

Brackets are given by their lower bounds; each runs up to the next one and the last has no top.
Repeat the option once per bracket (`--brackets-mins 0 --brackets-mins 1000000 ...`), or separate
values with spaces in the environment variable; always set both lists. Rounding methods are the
`decimal` module's modes, in any case and with or without `ROUND_` (`ceiling`, `ROUND_HALF_EVEN`).

### Adding a preset when the law changes

Copy the newest file in `src/syriantaxescli/presets/`, name it after the new law (names sort by
date and the last one is the default), and change the values. A test checks that every preset
is complete.

### Upgrading from 0.1

- syriantaxes 1.0 defines brackets by their lower bounds only, so `--brackets-maxs` and
  `SYRIANTAXES_BRACKET_TAX_MAXS` are gone; the last bracket has no top.
- `gross` takes the insured salary as `-i/--insured-salary` instead of a third argument.
- `-r/--compensations-rate` defaults to `net.compensation_share` (0 in the preset).
- `ar` is now `range`; `ar` still works as an alias.
- Tax-rule options are global and go before the command: `sytax --ss gross 1e6`.
  The environment variable names are unchanged.
- `rules` lost its `config` alias; `config` is now the configuration command group.
- `--write-path` is now `-e/--export` (the old name still works), and every command can export.
- JSON lines files have one compact object per line.

## Project structure

```text
src/syriantaxescli/
├── main.py                 # Builds the Typer app; `sytax` entry point
├── core/                   # Calculations, independent of the CLI
│   ├── config.py           # Layered config loading: presets, files, env, options
│   ├── settings.py         # The settings model (pydantic), with no defaults in code
│   ├── rounding.py         # Rounding methods and rules
│   ├── salary.py           # The Salary result
│   └── services.py         # gross / net / range calculations on syriantaxes
├── presets/                # Bundled law presets (TOML): the only defaults
└── cli/
    ├── callback.py         # Root callback: --version, global options, lazy settings
    ├── commands/           # One Typer app per command: gross, net, range, rules, config
    ├── dependencies/       # typer-di dependencies: context, settings, overrides, output
    ├── options.py          # Shared options
    ├── parsers.py          # Decimal parsing
    ├── renderers.py        # Tables and JSON
    └── exporters.py        # .xlsx, .csv, .json, .jsonl
```

## Development

```bash
uv sync
uv run pytest        # with branch coverage; fails below 100%
uv run mypy
uv run ruff check
uv run ruff format --check
```

## License

GNU General Public License v3 (GPLv3)
