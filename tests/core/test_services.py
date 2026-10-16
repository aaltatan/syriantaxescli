"""Expected amounts are worked out by hand from the default rules.

Brackets: 0% up to 837,000, 11% up to 850,000, 13% up to 1,100,000, then 15%.
Taxes are rounded half up to 100; compensations are taxed at a flat 5%; social security
is 7% of the insured salary, rounded half up to 1.
"""

from decimal import Decimal
from functools import partial

import pytest
from syriantaxes import Bracket, SalaryBelowMinimumError, TaxRules

from syriantaxescli.core import (
    amount_range,
    calculate_gross,
    calculate_net,
    calculate_net_range,
    make_brackets,
)
from syriantaxescli.core.config import preset_settings

D = Decimal
MIN_SALARY = D(837_000)
MAX_RANGE_SIZE = 1000
amount_range_ = partial(
    amount_range, max_size=MAX_RANGE_SIZE, stop_factor=D(10), step_divisor=D(10)
)


# --------------------
# make_brackets
# --------------------


def test_make_brackets_pairs_lowers_with_rates() -> None:
    assert make_brackets([D(0), D(100)], [D(0), D("0.1")]) == (
        Bracket(D(0), D(0)),
        Bracket(D(100), D("0.1")),
    )


@pytest.mark.parametrize(
    ("lowers", "rates"),
    [([D(0), D(100)], [D(0)]), ([D(0)], [D(0), D("0.1")]), ([], [D(0)])],
)
def test_make_brackets_needs_a_rate_for_every_lower(
    lowers: list[Decimal], rates: list[Decimal]
) -> None:
    with pytest.raises(ValueError, match="every bracket needs both"):
        make_brackets(lowers, rates)


def test_make_brackets_rejects_a_rate_of_one() -> None:
    with pytest.raises(ValueError, match="rate must be at least 0 and below 1"):
        make_brackets([D(0)], [D(1)])


def test_make_brackets_of_nothing_is_empty() -> None:
    assert make_brackets([], []) == ()


# --------------------
# calculate_gross
# --------------------


@pytest.mark.parametrize(
    ("salary", "compensation", "salary_tax", "compensation_tax", "net"),
    [
        # Below the first taxed bracket: no salary tax at all.
        (500_000, 0, 0, 0, 500_000),
        (837_000, 0, 0, 0, 837_000),
        # 11% of 13,000 = 1,430 -> 1,400.
        (850_000, 0, 1_400, 0, 848_600),
        # 1,430 + 13% of 150,000 = 20,930 -> 20,900.
        (1_000_000, 100_000, 20_900, 5_000, 1_074_100),
        # 1,430 + 32,500 + 15% of 900,000 = 168,930 -> 168,900.
        (2_000_000, 0, 168_900, 0, 1_831_100),
        # Compensations only.
        (0, 1_000_000, 0, 50_000, 950_000),
        (0, 0, 0, 0, 0),
    ],
)
def test_calculate_gross(
    rules: TaxRules,
    salary: int,
    compensation: int,
    salary_tax: int,
    compensation_tax: int,
    net: int,
) -> None:
    result = calculate_gross(rules, D(salary), D(compensation))

    assert result.salary == salary
    assert result.compensation == compensation
    assert result.social_security == 0
    assert result.salary_tax == salary_tax
    assert result.compensation_tax == compensation_tax
    assert result.net == net


def test_calculate_gross_deducts_social_security_before_tax(ss_rules: TaxRules) -> None:
    # 7% of 750,000 = 52,500; tax on 947,500 = 1,430 + 12,675 = 14,105 -> 14,100.
    result = calculate_gross(ss_rules, D(1_000_000), D(100_000), insured_salary=D(750_000))

    assert result.social_security == 52_500
    assert result.salary_tax == 14_100
    assert result.net == 1_028_400


def test_calculate_gross_insures_the_gross_salary_by_default(ss_rules: TaxRules) -> None:
    result = calculate_gross(ss_rules, D(1_000_000))

    assert result.social_security == 70_000


