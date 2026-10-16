import decimal
from decimal import Decimal

import pytest

from syriantaxescli.core import RoundingMethod, RoundingRule


def test_methods_are_the_decimal_rounding_modes() -> None:
    for method in RoundingMethod:
        assert method.value == getattr(decimal, f"ROUND_{method.name}".replace("UP05", "05UP"))


@pytest.mark.parametrize(
    ("method", "amount", "expected"),
    [
        (RoundingMethod.HALF_UP, "1250", "1300"),
        (RoundingMethod.HALF_UP, "1249.99", "1200"),
        (RoundingMethod.HALF_DOWN, "1250", "1200"),
        (RoundingMethod.HALF_EVEN, "1250", "1200"),
        (RoundingMethod.HALF_EVEN, "1350", "1400"),
        (RoundingMethod.CEILING, "1201", "1300"),
        (RoundingMethod.FLOOR, "1299", "1200"),
        (RoundingMethod.UP, "1201", "1300"),
        (RoundingMethod.DOWN, "1299", "1200"),
        (RoundingMethod.CEILING, "1200", "1200"),
    ],
)
def test_rounds_to_a_multiple_of_the_step(
    method: RoundingMethod, amount: str, expected: str
) -> None:
    assert RoundingRule(method, Decimal(100))(Decimal(amount)) == Decimal(expected)


def test_rounds_to_fractional_steps() -> None:
    rule = RoundingRule(RoundingMethod.HALF_UP, Decimal("0.01"))
    assert rule(Decimal("10.005")) == Decimal("10.01")


@pytest.mark.parametrize("step", ["0", "-100"])
def test_rejects_a_step_that_is_not_positive(step: str) -> None:
    with pytest.raises(ValueError, match="rounding step must be greater than 0"):
        RoundingRule(RoundingMethod.HALF_UP, Decimal(step))


def test_shows_how_it_rounds() -> None:
    assert str(RoundingRule(RoundingMethod.CEILING, Decimal(100))) == "CEILING to 100"


def test_rules_with_the_same_settings_are_equal() -> None:
    assert RoundingRule(RoundingMethod.UP, Decimal(1)) == RoundingRule(
        RoundingMethod.UP, Decimal(1)
    )
