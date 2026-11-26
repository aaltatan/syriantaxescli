# Environment variables

`SYRIANTAXES_*` variables override the config files, and are overridden by options and
`-s`. A `.env` file in the current folder is read as well; variables set in the shell
win over it.

| Variable | Setting | Example |
|----------|---------|---------|
| `SYRIANTAXES_PRESET` | `preset` | `syria-2024` |
| `SYRIANTAXES_CONFIG` | an extra config file, like `--config` | `/srv/payroll/company.toml` |
| `SYRIANTAXES_CONFIG_HOME` | the folder of the user `config.toml` | `C:\payroll\config` |
| `SYRIANTAXES_BRACKET_TAX_MINS` | `tax.brackets[].lower`, separated by spaces | `0 837000 850000 1100000` |
| `SYRIANTAXES_BRACKET_TAX_RATES` | `tax.brackets[].rate`, separated by spaces | `0 0.11 0.13 0.15` |
| `SYRIANTAXES_MIN_ALLOWED_SALARY` | `tax.min_salary` | `837000` |
| `SYRIANTAXES_FIXED_TAX_RATE` | `tax.compensation_tax_rate` | `0.05` |
| `SYRIANTAXES_TAXES_ROUNDING_METHOD` | `tax.rounding.method` | `half_up` |
| `SYRIANTAXES_TAXES_ROUND_TO_NEAREST` | `tax.rounding.step` | `100` |
| `SYRIANTAXES_SS_ENABLED` | `tax.social_security.enabled` | `true` |
| `SYRIANTAXES_SS_DEDUCTION_RATE` | `tax.social_security.rate` | `0.07` |
| `SYRIANTAXES_MIN_SS_ALLOWED_SALARY` | `tax.social_security.min_salary` | `750000` |
| `SYRIANTAXES_SS_ROUNDING_METHOD` | `tax.social_security.rounding.method` | `half_up` |
| `SYRIANTAXES_SS_ROUND_TO_NEAREST` | `tax.social_security.rounding.step` | `1` |

- Set **both** bracket variables, or neither, with the same number of values.
- An empty variable is ignored.
- `net`, `output` and `range` settings have no variables: set them in a config file or
  with `-s`.

## `.env`

```text
# .env, in the folder sytax runs from
SYRIANTAXES_SS_ENABLED=true
SYRIANTAXES_MIN_ALLOWED_SALARY=900000
```

`sytax config path` shows the `.env` it looks for, and `sytax config show --sources`
shows the values that came from environment variables as `environment variables`.
