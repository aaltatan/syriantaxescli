# Commands and options

```text
sytax [GLOBAL OPTIONS] COMMAND [ARGS] [OPTIONS]
```

## Global options

Global options go **before** the command.

| Option | Setting | Meaning |
|--------|---------|---------|
| `-v, --version` | | Show the version and exit |
| `--preset NAME` | `preset` | The tax law preset to start from (`sytax config presets`) |
| `--config FILE` | | An extra config file, on top of the user and project ones |
| `-s, --set KEY=VALUE` | any | Override any setting; repeatable |
| `--brackets-mins AMOUNT` | `tax.brackets[].lower` | Lower bound of each bracket; repeat once per bracket |
| `--brackets-rates RATE` | `tax.brackets[].rate` | Rate of each bracket, in the same order |
| `--min-allowed-salary AMOUNT` | `tax.min_salary` | Minimum salary; a net target below it can't be calculated |
| `--fixed-tax-rate RATE` | `tax.compensation_tax_rate` | Flat tax rate on compensations |
| `--taxes-rounding-method METHOD` | `tax.rounding.method` | `ROUND_HALF_UP`, `ROUND_CEILING`, ... |
| `--taxes-round-to-nearest AMOUNT` | `tax.rounding.step` | Taxes are rounded to a multiple of this |
| `--ss` / `--no-ss` | `tax.social_security.enabled` | Deduct social security before taxing the salary |
| `--ss-deduction-rate RATE` | `tax.social_security.rate` | Social security rate |
| `--min-ss-allowed-salary AMOUNT` | `tax.social_security.min_salary` | Minimum insured salary |
| `--ss-rounding-method METHOD` | `tax.social_security.rounding.method` | How social security is rounded |
| `--ss-round-to-nearest AMOUNT` | `tax.social_security.rounding.step` | Social security is rounded to a multiple of this |
| `--install-completion`, `--show-completion` | | Shell completion |
| `--help` | | Help; also after any command |

## Output options

`gross`, `net` and `range` take these, **after** the command:

| Option | Default | Meaning |
|--------|---------|---------|
| `-o, --output table\|json` | `output.format` | Print a table or JSON |
| `--json-indent N` | `output.json_indent` | JSON indentation; `0` prints one line |
| `-e, --export PATH` | | Write `.xlsx`, `.csv`, `.json` or `.jsonl` instead of printing |
| `--overwrite` | off | Replace the export file if it exists |

## `gross` (`g`)

```text
sytax gross SALARY [COMPENSATION] [-i AMOUNT] [output options]
```

| Argument / option | Default | Meaning |
|-------------------|---------|---------|
| `SALARY` | required | Gross salary |
| `COMPENSATION` | `0` | Gross compensations |
| `-i, --insured-salary` | the gross salary | Salary social security is based on; turns social security on |

## `net` (`n`)

```text
sytax net TARGET [-r SHARE] [output options]
```

| Argument / option | Default | Meaning |
|-------------------|---------|---------|
| `TARGET` | required | Wanted net total |
| `-r, --compensations-rate` | `net.compensation_share` | Share of the net paid as compensation, 0 to 1 |

## `range` (`r`, `ar`)

```text
sytax range START [STOP] [STEP] [-r SHARE] [output options]
```

| Argument / option | Default | Meaning |
|-------------------|---------|---------|
| `START` | required | First net total |
| `STOP` | START × `range.stop_factor` | Last net total, inclusive |
| `STEP` | START ÷ `range.step_divisor` | Gap between net totals |
| `-r, --compensations-rate` | `net.compensation_share` | Share of each net paid as compensation |

At most `range.max_size` rows.

## `rules`

```text
sytax rules [-o table|json]
```

The tax rules in use, after every config layer. JSON is indented by `output.json_indent`.

## `config` (`cfg`)

| Command | Alias | Options | Does |
|---------|-------|---------|------|
| `config show` | `s` | `-o table\|json\|toml`, `--sources` | The settings in use; `--sources` adds who set each one |
| `config path` | `p` | | Where config files are looked for, and which were found |
| `config init` | | `--user` / `--project` (default), `--preset NAME`, `--force` | Write a config file with every preset value commented out |
| `config presets` | | | The bundled presets, and the default |

## Amounts and rates

- Amounts: `1000000`, `1,000,000`, `1_000_000` or `1e6`. Negative amounts are refused.
- Rates: fractions, `0.25` for 25%.
