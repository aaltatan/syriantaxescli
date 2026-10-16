"""Load settings from layers, each overriding the one before it.

    preset -> user config.toml -> project sytax.toml -> --config file
    -> .env and SYRIANTAXES_* environment variables -> command-line options -> --set

A preset holds every value; the other layers hold only what they change.
"""

import json
import tomllib
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from importlib.resources import files
from pathlib import Path
from typing import Any, Final

from dotenv import dotenv_values
from pydantic import ValidationError

from .settings import Settings

type Layer = dict[str, Any]
type KeyPath = tuple[str | int, ...]

PRESETS_PACKAGE: Final = "syriantaxescli.presets"
USER_FILE: Final = "config.toml"
PROJECT_FILE: Final = "sytax.toml"
DOTENV_FILE: Final = ".env"
ENV_PREFIX: Final = "SYRIANTAXES_"
CONFIG_ENV: Final = "SYRIANTAXES_CONFIG"
CONFIG_HOME_ENV: Final = "SYRIANTAXES_CONFIG_HOME"

BRACKET_LOWERS_ENV: Final = "SYRIANTAXES_BRACKET_TAX_MINS"
BRACKET_RATES_ENV: Final = "SYRIANTAXES_BRACKET_TAX_RATES"

# Environment variables and the setting each one sets.
ENV_VARS: Final[Mapping[str, tuple[str, ...]]] = {
    "SYRIANTAXES_PRESET": ("preset",),
    "SYRIANTAXES_MIN_ALLOWED_SALARY": ("tax", "min_salary"),
    "SYRIANTAXES_FIXED_TAX_RATE": ("tax", "compensation_tax_rate"),
    "SYRIANTAXES_TAXES_ROUNDING_METHOD": ("tax", "rounding", "method"),
    "SYRIANTAXES_TAXES_ROUND_TO_NEAREST": ("tax", "rounding", "step"),
    "SYRIANTAXES_SS_ENABLED": ("tax", "social_security", "enabled"),
    "SYRIANTAXES_SS_DEDUCTION_RATE": ("tax", "social_security", "rate"),
    "SYRIANTAXES_MIN_SS_ALLOWED_SALARY": ("tax", "social_security", "min_salary"),
    "SYRIANTAXES_SS_ROUNDING_METHOD": ("tax", "social_security", "rounding", "method"),
    "SYRIANTAXES_SS_ROUND_TO_NEAREST": ("tax", "social_security", "rounding", "step"),
}


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class Source:
    name: str
    data: Layer


@dataclass(frozen=True)
class ConfigFiles:
    user: Path
    project: Path | None
    extra: Path | None
    dotenv: Path


@dataclass(frozen=True)
class LoadedSettings:
    settings: Settings
    sources: tuple[Source, ...]

    def origin(self, path: KeyPath) -> str:
        """Return the name of the last layer that set `path`."""
        return _origin(self.sources, path) or "default"


# --------------------
# Presets
# --------------------


def list_presets() -> list[str]:
    return sorted(
        entry.name.removesuffix(".toml")
        for entry in files(PRESETS_PACKAGE).iterdir()
        if entry.name.endswith(".toml")
    )


def default_preset() -> str:
    """Return the newest preset; preset names sort by date."""
    return list_presets()[-1]


def load_preset(name: str) -> Layer:
    if name not in list_presets():
        message = f"unknown preset {name!r}; available: {', '.join(list_presets())}"
        raise ConfigError(message)

    return tomllib.loads((files(PRESETS_PACKAGE) / f"{name}.toml").read_text(encoding="utf-8"))


def preset_settings(name: str | None = None) -> Settings:
    """Return a preset's settings with no overrides."""
    name = name or default_preset()
    return Settings.model_validate({**load_preset(name), "preset": name})


# --------------------
# Layers
# --------------------


