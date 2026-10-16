import json
import os
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

import pytest
from syriantaxes import TaxRules
from typer.testing import CliRunner, Result

from syriantaxescli.core.config import CONFIG_HOME_ENV, preset_settings
from syriantaxescli.main import app

Invoke = Callable[..., Result]
InvokeJSON = Callable[..., Any]


@pytest.fixture(autouse=True)
def _isolate_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Keep the developer's own settings out: env vars, user config and project files."""
    for name in list(os.environ):
        if name.startswith("SYRIANTAXES_"):
            monkeypatch.delenv(name)

    work = tmp_path / "work"
    home = tmp_path / "home"
    work.mkdir()
    home.mkdir()
    monkeypatch.chdir(work)
    monkeypatch.setenv(CONFIG_HOME_ENV, str(home))


@pytest.fixture
def work_dir() -> Path:
    """Return the current folder, where a project sytax.toml goes."""
    return Path.cwd()


@pytest.fixture
def user_dir() -> Path:
    """Return the folder where the user-wide config.toml goes."""
    return Path(os.environ[CONFIG_HOME_ENV])


@pytest.fixture
def rules() -> TaxRules:
    return preset_settings().tax.to_rules()


@pytest.fixture
def ss_rules() -> TaxRules:
    return preset_settings().tax.to_rules(social_security=True)


@pytest.fixture
def invoke() -> Invoke:
    """Run the CLI with a wide, fixed terminal so the output is stable."""
    runner = CliRunner()

    def _invoke(*args: str, env: Mapping[str, str] | None = None) -> Result:
        return runner.invoke(
            app, list(args), env={"COLUMNS": "200", "TERMINAL_WIDTH": "200", **(env or {})}
        )

    return _invoke


@pytest.fixture
def invoke_json(invoke: Invoke) -> InvokeJSON:
    """Run a command with `-o json`, check it succeeded and return the parsed output."""

    def _invoke_json(*args: str, env: Mapping[str, str] | None = None) -> Any:  # noqa: ANN401
        result = invoke(*args, "-o", "json", env=env)
        assert result.exit_code == 0, result.output
        return json.loads(result.stdout)

    return _invoke_json
