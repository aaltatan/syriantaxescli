"""Every setting the app uses, with no defaults: the values come from presets and config."""

from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Self

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, model_validator
from syriantaxes import SocialSecurity, TaxRules

from .rounding import RoundingMethod, RoundingRule
from .services import make_brackets


class Output(StrEnum):
    TABLE = "table"
    JSON = "json"


def _clean_number(value: object) -> object:
    """Accept `1,000,000` and `1_000_000` from config files and environment variables."""
    if isinstance(value, str):
        return value.strip().replace(",", "").replace("_", "")
    return value


def _clean_method(value: object) -> object:
    """Accept `half_up`, `HALF_UP` and `ROUND_HALF_UP` alike."""
    if isinstance(value, str):
        method = value.strip().upper()
        return method if method.startswith("ROUND_") else f"ROUND_{method}"
    return value


Number = Annotated[Decimal, BeforeValidator(_clean_number)]
Amount = Annotated[Decimal, BeforeValidator(_clean_number), Field(ge=0)]
Rate = Annotated[Decimal, BeforeValidator(_clean_number), Field(ge=0, lt=1)]
Share = Annotated[Decimal, BeforeValidator(_clean_number), Field(ge=0, le=1)]
Method = Annotated[RoundingMethod, BeforeValidator(_clean_method)]


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class RoundingSettings(_Model):
    method: Method
    step: Annotated[Decimal, BeforeValidator(_clean_number), Field(gt=0)]

    def rule(self) -> RoundingRule:
        return RoundingRule(self.method, self.step)


class BracketSettings(_Model):
    lower: Amount
    rate: Rate


class SocialSecuritySettings(_Model):
    enabled: bool
    rate: Rate
    min_salary: Amount
    rounding: RoundingSettings

    def to_rules(self) -> SocialSecurity:
        return SocialSecurity(
            rate=self.rate, min_salary=self.min_salary, rounding=self.rounding.rule()
        )


class TaxSettings(_Model):
    brackets: tuple[BracketSettings, ...]
    min_salary: Amount
    compensation_tax_rate: Rate
    rounding: RoundingSettings
    social_security: SocialSecuritySettings

    @model_validator(mode="after")
    def _check_rules(self) -> Self:
        self.to_rules()  # syriantaxes checks the brackets' order
        return self

    def to_rules(self, *, social_security: bool | None = None) -> TaxRules:
        """Build the syriantaxes rules; `social_security` overrides whether it is deducted."""
        enabled = self.social_security.enabled if social_security is None else social_security

        return TaxRules(
            brackets=make_brackets(
                [bracket.lower for bracket in self.brackets],
                [bracket.rate for bracket in self.brackets],
            ),
            min_salary=self.min_salary,
            compensation_tax_rate=self.compensation_tax_rate,
            social_security=self.social_security.to_rules() if enabled else None,
            rounding=self.rounding.rule(),
        )


class NetSettings(_Model):
    compensation_share: Share


class OutputSettings(_Model):
    format: Output
    json_indent: Annotated[int, Field(ge=0)]


class RangeSettings(_Model):
    max_size: Annotated[int, Field(gt=0)]
    stop_factor: Annotated[Number, Field(gt=0)]
    step_divisor: Annotated[Number, Field(gt=0)]


class Settings(_Model):
    preset: str
    tax: TaxSettings
    net: NetSettings
    output: OutputSettings
    range: RangeSettings
