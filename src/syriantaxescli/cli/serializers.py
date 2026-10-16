from collections.abc import Sequence
from decimal import Decimal

from syriantaxescli.core import Salary, to_dict

type JSONNumber = int | float
type Record = dict[str, JSONNumber]


def to_json_number(value: Decimal) -> JSONNumber:
    """Return whole amounts as `int` and anything else as `float`."""
    if value == value.to_integral_value():
        return int(value)

    return float(value)


def to_records(salaries: Sequence[Salary]) -> list[Record]:
    return [
        {key: to_json_number(value) for key, value in to_dict(salary).items()}
        for salary in salaries
    ]


def format_amount(value: Decimal) -> str:
    return f"{value:,.2f}"


def format_ratio(value: Decimal) -> str:
    return f"{value:.2%}"
