# Settings

Every setting, by its dotted key, with its value in the preset `syria-2024`. Set any of
them in a config file, or with `-s KEY=VALUE`; the tax rules also have an option and an
environment variable.

| Key | Preset value | Allowed | Option | Environment variable |
|-----|--------------|---------|--------|----------------------|
| `preset` | `syria-2024` (the newest) | a preset name | `--preset` | `SYRIANTAXES_PRESET` |
| `tax.min_salary` | `837000` | amount ≥ 0 | `--min-allowed-salary` | `SYRIANTAXES_MIN_ALLOWED_SALARY` |
| `tax.compensation_tax_rate` | `0.05` | rate, 0 ≤ r < 1 | `--fixed-tax-rate` | `SYRIANTAXES_FIXED_TAX_RATE` |
| `tax.brackets` | 4 brackets, see below | list of `{lower, rate}` | `--brackets-mins`, `--brackets-rates` | `SYRIANTAXES_BRACKET_TAX_MINS`, `SYRIANTAXES_BRACKET_TAX_RATES` |
| `tax.rounding.method` | `HALF_UP` | a [rounding method](#rounding-methods) | `--taxes-rounding-method` | `SYRIANTAXES_TAXES_ROUNDING_METHOD` |
| `tax.rounding.step` | `100` | number > 0 | `--taxes-round-to-nearest` | `SYRIANTAXES_TAXES_ROUND_TO_NEAREST` |
| `tax.social_security.enabled` | `false` | `true` / `false` | `--ss` / `--no-ss` | `SYRIANTAXES_SS_ENABLED` |
| `tax.social_security.rate` | `0.07` | rate, 0 ≤ r < 1 | `--ss-deduction-rate` | `SYRIANTAXES_SS_DEDUCTION_RATE` |
| `tax.social_security.min_salary` | `750000` | amount ≥ 0 | `--min-ss-allowed-salary` | `SYRIANTAXES_MIN_SS_ALLOWED_SALARY` |
| `tax.social_security.rounding.method` | `HALF_UP` | a rounding method | `--ss-rounding-method` | `SYRIANTAXES_SS_ROUNDING_METHOD` |
| `tax.social_security.rounding.step` | `1` | number > 0 | `--ss-round-to-nearest` | `SYRIANTAXES_SS_ROUND_TO_NEAREST` |
| `net.compensation_share` | `0` | share, 0 ≤ s ≤ 1 | `-r` (per command) | |
| `output.format` | `table` | `table` / `json` | `-o` (per command) | |
| `output.json_indent` | `4` | integer ≥ 0; `0` is one line | `--json-indent` (per command) | |
| `range.max_size` | `1000` | integer > 0 | | |
| `range.stop_factor` | `10` | number > 0 | | |
| `range.step_divisor` | `10` | number > 0 | | |

## Brackets

```toml
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
```

Each bracket runs from its `lower` to the next one's; the last has no top. A config file
that sets `tax.brackets` replaces the whole list.

## Rounding methods

The modes of Python's `decimal` module:

| Method | Rounds |
|--------|--------|
| `HALF_UP` | to the nearest; halves away from zero |
| `HALF_EVEN` | to the nearest; halves to the even step |
| `HALF_DOWN` | to the nearest; halves towards zero |
| `UP` | away from zero |
| `DOWN` | towards zero |
| `CEILING` | up |
| `FLOOR` | down |
| `05UP` | away from zero if the last digit is 0 or 5 |

In config files, `-s` and environment variables, write them in any case, with or
without `ROUND_`. The `--taxes-rounding-method` and `--ss-rounding-method` options need
the `ROUND_` names: `--taxes-rounding-method round_ceiling`.

## Amounts

Amounts and numbers can be written as `1000000`, `1_000_000`, `"1,000,000"` or `1e6`, in
files, `-s` and environment variables alike.
