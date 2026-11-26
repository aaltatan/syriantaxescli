# User guide

| Page | You will learn |
|------|----------------|
| [Gross to net](gross.md) | `gross`: taxes and net of a salary and compensations, with social security |
| [Net to gross](net.md) | `net`: the gross that pays a wanted net |
| [Salary scales](range.md) | `range`: the gross for a whole range of nets |
| [Output and export](output.md) | Tables, JSON, `.xlsx`, `.csv`, `.json`, `.jsonl` |
| [The tax rules](rules.md) | `rules`: the brackets, rates and rounding in use |
| [Configuration](configuration.md) | Config files, environment variables and options, and which wins |
| [Presets and law changes](presets.md) | What a preset is, and what to do when the law changes |

## The commands

| Command | Aliases | Does |
|---------|---------|------|
| `gross` | `g` | Taxes and net of a gross salary and (optional) compensations |
| `net` | `n` | Gross salary and compensations for a wanted net total |
| `range` | `r`, `ar` | A salary scale for net totals from START to STOP every STEP |
| `rules` | | The tax rules in use, after config files, environment variables and options |
| `config` | `cfg` | `show`, `path`, `init`, `presets` |

```text
sytax [GLOBAL OPTIONS] COMMAND [ARGS] [OPTIONS]
```

**Global options** (the tax rules, the preset, `--config`, `-s`) go **before** the
command: `sytax --ss gross 1000000`. Output options (`-o`, `-e`) go after it.

## Writing amounts

Amounts can be written in any of these ways:

| Written | Means |
|---------|-------|
| `1000000` | one million |
| `1,000,000` | one million |
| `1_000_000` | one million |
| `1e6` | one million |

```bash
sytax gross 1,000,000
sytax gross 1e6
```

Rates are fractions: `0.25` is 25%.

## The words

| Word | Means |
|------|-------|
| **Salary** | The basic salary (الراتب المقطوع), taxed by brackets |
| **Compensations** | Allowances paid on top of the salary (التعويضات), taxed at a flat rate |
| **Total** | Salary + compensations: the gross |
| **Social security** | The employee's share of social insurance (التأمينات الاجتماعية), deducted from the salary before the tax |
| **Deductions** | Social security + taxes |
| **Net** | Total − deductions: what the employee receives |
| **Compensation ratio** | Compensations ÷ total |
