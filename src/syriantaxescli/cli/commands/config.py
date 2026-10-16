import json
from collections.abc import Iterator, Mapping
from decimal import Decimal
from enum import Enum, StrEnum
from typing import TYPE_CHECKING, Annotated, Any

import typer
from rich.table import Table
from typer_di import TyperDI
from typer_swissknife import command

from syriantaxescli.cli.dependencies.ctx import ContextDI
from syriantaxescli.cli.dependencies.settings import LoadedDI
from syriantaxescli.cli.serializers import to_json_number
from syriantaxescli.core.config import (
    PROJECT_FILE,
    USER_FILE,
    KeyPath,
    LoadedSettings,
    config_files,
    default_preset,
    dump_toml,
    list_presets,
    preset_settings,
)

if TYPE_CHECKING:
    from pathlib import Path

app = TyperDI(help="Show, find and create configuration files.")


class ConfigFormat(StrEnum):
    TABLE = "table"
    JSON = "json"
    TOML = "toml"


def _settings_data(loaded: LoadedSettings) -> dict[str, Any]:
    return loaded.settings.model_dump(mode="python")


def _jsonable(value: object) -> object:
    if isinstance(value, Decimal):
        return to_json_number(value)
    raise TypeError(repr(value))  # pragma: no cover - settings hold no other types


def _flatten(data: Mapping[str, Any], prefix: KeyPath = ()) -> Iterator[tuple[KeyPath, Any]]:
    for key, value in data.items():
        path = (*prefix, key)
        if isinstance(value, Mapping):
            yield from _flatten(value, path)
        else:
            yield path, value


def _format_value(value: object) -> str:
    if isinstance(value, tuple | list):
        return ", ".join(f"{item['lower']} @ {item['rate']}" for item in value)
    if isinstance(value, Enum):
        return str(value.value)
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


@command(app, name="show", aliases=("s",))
def show_cmd(
    ctx: ContextDI,
    loaded: LoadedDI,
    output: Annotated[
        ConfigFormat, typer.Option("-o", "--output", case_sensitive=False)
    ] = ConfigFormat.TABLE,
    sources: Annotated[
        bool, typer.Option("--sources", help="Show which layer set each value.")
    ] = False,
) -> None:
    """Show the settings in use, after every config layer is applied."""
    data = _settings_data(loaded)
    rows = [
        (".".join(map(str, path)), value, loaded.origin(path)) for path, value in _flatten(data)
    ]

    if output is ConfigFormat.TOML:
        ctx.echo(dump_toml(data))
    elif output is ConfigFormat.JSON:
        payload: dict[str, Any] = {"settings": data}
        if sources:
            payload["sources"] = {key: source for key, _, source in rows}
        ctx.echo(json.dumps(payload if sources else data, indent=4, default=_jsonable))
    else:
        table = Table(title="Settings")
        table.add_column("Key")
        table.add_column("Value", style="cyan")
        if sources:
            table.add_column("Source", style="dim", overflow="fold")
        for key, value, source in rows:
            table.add_row(key, _format_value(value), *((source,) if sources else ()))
        ctx.print(table)


@command(app, name="path", aliases=("p",))
def path_cmd(ctx: ContextDI) -> None:
    """Show where config files are looked for, lowest precedence first."""
    location = ctx.location
    files = config_files(
        cwd=location.cwd,
        user_dir=location.user_dir,
        environ=location.environ,
        config_path=location.config_path,
    )
    rows: list[tuple[str, Path | None, str]] = [
        ("user", files.user, ""),
        ("project", files.project, f"no {PROJECT_FILE} in {location.cwd} or above"),
        ("--config", files.extra, "not given"),
        (".env", files.dotenv, ""),
    ]

    table = Table(title="Config files")
    table.add_column("Layer")
    table.add_column("Path", overflow="fold")
    table.add_column("Found", justify="center")
    for layer, file, missing in rows:
        found = file is not None and file.is_file()
        table.add_row(layer, str(file) if file else missing, "yes" if found else "no")
    ctx.print(table)


def _comment_out(line: str) -> str:
    """Comment out values, but keep `[table]` headers so uncommented keys land in them.

    `[[array]]` headers stay commented: an uncommented one would add an empty bracket.
    """
    if not line or (line.startswith("[") and not line.startswith("[[")):
        return line
    return f"# {line}"


@command(app, name="init")
def init_cmd(
    ctx: ContextDI,
    user: Annotated[
        bool,
        typer.Option(
            "--user/--project",
            help=f"Write the user-wide {USER_FILE}, or the project {PROJECT_FILE} here.",
        ),
    ] = False,
    preset: Annotated[
        str | None, typer.Option("--preset", help="Preset the file starts from.")
    ] = None,
    force: Annotated[bool, typer.Option("--force", help="Replace an existing file.")] = False,
) -> None:
    """Create a config file that holds only what you change; the rest comes from the preset."""
    name = preset or default_preset()
    if name not in list_presets():
        message = f"unknown preset {name!r}; available: {', '.join(list_presets())}"
        raise typer.BadParameter(message, param_hint="'--preset'")

    location = ctx.location
    target = location.user_dir / USER_FILE if user else location.cwd / PROJECT_FILE

    if target.exists() and not force:
        message = f"{target} already exists; pass --force to replace it."
        raise typer.BadParameter(message)

    reference = {
        key: value
        for key, value in preset_settings(name).model_dump(mode="python").items()
        if key != "preset"
    }
    commented = "\n".join(_comment_out(line) for line in dump_toml(reference).splitlines())

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "# sytax configuration.\n"
        f"# Everything comes from the {name!r} preset; uncomment and change only what\n"
        "# differs. `sytax config show --sources` shows where each value comes from.\n"
        "\n"
        f"preset = {json.dumps(name)}\n"
        "\n"
        f"{commented}\n",
        encoding="utf-8",
    )
    ctx.print(f"[green]Created {target}[/]")


@command(app, name="presets")
def presets_cmd(ctx: ContextDI) -> None:
    """List the built-in tax law presets."""
    default = default_preset()
    table = Table(title="Presets")
    table.add_column("Name")
    table.add_column("Default", justify="center")
    for name in list_presets():
        table.add_row(name, "yes" if name == default else "")
    ctx.print(table)
