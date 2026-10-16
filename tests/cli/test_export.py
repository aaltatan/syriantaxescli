import json
from pathlib import Path

import openpyxl
import pytest

from tests.conftest import Invoke


@pytest.mark.parametrize("flag", ["-e", "--export", "--write-path"])
def test_export_instead_of_printing(invoke: Invoke, tmp_path: Path, flag: str) -> None:
    path = tmp_path / "scale.json"

    result = invoke("range", "1000000", "1200000", "100000", flag, str(path))

    assert result.exit_code == 0, result.output
    assert "Exported 3 row(s) to" in result.output
    assert "Salary Scale" not in result.output
    assert len(json.loads(path.read_text(encoding="utf-8"))) == 3


def test_export_one_salary(invoke: Invoke, tmp_path: Path) -> None:
    path = tmp_path / "payslip.xlsx"

    result = invoke("gross", "1000000", "100000", "-e", str(path))

    assert result.exit_code == 0, result.output
    assert "Exported 1 row(s)" in result.output
    ws = openpyxl.load_workbook(path).active
    assert ws is not None
    assert ws.max_row == 2


def test_export_wins_over_json_output(invoke: Invoke, tmp_path: Path) -> None:
    path = tmp_path / "net.csv"

    result = invoke("net", "1000000", "-o", "json", "-e", str(path))

    assert result.exit_code == 0
    assert result.stdout.startswith("Exported")
    assert path.exists()


def test_existing_file_is_kept(invoke: Invoke, tmp_path: Path) -> None:
    path = tmp_path / "scale.csv"
    path.write_text("keep me", encoding="utf-8")

    result = invoke("gross", "1000000", "-e", str(path))

    assert result.exit_code == 2
    assert "already exists; pass --overwrite" in result.output
    assert path.read_text(encoding="utf-8") == "keep me"


def test_overwrite(invoke: Invoke, tmp_path: Path) -> None:
    path = tmp_path / "scale.csv"
    path.write_text("old", encoding="utf-8")

    result = invoke("gross", "1000000", "-e", str(path), "--overwrite")

    assert result.exit_code == 0, result.output
    assert path.read_text(encoding="utf-8").startswith("salary,")


def test_unsupported_extension(invoke: Invoke, tmp_path: Path) -> None:
    path = tmp_path / "scale.txt"

    result = invoke("gross", "1000000", "-e", str(path))

    assert result.exit_code == 2
    assert "Can't export to '.txt' files" in result.output
    assert not path.exists()


def test_missing_folder(invoke: Invoke, tmp_path: Path) -> None:
    path = tmp_path / "missing" / "scale.xlsx"

    result = invoke("gross", "1000000", "-e", str(path))

    assert result.exit_code == 2
    assert "does not exist" in result.output


def test_export_to_a_folder(invoke: Invoke, tmp_path: Path) -> None:
    result = invoke("gross", "1000000", "-e", str(tmp_path))

    assert result.exit_code == 2
    assert "is a directory" in result.output


def test_nothing_is_written_when_the_calculation_fails(invoke: Invoke, tmp_path: Path) -> None:
    path = tmp_path / "scale.xlsx"

    result = invoke("net", "1", "-e", str(path))

    assert result.exit_code == 2
    assert not path.exists()


def test_json_indent(invoke: Invoke) -> None:
    compact = invoke("gross", "1000000", "-o", "json", "--json-indent", "0")
    indented = invoke("gross", "1000000", "-o", "json", "--json-indent", "2")

    assert compact.stdout.count("\n") == 1
    assert '\n  "salary"' in indented.stdout
    assert json.loads(compact.stdout) == json.loads(indented.stdout)


def test_negative_json_indent(invoke: Invoke) -> None:
    result = invoke("gross", "1000000", "-o", "json", "--json-indent", "-1")

    assert result.exit_code == 2


@pytest.mark.parametrize("output", ["JSON", "Json"])
def test_output_is_case_insensitive(invoke: Invoke, output: str) -> None:
    result = invoke("gross", "1000000", "-o", output)

    assert result.exit_code == 0
    assert json.loads(result.stdout)["salary"] == 1_000_000
