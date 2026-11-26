# Development

```text
git clone https://github.com/aaltatan/syriantaxescli
cd syriantaxescli
uv sync
uv run pytest        # with branch coverage; fails below 100%
uv run mypy
uv run ruff check
uv run ruff format --check
```

The calculations come from the [syriantaxes](https://pypi.org/project/syriantaxes/)
library; sytax adds the configuration layers, the commands and the output.

## Project structure

```text
src/syriantaxescli/
├── main.py                 # builds the Typer app; the `sytax` entry point
├── core/                   # calculations, independent of the CLI
│   ├── config.py           # layered config loading: presets, files, env, options
│   ├── settings.py         # the settings model (pydantic), with no defaults in code
│   ├── rounding.py         # rounding methods and rules
│   ├── salary.py           # the Salary result
│   └── services.py         # gross / net / range calculations on syriantaxes
├── presets/                # bundled law presets (TOML): the only defaults
└── cli/
    ├── callback.py         # root callback: --version, global options, lazy settings
    ├── commands/           # one Typer app per command: gross, net, range, rules, config
    ├── dependencies/       # typer-di dependencies: context, settings, overrides, output
    ├── options.py          # shared options
    ├── parsers.py          # Decimal parsing
    ├── renderers.py        # tables and JSON
    └── exporters.py        # .xlsx, .csv, .json, .jsonl
examples/                   # config files used by the docs
tests/
└── test_docs.py            # runs every command in the docs and checks its output
```

## Adding a preset

See [Presets and law changes](guide/presets.md#in-sytax-a-new-preset). A test checks
that every preset is complete, and `tests/test_docs.py` checks that the preset shown in
the docs is the bundled one.

## Documentation

This site is built with [MkDocs](https://www.mkdocs.org) and
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/). The pages are in
`docs/`, and the navigation in `mkdocs.yml`.

```text
uv run --group docs mkdocs serve          # live preview on http://127.0.0.1:8000
uv run --group docs mkdocs build --strict # what CI runs: broken links fail the build
```

Every push to `main` builds the site and publishes it to GitHub Pages
(`.github/workflows/docs.yml`).

### Outputs in the docs are tested

`tests/test_docs.py` runs the commands of the docs from a copy of `examples/`, with the
user config and `SYRIANTAXES_*` variables kept out:

- in ` ```console ` blocks, each `$ sytax ...` line runs, and every line shown under it
  must be in the real output, in order. A line with `...` stands for any lines, so a
  page can show only the rows that matter;
- in ` ```bash ` blocks, every `sytax ...` line must succeed.

Commands that need a shell (pipes, loops, environment variables) go in ` ```text ` or
` ```powershell ` blocks, which are not run.

## Releasing

Push a `v*` tag. The release workflow builds the package, publishes it to PyPI with
trusted publishing, and creates a GitHub release.
