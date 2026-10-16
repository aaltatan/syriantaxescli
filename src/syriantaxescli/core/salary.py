from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal
from typing import Final


@dataclass(frozen=True, kw_only=True)
class Salary:
    """A gross salary and compensation, with everything deducted from them."""

    salary: Decimal
    compensation: Decimal = Decimal(0)
    social_security: Decimal = Decimal(0)
    salary_tax: Decimal = Decimal(0)
    compensation_tax: Decimal = Decimal(0)

    @property
    def total(self) -> Decimal:
        return self.salary + self.compensation

    @property
    def taxes(self) -> Decimal:
        return self.salary_tax + self.compensation_tax

    @property
    def deductions(self) -> Decimal:
        return self.social_security + self.taxes

    @property
    def net(self) -> Decimal:
        return self.total - self.deductions

    @property
    def compensation_ratio(self) -> Decimal:
        """The share of the total paid as compensation; 0 when the total is 0."""
        if not self.total:
            return Decimal(0)

        return self.compensation / self.total


@dataclass(frozen=True)
class Field:
    key: str
    header: str
    getter: Callable[[Salary], Decimal]


FIELDS: Final = (
    Field("salary", "Salary", lambda s: s.salary),
    Field("compensation", "Compensation", lambda s: s.compensation),
    Field("total", "Total", lambda s: s.total),
    Field("social_security", "Social Security", lambda s: s.social_security),
    Field("salary_tax", "Salary Tax", lambda s: s.salary_tax),
    Field("compensation_tax", "Compensation Tax", lambda s: s.compensation_tax),
    Field("taxes", "Taxes", lambda s: s.taxes),
    Field("deductions", "Deductions", lambda s: s.deductions),
    Field("net", "Net", lambda s: s.net),
    Field("compensation_ratio", "Compensation Ratio", lambda s: s.compensation_ratio),
)


def to_dict(salary: Salary) -> dict[str, Decimal]:
    return {field.key: field.getter(salary) for field in FIELDS}
