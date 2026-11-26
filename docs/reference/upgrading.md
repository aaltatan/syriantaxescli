# Upgrading from 0.1

| 0.1 | 0.2 |
|-----|-----|
| `--brackets-maxs` and `SYRIANTAXES_BRACKET_TAX_MAXS` | Gone: syriantaxes 1.0 defines brackets by their lower bounds only, and the last bracket has no top |
| `gross SALARY COMPENSATION INSURED` | `gross SALARY COMPENSATION -i INSURED` (`--insured-salary`) |
| `-r/--compensations-rate` defaults to a fixed value | It defaults to the setting `net.compensation_share` (0 in the preset) |
| `ar` | `range`; `ar` still works as an alias |
| Tax-rule options after the command | Global: before the command, `sytax --ss gross 1e6`. The environment variable names are unchanged. |
| `rules` has a `config` alias | Removed: `config` is now the configuration command group |
| `--write-path` | `-e/--export` (the old name still works), and every command can export |
| JSON lines files | One compact object per line |

New in 0.2: presets, config files (`sytax.toml`, the user `config.toml`, `--config`),
`-s/--set`, `config show/path/init/presets`, and `.env` files. See
[Configuration](../guide/configuration.md).
