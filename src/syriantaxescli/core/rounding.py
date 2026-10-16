from dataclasses import dataclass
from decimal import (
    ROUND_05UP,
    ROUND_CEILING,
    ROUND_DOWN,
    ROUND_FLOOR,
    ROUND_HALF_DOWN,
    ROUND_HALF_EVEN,
    ROUND_HALF_UP,
    ROUND_UP,
    Decimal,
)
from enum import StrEnum

from syriantaxes import round_to


class RoundingMethod(StrEnum):
    """The `decimal` module's rounding modes, by their constant values (e.g. `ROUND_HALF_UP`)."""

    CEILING = ROUND_CEILING
    FLOOR = ROUND_FLOOR
    UP = ROUND_UP
    DOWN = ROUND_DOWN
    HALF_UP = ROUND_HALF_UP
    HALF_DOWN = ROUND_HALF_DOWN
    HALF_EVEN = ROUND_HALF_EVEN
    UP05 = ROUND_05UP


@dataclass(frozen=True)
class RoundingRule:
    """A `syriantaxes` rounding function that remembers how it rounds, so it can be shown."""

    method: RoundingMethod
    step: Decimal

    def __post_init__(self) -> None:
        if self.step <= 0:
            message = f"rounding step must be greater than 0, got {self.step}"
            raise ValueError(message)

    def __call__(self, amount: Decimal) -> Decimal:
        return round_to(self.step, self.method.value)(amount)

    def __str__(self) -> str:
        return f"{self.method.name} to {self.step}"
