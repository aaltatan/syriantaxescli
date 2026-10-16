"""Tax calculations, independent of the command line."""

from .rounding import RoundingMethod, RoundingRule
from .salary import FIELDS, Field, Salary, to_dict
from .services import (
    amount_range,
    calculate_gross,
    calculate_net,
    calculate_net_range,
    make_brackets,
)

__all__ = [
    "FIELDS",
    "Field",
    "RoundingMethod",
    "RoundingRule",
    "Salary",
    "amount_range",
    "calculate_gross",
    "calculate_net",
    "calculate_net_range",
    "make_brackets",
    "to_dict",
]
