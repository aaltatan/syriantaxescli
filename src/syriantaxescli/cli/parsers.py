"""Typer parsers for `Decimal` inputs.

Typer shows a parser's function name as the type in the help, hence the short names.
"""

from decimal import Decimal, InvalidOperation

import typer


def number(value: str | Decimal) -> Decimal:
    """Parse a number such as `1000000`, `1,000,000`, `1_000_000`, `1e6` or `0.11`.

    Raises:
        typer.BadParameter: If `value` is not a finite number.

    """
    if isinstance(value, Decimal):
        return value

    try:
        parsed = Decimal(value.strip().replace(",", "").replace("_", ""))
    except InvalidOperation:
        message = f"{value!r} is not a valid number."
        raise typer.BadParameter(message) from None

    if not parsed.is_finite():
        message = f"{value!r} is not a finite number."
        raise typer.BadParameter(message)

    return parsed


def rate(value: str | Decimal) -> Decimal:
    """Parse a rate such as `0.11`; the tax rules check its range."""
    return number(value)


def amount(value: str | Decimal) -> Decimal:
    """Parse a money amount, which must not be negative."""
    parsed = number(value)

    if parsed < 0:
        message = f"{value!r} must not be negative."
        raise typer.BadParameter(message)

    return parsed