def test_calculate_gross_ignores_the_insured_salary_without_social_security(
    rules: TaxRules,
) -> None:
    result = calculate_gross(rules, D(1_000_000), insured_salary=D(750_000))

    assert result.social_security == 0


def test_calculate_gross_rejects_an_insured_salary_below_the_minimum(ss_rules: TaxRules) -> None:
    with pytest.raises(ValueError, match="insured salary must be at least 750000"):
        calculate_gross(ss_rules, D(1_000_000), insured_salary=D(500_000))


@pytest.mark.parametrize(("salary", "compensation"), [(-1, 0), (0, -1)])
def test_calculate_gross_rejects_negative_amounts(
    rules: TaxRules, salary: int, compensation: int
) -> None:
    with pytest.raises(ValueError, match="must not be negative"):
        calculate_gross(rules, D(salary), D(compensation))


def test_calculate_gross_keeps_fractions(rules: TaxRules) -> None:
    result = calculate_gross(rules, D("837000.50"))

    assert result.salary == D("837000.50")
    assert result.net == D("837000.50")


# --------------------
# calculate_net
# --------------------


def test_calculate_net_without_compensation(rules: TaxRules) -> None:
    # Gross 1,024,100: tax 1,430 + 13% of 174,100 = 24,063 -> 24,100.
    result = calculate_net(rules, D(1_000_000))

    assert result.salary == 1_024_100
    assert result.compensation == 0
    assert result.net == 1_000_000


def test_calculate_net_splits_salary_and_compensation(rules: TaxRules) -> None:
    result = calculate_net(rules, D(4_000_000), D("0.75"))

    assert result.salary == 1_024_100
    assert result.compensation == 3_157_900
    assert result.net == 4_000_000


def test_calculate_net_pays_at_least_the_minimum_salary(rules: TaxRules) -> None:
    result = calculate_net(rules, D(1_000_000), D(1))

    assert result.salary == MIN_SALARY
    assert result.net >= 1_000_000


def test_calculate_net_accounts_for_social_security(ss_rules: TaxRules) -> None:
    result = calculate_net(ss_rules, D(1_000_000))

    assert result.social_security > 0
    assert result.net >= 1_000_000


def test_calculate_net_at_exactly_the_minimum_salary(rules: TaxRules) -> None:
    result = calculate_net(rules, MIN_SALARY)

    assert result.salary == MIN_SALARY
    assert result.net == MIN_SALARY


def test_calculate_net_below_the_minimum_salary(rules: TaxRules) -> None:
    with pytest.raises(SalaryBelowMinimumError):
        calculate_net(rules, MIN_SALARY - 1)


@pytest.mark.parametrize("share", ["-0.1", "1.01"])
def test_calculate_net_rejects_a_share_outside_zero_to_one(rules: TaxRules, share: str) -> None:
    with pytest.raises(ValueError, match="compensation_share must be between 0 and 1"):
        calculate_net(rules, D(1_000_000), D(share))


# syriantaxes 1.0 `gross_compensation` returns round(net / (1 - rate)) without checking
# that the net left after the *rounded* tax reaches the target (unlike `gross_salary`), so
# with taxes rounded to 100 the net compensation can fall up to ~100 short.
# These are strict: they start failing, as a reminder to drop the mark, once it is fixed.
COMPENSATION_SHORTFALL = pytest.mark.xfail(
    strict=True, reason="syriantaxes 1.0 gross_compensation can net less than asked"
)


@pytest.mark.parametrize(
    "share",
    [
        "0",
        pytest.param("0.1", marks=COMPENSATION_SHORTFALL),
        pytest.param("0.5", marks=COMPENSATION_SHORTFALL),
        pytest.param("1", marks=COMPENSATION_SHORTFALL),
    ],
)
@pytest.mark.parametrize("social_security", [False, True])
def test_calculate_net_always_reaches_the_target(share: str, *, social_security: bool) -> None:
    rules = preset_settings().tax.to_rules(social_security=social_security)

    for target in range(837_000, 5_000_000, 9_973):
        result = calculate_net(rules, D(target), D(share))

        assert result.net >= target, target
        # Rounding to 100 can overshoot, but never by much.
        assert result.net - target < 200