def find_project_file(cwd: Path) -> Path | None:
    """Return the nearest `sytax.toml` in `cwd` or any folder above it."""
    return next(
        (
            folder / PROJECT_FILE
            for folder in (cwd, *cwd.parents)
            if (folder / PROJECT_FILE).is_file()
        ),
        None,
    )


def config_files(
    *, cwd: Path, user_dir: Path, environ: Mapping[str, str], config_path: Path | None = None
) -> ConfigFiles:
    extra = config_path or (Path(environ[CONFIG_ENV]) if environ.get(CONFIG_ENV) else None)
    return ConfigFiles(
        user=user_dir / USER_FILE,
        project=find_project_file(cwd),
        extra=extra,
        dotenv=cwd / DOTENV_FILE,
    )


def read_toml(path: Path) -> Layer:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except OSError as e:
        message = f"can't read {path}: {e.strerror}"
        raise ConfigError(message) from e
    except tomllib.TOMLDecodeError as e:
        message = f"{path} is not valid TOML: {e}"
        raise ConfigError(message) from e


def brackets_layer(lowers: Sequence[object], rates: Sequence[object]) -> list[Layer]:
    if len(lowers) != len(rates):
        message = (
            f"got {len(lowers)} bracket lower bound(s) but {len(rates)} rate(s); "
            "every bracket needs both"
        )
        raise ConfigError(message)

    return [{"lower": lower, "rate": rate} for lower, rate in zip(lowers, rates, strict=True)]


def env_layer(environ: Mapping[str, str]) -> Layer:
    """Turn SYRIANTAXES_* environment variables into a layer."""
    layer: Layer = {}

    for name, path in ENV_VARS.items():
        if environ.get(name):
            set_path(layer, path, environ[name])

    lowers, rates = environ.get(BRACKET_LOWERS_ENV), environ.get(BRACKET_RATES_ENV)
    if lowers or rates:
        if not (lowers and rates):
            message = f"set both {BRACKET_LOWERS_ENV} and {BRACKET_RATES_ENV}, or neither"
            raise ConfigError(message)
        set_path(layer, ("tax", "brackets"), brackets_layer(lowers.split(), rates.split()))

    return layer


def parse_set(item: str) -> Layer:
    """Turn `tax.min_salary=900000` into `{"tax": {"min_salary": 900000}}`.

    The value is read as a TOML value (`900000`, `0.05`, `true`, `"text"`, `[...]`,
    `{...}`); anything else is kept as text, so `output.format=json` works.
    """
    key, sep, text = item.partition("=")
    path = tuple(part.strip() for part in key.split("."))

    if not sep or not all(path):
        message = f"--set {item!r} must look like KEY=VALUE, e.g. tax.min_salary=900000"
        raise ConfigError(message)

    try:
        value = tomllib.loads(f"value = {text.strip()}")["value"]
    except tomllib.TOMLDecodeError:
        value = text.strip()

    layer: Layer = {}
    set_path(layer, path, value)
    return layer


def set_path(layer: Layer, path: Sequence[str], value: object) -> None:
    node = layer
    for key in path[:-1]:
        node = node.setdefault(key, {})
    node[path[-1]] = value


def merge(base: Layer, override: Layer) -> Layer:
    """Merge `override` into `base`: tables merge key by key, anything else is replaced."""
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = merge(merged[key], dict(value))
        else:
            merged[key] = value
    return merged


def _origin(sources: Sequence[Source], path: KeyPath) -> str | None:
    return next((source.name for source in reversed(sources) if _has(source.data, path)), None)


def _has(data: Layer, path: KeyPath) -> bool:
    node: object = data
    for key in path:
        if not isinstance(key, str):
            return True  # inside a list: whoever set the list set this
        if not isinstance(node, Mapping) or key not in node:
            return False
        node = node[key]
    return True


# --------------------
# Loading
# --------------------


