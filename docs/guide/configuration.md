# Configuration

**No value is hard-coded.** Every default (the brackets, the rates, the rounding, the
minimums, social security, the output format, the range limits, the default
compensation share) comes from a **preset**: a TOML file bundled with sytax that
describes one version of the law. Out of the box you configure nothing.

When something differs for you, override **only that value**, in the layer that fits.

## The layers

| Precedence | Layer | Use it for |
|------------|-------|------------|
| 1 (lowest) | the preset (`--preset`; default: the newest) | The law itself |
| 2 | the user file `config.toml` | Your company's settings, in every folder |
| 3 | the project file `sytax.toml` | One payroll folder; found from the current folder upward |
| 4 | `--config FILE` / `SYRIANTAXES_CONFIG` | A file shared by a team |
| 5 | `.env` and `SYRIANTAXES_*` environment variables | CI, scripts, containers |
| 6 | global options (`--ss`, `--fixed-tax-rate`, ...) | One-off overrides of the tax rules |
| 7 (highest) | `-s, --set KEY=VALUE` | Any setting, one-off |

- A higher layer wins over a lower one, **key by key**: a file that sets only
  `tax.min_salary` leaves every other setting to the layers below.
- **Lists are replaced as a whole**: a file that sets `tax.brackets` replaces every
  bracket, it does not add one.

## Config files

A config file holds **only what you change**.
[`examples/company.toml`](https://github.com/aaltatan/syriantaxescli/blob/main/examples/company.toml):

```toml
# A company's payroll settings: only what differs from the preset.
preset = "syria-2024"

[net]
# net and range pay a quarter of the net as compensations unless -r says otherwise
compensation_share = 0.25

[output]
json_indent = 2
```

```console
$ sytax --config company.toml net 1500000
             Net Salary
...
│ Compensation       │   394,700.00 │
...
│ Net                │ 1,500,029.00 │
│ Compensation Ratio │       25.24% │
└────────────────────┴──────────────┘
```

Where to put it:

=== "Project file"

    `sytax.toml` in the payroll folder, or any folder above it. Every `sytax` run from
    inside that folder uses it.

    ```bash
    sytax config init              # write ./sytax.toml
    ```

=== "User file"

    `config.toml` in your user config folder, used in every folder.

    ```text
    sytax config init --user       # write the user config.toml
    sytax config path              # where it is
    ```

    `SYRIANTAXES_CONFIG_HOME` moves that folder.

=== "Shared file"

    Any path, given with `--config` or `SYRIANTAXES_CONFIG`: a file a whole team keeps
    in a shared folder or a repository.

    ```bash
    sytax --config company.toml rules
    ```

### `config init`

`sytax config init` writes a starter file: the preset name, and **every** setting of the
preset commented out. Uncomment and change only what differs:

```toml
# sytax configuration.
# Everything comes from the 'syria-2024' preset; uncomment and change only what
# differs. `sytax config show --sources` shows where each value comes from.

preset = "syria-2024"

[tax]
# min_salary = 837000
# compensation_tax_rate = 0.05

# [[tax.brackets]]
# lower = 0
# rate = 0
...
```

An existing file is kept unless you pass `--force`. `--preset` picks another preset to
start from.

## Who set what: `config show`

`sytax config show` prints every setting in use, and `--sources` the layer that set
each one:

```console
$ sytax --config company.toml config show --sources
...
│ preset                              │ syria-2024                                          │ company.toml      │
│ tax.brackets                        │ 0 @ 0, 837000 @ 0.11, 850000 @ 0.13, 1100000 @ 0.15 │ preset syria-2024 │
│ tax.min_salary                      │ 837000                                              │ preset syria-2024 │
...
│ net.compensation_share              │ 0.25                                                │ company.toml      │
│ output.format                       │ table                                               │ preset syria-2024 │
│ output.json_indent                  │ 2                                                   │ company.toml      │
...
```

| Option | Prints |
|--------|--------|
| *(none)* | A table of every key and value |
| `--sources` | Adds the layer of each value |
| `-o json` | The settings as JSON; with `--sources`, `{"settings": ..., "sources": ...}` |
| `-o toml` | The settings as a complete config file |

`sytax config path` shows where each config file is looked for, and whether it was
found.

## Environment variables

Every tax rule has an environment variable, and a `.env` file in the current folder is
read too:

```text
# .env
SYRIANTAXES_SS_ENABLED=true
SYRIANTAXES_MIN_ALLOWED_SALARY=900000
```

=== "PowerShell"

    ```powershell
    $env:SYRIANTAXES_SS_ENABLED = "true"
    sytax gross 1000000
    ```

=== "bash"

    ```text
    SYRIANTAXES_SS_ENABLED=true sytax gross 1000000
    ```

Bracket lists are separated by spaces:
`SYRIANTAXES_BRACKET_TAX_MINS="0 1000000"`, `SYRIANTAXES_BRACKET_TAX_RATES="0 0.1"`.
The full list is in [Environment variables](../reference/environment.md).

## One-off: options and `-s`

Rule options and `-s` go **before** the command:

```bash
sytax --ss gross 1000000
sytax --fixed-tax-rate 0.04 net 1500000
sytax -s tax.min_salary=900000 -s output.format=json range 1000000
sytax --preset syria-2024 gross 1000000 100000
```

`-s KEY=VALUE` sets **any** setting by its dotted key, and is repeatable:

```console
$ sytax -s net.compensation_share=0.25 -s output.json_indent=0 net 1500000 -o json
{"salary": 1169329, "compensation": 394700, "total": 1564029, "social_security": 0, "salary_tax": 44300, "compensation_tax": 19700, "taxes": 64000, "deductions": 64000, "net": 1500029, "compensation_ratio": 0.2523610495713315}
```

Every key is listed in [Settings](../reference/settings.md). An unknown key is an error,
so a typo never passes silently:

```console
$ sytax -s tax.nope=1 gross 1
Invalid value for configuration: invalid settings:
tax.nope: unknown setting; `sytax config show` lists them (from --set tax.nope=1)
```

## Settings are checked

Every layer is checked when a command needs the settings: wrong types, unknown keys and
impossible values are reported with the layer they came from. A broken config file does
not stop `--help` from working.
