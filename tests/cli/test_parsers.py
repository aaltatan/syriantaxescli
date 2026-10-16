from decimal import Decimal

import pytest
import typer

from syriantaxescli.cli import parsers


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1000000", "1000000"),
        ("1,000,000", "1000000"),
        ("1_000_000", "1000000"),
        ("1e6", "1E+6"),
        ("0.11", "0.11"),
        (" 42 ", "42"),
        ("-5", "-5"),
        ("1,000.50", "1000.50"),
    ],
)
def test_number_parses_common_spellings(text: str, expected: str) -> None:
    assert parsers.number(text) == Decimal(expected)


def test_number_keeps_decimals_as_they_are() -> None:
    value = Decimal("0.13")
    assert parsers.number(value) is value


@pytest.mark.parametrize("text", ["", "abc", "1.2.3", "12abc", "--1"])
def test_number_rejects_text_that_is_not_a_number(text: str) -> None:
    with pytest.raises(typer.BadParameter, match="is not a valid number"):
        parsers.number(text)


@pytest.mark.parametrize("text", ["nan", "NaN", "inf", "-Infinity", "sNaN"])
def test_number_rejects_numbers_that_are_not_finite(text: str) -> None:
    with pytest.raises(typer.BadParameter, match="is not a finite number"):
        parsers.number(text)


def test_rate_is_any_number() -> None:
    assert parsers.rate("0.15") == Decimal("0.15")
    assert parsers.rate("-0.1") == Decimal("-0.1")


@pytest.mark.parametrize("text", ["0", "-0", "837000", "0.01"])
def test_amount_accepts_zero_and_up(text: str) -> None:
    assert parsers.amount(text) == Decimal(text)


@pytest.mark.parametrize("value", ["-1", "-0.01", Decimal(-1)])
def test_amount_rejects_negative_amounts(value: str | Decimal) -> None:
    with pytest.raises(typer.BadParameter, match="must not be negative"):
        parsers.amount(value)