@pytest.mark.parametrize("share", ["0", "0.1", "0.5", "1"])
def test_calculate_net_stays_close_to_the_target(share: str, rules: TaxRules) -> None:
    for target in range(837_000, 5_000_000, 9_973):
        result = calculate_net(rules, D(target), D(share))

        assert abs(result.net - target) < 200, target
        # Recalculating from the gross gives the same answer.
        assert calculate_gross(rules, result.salary, result.compensation) == result


@COMPENSATION_SHORTFALL
def test_calculate_net_with_compensation_reaches_the_target(rules: TaxRules) -> None:
    # The salary is the 837,000 minimum, so the compensation must net 100,020:
    # 100,020 / 0.95 = 105,284.2 -> 105,300, taxed 5,265 -> 5,300, which nets only 100,000.
    result = calculate_net(rules, D(937_020), D(1))

    assert result.net >= 937_020


# --------------------
# amount_range
# --------------------


def test_amount_range_includes_both_ends() -> None:
    assert amount_range_(D(1_000), D(1_300), D(100)) == [D(1_000), D(1_100), D(1_200), D(1_300)]


def test_amount_range_stops_before_passing_stop() -> None:
    assert amount_range_(D(1_000), D(1_250), D(100)) == [D(1_000), D(1_100), D(1_200)]


def test_amount_range_of_one_amount() -> None:
    assert amount_range_(D(1_000), D(1_000), D(100)) == [D(1_000)]


def test_amount_range_with_a_step_bigger_than_the_range() -> None:
    assert amount_range_(D(1_000), D(1_050), D(100)) == [D(1_000)]


def test_amount_range_defaults_to_ten_times_start_in_tenths() -> None:
    amounts = amount_range_(D(1_000_000))

    assert len(amounts) == 91
    assert amounts[0] == 1_000_000
    assert amounts[1] == 1_100_000
    assert amounts[-1] == 10_000_000


def test_amount_range_with_fractional_steps() -> None:
    assert amount_range_(D(1), D(2), D("0.3")) == [D(1), D("1.3"), D("1.6"), D("1.9")]


@pytest.mark.parametrize("step", ["0", "-1"])
def test_amount_range_rejects_a_step_that_is_not_positive(step: str) -> None:
    with pytest.raises(ValueError, match="step must be greater than 0"):
        amount_range_(D(1_000), D(2_000), D(step))


def test_amount_range_starting_at_zero_needs_a_step() -> None:
    with pytest.raises(ValueError, match="step must be greater than 0"):
        amount_range_(D(0))


def test_amount_range_rejects_stop_below_start() -> None:
    with pytest.raises(ValueError, match="must not be less than start"):
        amount_range_(D(2_000), D(1_000), D(100))


def test_amount_range_allows_exactly_the_maximum_size() -> None:
    assert len(amount_range_(D(1), D(MAX_RANGE_SIZE), D(1))) == MAX_RANGE_SIZE


def test_amount_range_rejects_more_than_the_maximum_size() -> None:
    with pytest.raises(ValueError, match="at most 1,000 are allowed"):
        amount_range_(D(1), D(MAX_RANGE_SIZE + 1), D(1))


# --------------------
# calculate_net_range
# --------------------


def test_calculate_net_range(rules: TaxRules) -> None:
    nets = [D(1_000_000), D(2_000_000)]

    results = calculate_net_range(rules, nets, D("0.5"))

    assert [result.net >= net for result, net in zip(results, nets, strict=True)] == [True, True]
    assert results[0] == calculate_net(rules, nets[0], D("0.5"))


def test_calculate_net_range_of_nothing(rules: TaxRules) -> None:
    assert calculate_net_range(rules, []) == []


def test_calculate_net_range_stops_at_the_first_amount_below_the_minimum(rules: TaxRules) -> None:
    with pytest.raises(SalaryBelowMinimumError):
        calculate_net_range(rules, [D(1_000_000), D(1)])
