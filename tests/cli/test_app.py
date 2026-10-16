import io
import runpy
import sys
from importlib.metadata import version

import pytest

from syriantaxescli.main import main, use_utf8
from tests.conftest import Invoke

COMMANDS = {
    "gross": ("g",),
    "net": ("n",),
    "range": ("ar", "r"),
    "rules": (),
    "config": ("cfg",),
}


def test_no_arguments_shows_the_help(invoke: Invoke) -> None:
    result = invoke()

    assert "Usage: root [OPTIONS] COMMAND" in result.output
    assert "Calculate Syrian salary and compensation taxes." in result.output


def test_help_has_an_ascii_banner_and_lists_commands_with_aliases(invoke: Invoke) -> None:
    result = invoke("--help")

    assert result.exit_code == 0
    assert "███████╗" in result.output
    for name, aliases in COMMANDS.items():
        assert (f"{name} ({', '.join(aliases)})" if aliases else name) in result.output


@pytest.mark.parametrize(
    "name", [name for name, aliases in COMMANDS.items() for name in (name, *aliases)]
)
def test_every_command_and_alias_has_help(invoke: Invoke, name: str) -> None:
    result = invoke(name, "--help")

    assert result.exit_code == 0, result.output
    # Tax rules are global options now, so command help stays short.
    assert "--brackets-mins" not in result.output


@pytest.mark.parametrize("flag", ["-v", "--version"])
def test_version(invoke: Invoke, flag: str) -> None:
    result = invoke(flag)

    assert result.exit_code == 0
    assert result.output.strip() == f"sytax {version('syriantaxescli')}"


def test_unknown_command(invoke: Invoke) -> None:
    result = invoke("taxes")

    assert result.exit_code == 2
    assert "No such command 'taxes'" in result.output


def test_help_documents_environment_variables(invoke: Invoke) -> None:
    result = invoke("--help")

    assert "Tax Rules" in result.output
    assert "Configuration" in result.output
    for name in (
        "SYRIANTAXES_BRACKET_TAX_MINS",
        "SYRIANTAXES_BRACKET_TAX_RATES",
        "SYRIANTAXES_MIN_ALLOWED_SALARY",
        "SYRIANTAXES_FIXED_TAX_RATE",
        "SYRIANTAXES_TAXES_ROUNDING_METHOD",
        "SYRIANTAXES_TAXES_ROUND_TO_NEAREST",
        "SYRIANTAXES_SS_ENABLED",
        "SYRIANTAXES_SS_DEDUCTION_RATE",
        "SYRIANTAXES_MIN_SS_ALLOWED_SALARY",
        "SYRIANTAXES_SS_ROUNDING_METHOD",
        "SYRIANTAXES_SS_ROUND_TO_NEAREST",
    ):
        assert name in result.output


# --------------------
# Entry points
# --------------------


def test_use_utf8_reconfigures_streams_that_are_not_utf8() -> None:
    cp1252 = io.TextIOWrapper(io.BytesIO(), encoding="cp1252")
    utf8 = io.TextIOWrapper(io.BytesIO(), encoding="UTF-8")
    other = io.StringIO()

    use_utf8([cp1252, utf8, other])

    assert cp1252.encoding == "utf-8"
    assert utf8.encoding == "UTF-8"
    cp1252.write("██")  # would raise UnicodeEncodeError in cp1252


def test_main_runs_the_app(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["sytax", "--version"])

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 0
    assert "sytax" in capsys.readouterr().out


def test_python_dash_m(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(sys, "argv", ["sytax", "--version"])

    with pytest.raises(SystemExit):
        runpy.run_module("syriantaxescli", run_name="__main__")

    assert "sytax" in capsys.readouterr().out
