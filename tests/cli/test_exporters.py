import csv
import json
from decimal import Decimal
from pathlib import Path

import openpyxl
import pytest

from syriantaxescli.cli.exporters import (
    ExportersRegistry,
    ExtensionNotSupportedError,
    exporters,
    get_extension,
)
from syriantaxescli.core import FIELDS, Salary

SALARIES = [
    Salary(salary=Decimal(1_000_000), compensation=Decimal(100_000), salary_tax=Decimal(20_900)),
    Salary(salary=Decimal(2_000_000), salary_tax=Decimal(168_900)),
]


def test_supported_extensions() -> None:
    assert sorted(exporters.extensions) == ["csv", "json", "jsonl", "xlsx"]


@pytest.mark.parametrize(
    ("name", "extension"),
    [("a.xlsx", "xlsx"), ("A.XLSX", "xlsx"), ("a.b.json", "json"), ("noext", "")],
)
def test_get_extension(name: str, extension: str) -> None:
    assert get_extension(Path(name)) == extension


@pytest.mark.parametrize("extension", ["txt", "xls", ""])
def test_unsupported_extensions(extension: str) -> None:
    with pytest.raises(ExtensionNotSupportedError, match=r"use one of: \.xlsx, \.csv"):
        exporters[extension]


def test_xlsx(tmp_path: Path) -> None:
    path = tmp_path / "scale.xlsx"

    exporters.export(SALARIES, path)

    ws = openpyxl.load_workbook(path).active
    assert ws is not None
    rows = list(ws.iter_rows(values_only=True))
    assert rows[0] == ("#", *(field.header for field in FIELDS))
    assert len(rows) == 3
    assert rows[1][0] == 1
    assert rows[2][0] == 2
    net_column = 1 + [field.key for field in FIELDS].index("net")
    assert rows[1][net_column] == 1_079_100
    assert ws.cell(row=2, column=net_column + 1).number_format == "#,##0.00"
    assert ws.cell(row=2, column=len(FIELDS) + 1).number_format == "0.00%"


def test_xlsx_with_uppercase_extension(tmp_path: Path) -> None:
    path = tmp_path / "SCALE.XLSX"

    exporters.export(SALARIES, path)

    assert openpyxl.load_workbook(path).active is not None


def test_csv(tmp_path: Path) -> None:
    path = tmp_path / "scale.csv"

    exporters.export(SALARIES, path)

    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2
    assert list(rows[0]) == [field.key for field in FIELDS]
    assert Decimal(rows[0]["net"]) == 1_079_100
    assert Decimal(rows[1]["salary_tax"]) == 168_900


def test_json(tmp_path: Path) -> None:
    path = tmp_path / "scale.json"

    exporters.export(SALARIES, path)

    data = json.loads(path.read_text(encoding="utf-8"))
    assert [row["net"] for row in data] == [1_079_100, 1_831_100]


def test_jsonl_has_one_valid_json_object_per_line(tmp_path: Path) -> None:
    path = tmp_path / "scale.jsonl"

    exporters.export(SALARIES, path)

    lines = path.read_text(encoding="utf-8").splitlines()
    assert [json.loads(line)["net"] for line in lines] == [1_079_100, 1_831_100]


def test_exporting_nothing_writes_only_headers(tmp_path: Path) -> None:
    path = tmp_path / "empty.csv"

    exporters.export([], path)

    assert path.read_text(encoding="utf-8").strip() == ",".join(field.key for field in FIELDS)


def test_register_a_new_exporter() -> None:
    registry = ExportersRegistry()
    written: list[Path] = []

    @registry.register("txt")
    def export_txt(_salaries: object, path: Path) -> None:
        written.append(path)

    registry.export(SALARIES, Path("a.TXT"))

    assert written == [Path("a.TXT")]
    assert registry.extensions == ["txt"]
