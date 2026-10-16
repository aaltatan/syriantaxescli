import os
from functools import cache
from importlib.metadata import version
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from syriantaxescli.core.config import CONFIG_HOME_ENV, LoadedSettings, load_settings, merge

from .dependencies.ctx import ConfigLocation
from .dependencies.overrides import CliLayerDI
from .options import ConfigPathOpt, PresetOpt, SetOpt

APP_NAME = "sytax"


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"sytax {version('syriantaxescli')}")
        raise typer.Exit


def user_config_dir() -> Path:
    """Where the user-wide config.toml lives; SYRIANTAXES_CONFIG_HOME overrides it."""
    return Path(os.environ.get(CONFIG_HOME_ENV) or typer.get_app_dir(APP_NAME))


def callback(
    ctx: typer.Context,
    cli_layer: CliLayerDI,
    _version: Annotated[
        bool,
        typer.Option(
            "-v",
            "--version",
            callback=_version_callback,
            is_eager=True,
            help="Show the version and exit.",
        ),
    ] = False,
    preset: PresetOpt = None,
    config_path: ConfigPathOpt = None,
    set_items: SetOpt = None,
) -> None:
    location = ConfigLocation(
        cwd=Path.cwd(),
        user_dir=user_config_dir(),
        environ=dict(os.environ),
        config_path=config_path,
    )
    layer = cli_layer if preset is None else merge(cli_layer, {"preset": preset})

    # Settings are loaded on first use, so a broken config file doesn't break --help.
    @cache
    def load() -> LoadedSettings:
        return load_settings(
            cwd=location.cwd,
            user_dir=location.user_dir,
            environ=location.environ,
            config_path=location.config_path,
            cli_layer=layer,
            set_items=set_items or (),
        )

    ctx.obj = {"console": Console(), "load": load, "location": location}
