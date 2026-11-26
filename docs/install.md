# Installation

sytax needs **Python 3.12 or newer**. Install it as a tool:

=== "uv"

    ```text
    uv tool install syriantaxescli
    ```

=== "pipx"

    ```text
    pipx install syriantaxescli
    ```

=== "pip"

    ```text
    pip install syriantaxescli
    ```

The package is called `syriantaxescli`, and the command it installs is `sytax`.

```text
$ sytax --version
sytax 0.2.1
```

## Shell completion

```text
sytax --install-completion
```

Restart the shell after installing it.

## Upgrade and uninstall

=== "uv"

    ```text
    uv tool upgrade syriantaxescli
    uv tool uninstall syriantaxescli
    ```

=== "pipx"

    ```text
    pipx upgrade syriantaxescli
    pipx uninstall syriantaxescli
    ```

Upgrading from 0.1? Some options moved: see [Upgrading from 0.1](reference/upgrading.md).

## Nothing to configure

The tax rules come from the bundled preset `syria-2024`, so `sytax gross 1000000` works
right after installing. When something differs for you, see
[Configuration](guide/configuration.md).

## The example files

The config files used in this documentation are in the
[`examples/`](https://github.com/aaltatan/syriantaxescli/tree/main/examples) folder:

| File | What it sets |
|------|--------------|
| `company.toml` | A quarter of the net as compensations; JSON indented by 2 |
| `social-security.toml` | Social security on |
| `draft-law.toml` | A made-up draft law: a higher minimum salary and new brackets |

```text
git clone https://github.com/aaltatan/syriantaxescli
cd syriantaxescli/examples
```

Every command shown with its output in this documentation is run by the test suite, and
the output is checked.