def load_settings(  # noqa: PLR0913
    *,
    cwd: Path,
    user_dir: Path,
    environ: Mapping[str, str],
    config_path: Path | None = None,
    cli_layer: Layer | None = None,
    set_items: Iterable[str] = (),
) -> LoadedSettings:
    """Load the settings, layer by layer. See the module docstring for the order.

    Raises:
        ConfigError: If a file can't be read, or a value is missing or invalid.

    """
    dotenv_file = cwd / DOTENV_FILE
    dotenv = dotenv_values(dotenv_file) if dotenv_file.is_file() else {}
    env = {
        **{key: value for key, value in dotenv.items() if value is not None},
        **{key: value for key, value in environ.items() if key.startswith(ENV_PREFIX)},
    }
    paths = config_files(cwd=cwd, user_dir=user_dir, environ=env, config_path=config_path)

    sources: list[Source] = []

    if paths.user.is_file():
        sources.append(Source(str(paths.user), read_toml(paths.user)))
    if paths.project is not None:
        sources.append(Source(str(paths.project), read_toml(paths.project)))
    if paths.extra is not None:
        sources.append(Source(str(paths.extra), read_toml(paths.extra)))
    if layer := env_layer(env):
        sources.append(Source("environment variables", layer))
    if cli_layer:
        sources.append(Source("command-line options", cli_layer))
    sources.extend(Source(f"--set {item}", parse_set(item)) for item in set_items)

    preset = next(
        (source.data["preset"] for source in reversed(sources) if "preset" in source.data),
        default_preset(),
    )
    if not isinstance(preset, str):
        message = f"preset must be a name, got {preset!r}"
        raise ConfigError(message)

    sources.insert(0, Source(f"preset {preset}", load_preset(preset)))
    data: Layer = {}
    for source in sources:
        data = merge(data, source.data)
    data["preset"] = preset

    try:
        settings = Settings.model_validate(data)
    except ValidationError as e:
        raise ConfigError(_describe(e, sources)) from e

    return LoadedSettings(settings, tuple(sources))


def _describe(error: ValidationError, sources: Sequence[Source]) -> str:
    lines = ["invalid settings:"]
    for item in error.errors():
        path = tuple(item["loc"])
        origin = _origin(sources, path)
        where = f" (from {origin})" if origin else ""
        key = ".".join(str(part) for part in path)
        message = (
            "unknown setting; `sytax config show` lists them"
            if item["type"] == "extra_forbidden"
            else item["msg"]
        )
        lines.append(f"  {key}: {message}{where}")
    return "\n".join(lines)


# --------------------
# TOML output
# --------------------


def dump_toml(data: Mapping[str, Any]) -> str:
    """Write settings as TOML: tables, arrays of tables and plain values only."""
    lines: list[str] = []
    _dump_table(lines, (), data)
    return "\n".join(lines).strip() + "\n"


def _dump_table(lines: list[str], prefix: tuple[str, ...], table: Mapping[str, Any]) -> None:
    for key, value in table.items():
        if not isinstance(value, Mapping) and not _is_table_array(value):
            lines.append(f"{key} = {_toml_value(value)}")

    for key, value in table.items():
        name = ".".join((*prefix, key))
        if isinstance(value, Mapping):
            lines.extend(("", f"[{name}]"))
            _dump_table(lines, (*prefix, key), value)
        elif _is_table_array(value):
            for item in value:
                lines.extend(("", f"[[{name}]]"))
                _dump_table(lines, (*prefix, key), item)


def _is_table_array(value: object) -> bool:
    return (
        isinstance(value, list | tuple)
        and bool(value)
        and all(isinstance(item, Mapping) for item in value)
    )


def _toml_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, Enum):
        return json.dumps(value.value)
    if isinstance(value, int | float | Decimal):
        return str(value)
    if isinstance(value, list | tuple):
        return "[" + ", ".join(_toml_value(item) for item in value) + "]"
    return json.dumps(str(value))
