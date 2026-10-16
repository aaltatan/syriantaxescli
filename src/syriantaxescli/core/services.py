from collections.abc import Iterable, Sequence
from decimal import Decimal

from syriantaxes import Bracket, TaxRules, compensation_tax, salary_breakdown, split_net_package

from .salary import Salary


def make_brackets(lowers: Sequence[Decimal], rates: Sequence[Decimal]) -> tuple[Bracket, ...]:
    """Pair each bracket's lower bound with its rate.

    Raises:
        ValueError: If the counts differ, or a bound or rate is invalid.

    """
    if len(lowers) != len(rates):
        message = (
            f"got {len(lowers)} bracket lower bound(s) but {len(rates)} rate(s); "
            "every bracket needs both"
        )
        raise ValueError(message)

    return tuple(Bracket(lower, rate) for lower, rate in zip(lowers, rates, strict=True))


def calculate_gross(
    rules: TaxRules,
    salary: Decimal,
    compensation: Decimal = Decimal(0),
    *,
    insured_salary: Decimal | None = None,
) -> Salary:
    """Work out the taxes and net of a gross salary and compensation.

    Social security is deducted only when `rules` include it, based on `insured_salary`
    (which defaults to the salary itself).
    """
    _check_not_negative(salary, "salary")
    _check_not_negative(compensation, "compensation")

    breakdown = salary_breakdown(rules, salary, insured_salary=insured_salary)

    return Salary(
        salary=salary,
        compensation=compensation,
        social_security=breakdown.social_security,
        salary_tax=breakdown.tax,
        compensation_tax=compensation_tax(rules, compensation),
    )


def calculate_net(
    rules: TaxRules, net: Decimal, compensation_share: Decimal = Decimal(0)
) -> Salary:
    """Find the gross salary and compensation that pay a wanted net total.

    `compensation_share` of the net is paid as compensation and the rest as salary. The
    resulting net is at least `net`; rounding can push it slightly above.

    Raises:
        syriantaxes.SalaryBelowMinimumError: If `net` is below the minimum salary.
        ValueError: If `compensation_share` is not between 0 and 1.

    """
    package = split_net_package(rules, net, compensation_share)
    return calculate_gross(rules, package.salary, package.compensation)


def calculate_net_range(
    rules: TaxRules, nets: Iterable[Decimal], compensation_share: Decimal = Decimal(0)
) -> list[Salary]:
    return [calculate_net(rules, net, compensation_share) for net in nets]


def amount_range(  # noqa: PLR0913
    start: Decimal,
    stop: Decimal | None = None,
    step: Decimal | None = None,
    *,
    max_size: int,
    stop_factor: Decimal,
    step_divisor: Decimal,
) -> list[Decimal]:
    """Return the amounts from `start` to `stop` (inclusive) every `step`.

    `stop` defaults to `start * stop_factor` and `step` to `start / step_divisor`.

    Raises:
        ValueError: If `step` is not positive, `stop` is below `start`, or the range
            has more than `max_size` amounts.

    """
    stop = start * stop_factor if stop is None else stop
    step = start / step_divisor if step is None else step

    if step <= 0:
        message = f"step must be greater than 0, got {step}"
        raise ValueError(message)

    if stop < start:
        message = f"stop ({stop}) must not be less than start ({start})"
        raise ValueError(message)

    size = int((stop - start) / step) + 1

    if size > max_size:
        message = (
            f"the range has {size:,} amounts but at most {max_size:,} are allowed; "
            "use a bigger step or a smaller range"
        )
        raise ValueError(message)

    return [start + step * index for index in range(size)]


def _check_not_negative(value: Decimal, name: str) -> None:
    if value < 0:
        message = f"{name} must not be negative, got {value}"
        raise ValueError(message)
