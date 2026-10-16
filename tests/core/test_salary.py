from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from syriantaxescli.core import FIELDS, Salary, to_dict


def test_derived_amounts() -> None:
    salary = Salary(
        salary=Decimal(1_000_000),
        compensation=Decimal(100_000),
        social_security=Decimal(52_500),
        salary_tax=Decimal(14_100),
        compensation_tax=Decimal(5_000),
    )

    assert salary.total == Decimal(1_100_000)
    assert salary.taxes == Decimal(19_100)
    assert salary.deductions == Decimal(71_600)
    assert salary.net == Decimal(1_028_400)
    assert salary.compensation_ratio == Decimal(100_000) / Decimal(1_100_000)


def test_defaults_to_no_compensation_and_no_deductions() -> None:
    salary = Salary(salary=Decimal(900_000))

    assert salary.total == salary.net == Decimal(900_000)
    assert salary.deductions == 0
    assert salary.compensation_ratio == 0


def test_ratio_is_zero_when_nothing_is_paid() -> None:
    assert Salary(salary=Decimal(0)).compensation_ratio == 0


def test_ratio_is_one_when_only_compensation_is_paid() -> None:
    assert Salary(salary=Decimal(0), compensation=Decimal(10)).compensation_ratio == 1


def test_to_dict_follows_the_field_order() -> None:
    data = to_dict(Salary(salary=Decimal(1), compensation=Decimal(2)))

    assert list(data) == [field.key for field in FIELDS]
    assert data["total"] == Decimal(3)


def test_is_immutable() -> None:
    salary = Salary(salary=Decimal(1))

    with pytest.raises(FrozenInstanceError):
        salary.salary = Decimal(2)  # type: ignore[misc]
