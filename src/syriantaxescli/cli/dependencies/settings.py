from typing import Annotated

import typer
from typer_di import Depends

from syriantaxescli.core.config import ConfigError, LoadedSettings
from syriantaxescli.core.settings import Settings

from .ctx import ContextDI


def _get_loaded(context: ContextDI) -> LoadedSettings:
    try:
        return context.load()
    except ConfigError as e:
        raise typer.BadParameter(str(e), param_hint="configuration") from e


LoadedDI = Annotated[LoadedSettings, Depends(_get_loaded)]


def _get_settings(loaded: LoadedDI) -> Settings:
    return loaded.settings


SettingsDI = Annotated[Settings, Depends(_get_settings)]
