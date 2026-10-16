import csv
import json
from collections.abc import Callable, Sequence
from pathlib import Path

import openpyxl

from syriantaxescli.core import FIELDS, Salary, to_dict

from .serializers import to_records

type ExportFn = Callable[[Sequence[Salary], Path], None]


class ExtensionNotSupportedError(Exception):
    def __init__(self, extension: str, supported: Sequence[str]) -> None:
        super().__init__(
            f"Can't export to '.{extension}' files; use one of: "
            + ", ".join(f".{ext}" for ext in supported)
        )


class ExportersRegistry:
    def __init__(self) -> None:
        self._exporters: dict[str, ExportFn] = {}

    @property
    def extensions(self) -> list[str]:
        return list(self._exporters)

    def register(self, extension: str) -> Callable[[ExportFn], ExportFn]:
        def decorator(export_fn: ExportFn) -> ExportFn:
            self._exporters[extension] = export_fn
            return export_fn

        return decorator

    def __getitem__(self, extension: str) -> ExportFn:
        if extension not in self._exporters:
            raise ExtensionNotSupportedError(extension, self.extensions)

        return self._exporters[extension]

    def export(self, salaries: Sequence[Salary], path: Path) -> None:
        """Write `salaries` to `path` in the format its extension names."""
        self[get_extension(path)](salaries, path)


def get_extension(path: Path) -> str:
    return path.suffix.lower().removeprefix(".")


exporters = ExportersRegistry()


@exporters.register("xlsx")
def export_xlsx(salaries: Sequence[Salary], path: Path) -> None:
    wb = openpyxl.Workbook()
    ws = wb.active

    if ws is None:  # pragma: no cover - a new workbook always has an active sheet
        message = "Workbook has no active sheet"
        raise ValueError(message)

    ws.title = "Salaries"
    ws.append(["#", *(field.header for field in FIELDS)])

    for index, salary in enumerate(salaries, start=1):
        ws.append([index, *(field.getter(salary) for field in FIELDS)])

    for column, field in enumerate(FIELDS, start=2):
        number_format = "0.00%" if field.key == "compensation_ratio" else "#,##0.00"
        for (cell,) in ws.iter_rows(min_row=2, min_col=column, max_col=column):
            cell.number_format = number_format

    wb.save(path)


@exporters.register("csv")
def export_csv(salaries: Sequence[Salary], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(field.key for field in FIELDS)
        writer.writerows(to_dict(salary).values() for salary in salaries)


@exporters.register("json")
def export_json(salaries: Sequence[Salary], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(to_records(salaries), f, indent=4)


@exporters.register("jsonl")
def export_jsonl(salaries: Sequence[Salary], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        f.writelines(json.dumps(record) + "\n" for record in to_records(salaries))
