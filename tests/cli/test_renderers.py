import json
from decimal import Decimal

import pytest
from rich.console import Console
from rich.table import Table

from syriantaxescli.cli.renderers import render_json, render_table
from syriantaxescli.cli.serializers import (
    format_amount,
    format_ratio,
    to_json_number,
    to_records,
)
from syriantaxescli.core import FIELDS, Salary

SALARY = Salary(
    salary=Decimal(1_000_000),
    compensation=Decimal(100_000),
    salary_tax=Decimal(20_900),
    compensation_tax=Decimal(5_000),
)


def _text(table: Table) -> str:
    console = Console(width=200, record=True)
    console.print(table)
    return console.export_text()


# --------------------
# serializers
# --------------------


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (Decimal(5), 5),
        (Decimal("5.00"), 5),
        (Decimal("0E+2"), 0),
        (Decimal("5.5"), 5.5),
        (Decimal(1) / Decimal(3), 1 / 3),
    ],
)
def test_to_json_number(value: Decimal, expected: float) -> None:
    result = to_json_number(value)

    assert result == expected
    assert type(result) is type(expected)


def test_to_records() -> None:
    (record,) = to_records([SALARY])

    assert list(record) == [field.key for field in FIELDS]
    assert record["net"] == 1_074_100
    assert record["compensation_ratio"] == pytest.approx(1 / 11)


def test_formats() -> None:
    assert format_amount(Decimal("1234567.891")) == "1,234,567.89"
    assert format_amount(Decimal(0)) == "0.00"
    assert format_ratio(Decimal("0.0909")) == "9.09%"


# --------------------
# tables
# --------------------


def test_one_salary_is_shown_as_a_card() -> None:
    table = render_table(SALARY, title="Gross Salary")

    assert table.title == "Gross Salary"
    assert table.row_count == len(FIELDS)

    text = _text(table)
    assert "Compensation Ratio" in text
    assert "9.09%" in text
    assert "1,074,100.00" in text


def test_several_salaries_are_shown_one_per_row() -> None:
    table = render_table([SALARY, SALARY, SALARY], title="Salary Scale")

    assert table.row_count == 3
    headers = [str(column.header) for column in table.columns]
    assert headers == [
        "#",
        "Salary",
        "Compensation",
        "Total",
        "Social Security",
        "Salary Tax",
        "Compensation Tax",
        "Net",
    ]


def test_an_empty_list_is_an_empty_table() -> None:
    assert render_table([], title="Nothing").row_count == 0


# --------------------
# JSON
# --------------------


def test_one_salary_is_a_json_object() -> None:
    data = json.loads(render_json(SALARY, indent=2))

    assert data["net"] == 1_074_100


def test_several_salaries_are_a_json_array() -> None:
    data = json.loads(render_json([SALARY, SALARY], indent=2))

    assert [row["net"] for row in data] == [1_074_100, 1_074_100]


def test_json_indent() -> None:
    assert "\n" not in render_json(SALARY, indent=0)
    assert '\n    "salary"' in render_json(SALARY, indent=4)
