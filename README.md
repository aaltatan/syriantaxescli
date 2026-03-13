# syriantaxescli

A command-line tool for calculating and analyzing Syrian salary taxes, built with [Typer](https://typer.tiangolo.com/) and leveraging the [syriantaxes](https://pypi.org/project/syriantaxes/) library.

## Features

- **Gross and Net Salary Calculations:** Compute taxes for a given gross salary or determine the required gross salary for a target net salary.
- **Batch Calculations:** Generate salary tables for a range of amounts.
- **Export Results:** Output results to Excel (`.xlsx`), JSON, or JSONL files.
- **Rich CLI Output:** Nicely formatted tables using [rich](https://rich.readthedocs.io/).

## Installation

```bash
pip install syriantaxescli
```

## Usage

After installation, use the CLI tool:

```bash
sytax [COMMAND] [OPTIONS]
```

### Commands

- `gross`: Calculate taxes for a given gross salary and compensations.
- `net`: Calculate gross salary and compensations for a given target net salary.
- `ar`: Generate salaries for a range of amounts (amount range).

### Options

- Bracket configuration: `--brackets-mins`, `--brackets-maxs`, `--brackets-rates`
- Compensation rate: `--compensations-rate`
- Fixed tax rate, minimum allowed salary, social security options, and more.
- Output file: `--write-path` (supports `.xlsx`, `.json`, `.jsonl`)

### Example

```bash
sytax gross --gross-salary 1000000 --compensations 100000
sytax net --target-salary 900000 --compensations-rate 0.1
sytax ar --start 800000 --stop 1200000 --step 50000 --compensations-rate 0.1 --write-path results.xlsx
```

## Project Structure

- `src/syriantaxescli/controllers.py`: CLI entry point and command definitions.
- `src/syriantaxescli/services.py`: Core tax calculation logic.
- `src/syriantaxescli/writers.py`: Export utilities for Excel, JSON, and JSONL.
- `src/syriantaxescli/tables.py`: Table formatting for CLI output.
- `src/syriantaxescli/schemas.py`: Data models for salary and tax results.
- `src/syriantaxescli/options.py`, `dependencies.py`, `constants.py`, `callbacks.py`: CLI options, validation, and configuration.

## Requirements

- Python 3.12+
- [syriantaxes](https://pypi.org/project/syriantaxes/)
- typer, typer-di, xlwings, rich

## License

GNU General Public License v3 (GPLv3)
