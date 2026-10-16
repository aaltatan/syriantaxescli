import json
from collections.abc import Sequence
from typing import Final

from rich.table import Table

from syriantaxescli.core import FIELDS, Field, Salary

from .serializers import Record, format_amount, format_ratio, to_records

STYLES: Final = {
    "total": "green",
    "taxes": "red",
    "deductions": "red",
    "net": "bold green",
}

# The wide table leaves out the sums that the other columns already show.
WIDE_TABLE_KEYS: Final = (
    "salary",
    "compensation",
    "total",
    "social_security",
    "salary_tax",
    "compensation_tax",
    "net",
)


def _format(field: Field, salary: Salary) -> str:
    value = field.getter(salary)
    return format_ratio(value) if field.key == "compensation_ratio" else format_amount(value)


def render_table(result: Salary | Sequence[Salary], *, title: str) -> Table:
    """Show one salary as a two-column card, and a list of salaries as one row each."""
    if isinstance(result, Salary):
        return _render_card(result, title=title)

    return _render_rows(result, title=title)


def _render_card(salary: Salary, *, title: str) -> Table:
    table = Table(title=title)
    table.add_column("Item")
    table.add_column("Amount", justify="right")

    for field in FIELDS:
        style = STYLES.get(field.key)
        table.add_row(field.header, _format(field, salary), style=style)

    return table


def _render_rows(salaries: Sequence[Salary], *, title: str) -> Table:
    fields = [field for field in FIELDS if field.key in WIDE_TABLE_KEYS]

    table = Table(title=title)
    table.add_column("#", justify="right")
    for field in fields:
        table.add_column(field.header, justify="right", style=STYLES.get(field.key))

    for index, salary in enumerate(salaries, start=1):
        table.add_row(str(index), *(_format(field, salary) for field in fields))

    return table


def render_json(result: Salary | Sequence[Salary], *, indent: int) -> str:
    """Render one salary as a JSON object, and a list of salaries as an array."""
    if isinstance(result, Salary):
        data: Record | list[Record] = to_records([result])[0]
    else:
        data = to_records(result)

    return json.dumps(data, indent=indent or None)
