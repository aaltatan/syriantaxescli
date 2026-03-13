from dataclasses import dataclass

from rich.console import Console
from syriantaxes import Bracket, Rounder, RoundingMethod, SocialSecurity
from typer_di import Depends

from .options import (
    BracketMaxesOpt,
    BracketMinsOpt,
    BracketRatesOpt,
    CompensationsRateOpt,
    FixedTaxRateOpt,
    GrossCompensationsArg,
    GrossSalaryArg,
    MinAllowedSalaryOpt,
    MinSsAllowedSalaryOpt,
    SocialSecuritySalaryOpt,
    SsDeductionRateOpt,
    SsRoundingMethodOpt,
    SsRoundToNearestOpt,
    StartAmountRangeArg,
    StepAmountRangeArg,
    StopAmountRangeArg,
    TargetSalaryArg,
    TaxesRoundingMethodOpt,
    TaxesRoundToNearestOpt,
)

BRACKETS_MINS: list[float] = [0, 837000, 850000, 1100000]
BRACKETS_MAXS: list[float] = [837000, 850000, 1100000, 25000000]
BRACKETS_RATES = [0, 0.11, 0.13, 0.15]

TAXES_ROUNDING_METHOD = RoundingMethod.HALF_UP
TAXES_ROUND_TO_NEAREST = 100

SS_ROUNDING_METHOD = RoundingMethod.HALF_UP
SS_ROUND_TO_NEAREST = 1

FIXED_TAX_RATE = 0.05
MIN_ALLOWED_SALARY = 837_000

MIN_SS_ALLOWED_SALARY = 750_000
DEFAULT_SS_DEDUCTION_RATE = 0.07


@dataclass
class Net:
    target_salary: TargetSalaryArg
    compensations_rate: CompensationsRateOpt


@dataclass
class Gross:
    salary: GrossSalaryArg
    compensations: GrossCompensationsArg = 0
    ss_salary: SocialSecuritySalaryOpt = None


@dataclass
class Config:
    min_allowed_salary: MinAllowedSalaryOpt = MIN_ALLOWED_SALARY
    fixed_tax_rate: FixedTaxRateOpt = FIXED_TAX_RATE


@dataclass
class AmountRange:
    compensations_rate: CompensationsRateOpt
    start: StartAmountRangeArg
    stop: StopAmountRangeArg = None
    step: StepAmountRangeArg = None


def get_brackets(
    mins: BracketMinsOpt = BRACKETS_MINS,
    maxes: BracketMaxesOpt = BRACKETS_MAXS,
    rates: BracketRatesOpt = BRACKETS_RATES,
) -> list[Bracket]:
    return [Bracket(mins, maxs, rate) for mins, maxs, rate in zip(mins, maxes, rates, strict=True)]


def get_taxes_rounder(
    method: TaxesRoundingMethodOpt = TAXES_ROUNDING_METHOD,
    to_nearest: TaxesRoundToNearestOpt = TAXES_ROUND_TO_NEAREST,
) -> Rounder:
    return Rounder(method, to_nearest)


def get_ss_rounder(
    ss_rounding_method: SsRoundingMethodOpt = SS_ROUNDING_METHOD,
    ss_rounding_to_nearest: SsRoundToNearestOpt = SS_ROUND_TO_NEAREST,
) -> Rounder:
    return Rounder(ss_rounding_method, ss_rounding_to_nearest)


def get_ss_obj(
    min_salary: MinSsAllowedSalaryOpt = MIN_SS_ALLOWED_SALARY,
    deduction_rate: SsDeductionRateOpt = DEFAULT_SS_DEDUCTION_RATE,
    rounder: Rounder = Depends(get_ss_rounder),  # noqa: B008
) -> SocialSecurity:
    return SocialSecurity(min_salary, deduction_rate, rounder)


def get_console() -> Console:
    return Console()
