from pathlib import Path
from typing import Annotated

import typer
from syriantaxes import RoundingMethod

from .callbacks import (
    amount_range_start_callback,
    amount_range_step_callback,
    amount_range_stop_callback,
    ss_salary_callback,
    write_path_callback,
)

CompensationsRateOpt = Annotated[
    float,
    typer.Option(
        "-r",
        "--compensations-rate",
    ),
]

StartAmountRangeArg = Annotated[float, typer.Argument(callback=amount_range_start_callback)]
StopAmountRangeArg = Annotated[float | None, typer.Argument(callback=amount_range_stop_callback)]
StepAmountRangeArg = Annotated[float | None, typer.Argument(callback=amount_range_step_callback)]

BracketMinsOpt = Annotated[
    list[float],
    typer.Option(
        "--brackets-mins",
        envvar="SYRIANTAXES_BRACKET_TAX_MINS",
        rich_help_panel="Brackets",
    ),
]
BracketMaxesOpt = Annotated[
    list[float],
    typer.Option(
        "--brackets-maxs",
        envvar="SYRIANTAXES_BRACKET_TAX_MAXS",
        rich_help_panel="Brackets",
    ),
]
BracketRatesOpt = Annotated[
    list[float],
    typer.Option(
        "--brackets-rates",
        envvar="SYRIANTAXES_BRACKET_TAX_RATES",
        rich_help_panel="Brackets",
    ),
]


TaxesRoundingMethodOpt = Annotated[
    RoundingMethod,
    typer.Option(
        "--taxes-rounding-method",
        envvar="SYRIANTAXES_TAXES_ROUNDING_METHOD",
        rich_help_panel="Taxes Rounding",
    ),
]
TaxesRoundToNearestOpt = Annotated[
    float,
    typer.Option(
        "--taxes-round-to-nearest",
        envvar="SYRIANTAXES_TAXES_ROUND_TO_NEAREST",
        rich_help_panel="Taxes Rounding",
    ),
]


MinAllowedSalaryOpt = Annotated[
    float,
    typer.Option(
        "--min-allowed-salary",
        envvar="SYRIANTAXES_MIN_ALLOWED_SALARY",
    ),
]
FixedTaxRateOpt = Annotated[
    float,
    typer.Option(
        "--fixed-tax-rate",
        envvar="SYRIANTAXES_FIXED_TAX_RATE",
    ),
]

WritePathOpt = Annotated[
    Path | None,
    typer.Option(
        "-e",
        "--write-path",
        help="Path to the output file",
        exists=False,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
        callback=write_path_callback,
    ),
]


GrossSalaryArg = Annotated[float, typer.Argument()]
GrossCompensationsArg = Annotated[float, typer.Argument()]
SocialSecuritySalaryOpt = Annotated[float | None, typer.Argument(callback=ss_salary_callback)]

TargetSalaryArg = Annotated[float, typer.Argument()]


SsRoundingMethodOpt = Annotated[
    RoundingMethod,
    typer.Option(
        "--ss-rounding-method",
        envvar="SYRIANTAXES_SS_ROUNDING_METHOD",
        rich_help_panel="Social Security",
    ),
]

SsRoundToNearestOpt = Annotated[
    float,
    typer.Option(
        "--ss-round-to-nearest",
        envvar="SYRIANTAXES_SS_ROUND_TO_NEAREST",
        rich_help_panel="Social Security",
    ),
]

MinSsAllowedSalaryOpt = Annotated[
    float,
    typer.Option(
        "--min-ss-allowed-salary",
        envvar="SYRIANTAXES_MIN_SS_ALLOWED_SALARY",
        rich_help_panel="Social Security",
    ),
]

SsDeductionRateOpt = Annotated[
    float,
    typer.Option(
        "--ss-deduction-rate",
        envvar="SYRIANTAXES_SS_DEDUCTION_RATE",
        rich_help_panel="Social Security",
    ),
]
