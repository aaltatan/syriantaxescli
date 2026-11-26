# Errors and exit codes

| Exit | Meaning |
|------|---------|
| `0` | Done |
| `2` | Bad input: an argument, an option, a setting or a config file |

Errors are a short message in a red panel, never a Python traceback, and nothing is
exported when a command fails.

## Amounts and arguments

| Message | Fix |
|---------|-----|
| `Invalid value for 'salary': 'abc' is not a valid number.` | Write amounts as `1000000`, `1,000,000`, `1_000_000` or `1e6` |
| `Invalid value for 'salary': '-5' must not be negative.` | Amounts are 0 or more |
| `Invalid value for 'TARGET': Can't be calculated for salary less than 837000.` | A net target must be at least `tax.min_salary` |
| `Invalid value: compensation_share must be between 0 and 1, got 1.5` | `-r` is a fraction: `0.25` for 25% |
| `Invalid value: stop (900000) must not be less than start (1000000)` | `range START STOP`: STOP ≥ START |
| `Invalid value: the range has 999,000,001 amounts but at most 1,000 are allowed; use a bigger step or a smaller range` | A bigger STEP, or raise `range.max_size` |

## Output

| Message | Fix |
|---------|-----|
| `Invalid value for '-e' / '--export': Can't export to '.txt' files; use one of: .xlsx, .csv, .json, .jsonl` | Use a supported extension |
| `Invalid value for '-e' / '--export': The file '...' already exists; pass --overwrite to replace it.` | `--overwrite`, or another name |
| `No such option: --json-indent` (on `rules`) | `rules` uses `output.json_indent`: `-s output.json_indent=0` |

## Rules and settings

| Message | Fix |
|---------|-----|
| `Invalid value for '--brackets-mins' / '--brackets-rates': got 2 bracket lower bound(s) but 1 rate(s); every bracket needs both` | Give as many rates as lower bounds |
| `Invalid value for configuration: set both SYRIANTAXES_BRACKET_TAX_MINS and SYRIANTAXES_BRACKET_TAX_RATES, or neither` | Set both variables |
| `Invalid value for '--taxes-rounding-method': Value error, 'ceiling' is not one of 'round_ceiling', ...` | The option needs the `ROUND_` name: `round_ceiling` |
| `Invalid value for configuration: unknown preset 'nope'; available: syria-2024` | `sytax config presets` lists them |
| `Invalid value for configuration: invalid settings: tax.nope: unknown setting; ...` | Check the key: `sytax config show` lists them |
| `... tax.compensation_tax_rate: Input should be less than 1 (from --set tax.compensation_tax_rate=1)` | Rates are fractions below 1; the message names the layer |

## Config files

| Message | Fix |
|---------|-----|
| `Invalid value: ...\sytax.toml already exists; pass --force to replace it.` | `config init --force`, or edit the file |
| `Invalid value for '--config': file 'nope.toml' does not exist.` | Check the path |

A settings error names the layer it came from (a file path, `environment variables`,
`--set ...`), so you know which one to fix. `sytax config show --sources` shows every
layer's values.
