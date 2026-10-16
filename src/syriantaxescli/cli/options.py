"""Shared options. They default to None: unset options leave the settings alone."""

from decimal import Decimal
from pathlib import Path
from typing import Annotated, Final

import typer

from syriantaxescli.core import RoundingMethod

from . import parsers

CONFIG_PANEL: Final = "Configuration"
RULES_PANEL: Final = "Tax Rules"
SS_PANEL: Final = "Social Security"


# --------------------
# Configuration
# --------------------

PresetOpt = Annotated[
    str | None,
    typer.Option(
        "--preset",
        help="Tax law preset to start from; see `sytax config presets`. (env: SYRIANTAXES_PRESET)",
        rich_help_panel=CONFIG_PANEL,
    ),
]
ConfigPathOpt = Annotated[
    Path | None,
    typer.Option(
        "--config",
        exists=True,
        dir_okay=False,
        help="Extra config file, on top of the user and project ones. (env: SYRIANTAXES_CONFIG)",
        rich_help_panel=CONFIG_PANEL,
    ),
]
SetOpt = Annotated[
    list[str] | None,
    typer.Option(
        "-s",
        "--set",
        metavar="KEY=VALUE",
        help="Override any setting, e.g. -s tax.min_salary=900000. Repeatable.",
        rich_help_panel=CONFIG_PANEL,
    ),
]


# --------------------
# Tax rules
# --------------------

BracketLowersOpt = Annotated[
    list[Decimal] | None,
    typer.Option(
        "--brackets-mins",
        parser=parsers.amount,
        help=(
            "Lower bound of each bracket; repeat once per bracket, with --brackets-rates."
            " (env: SYRIANTAXES_BRACKET_TAX_MINS)"
        ),
        rich_help_panel=RULES_PANEL,
    ),
]
BracketRatesOpt = Annotated[
    list[Decimal] | None,
    typer.Option(
        "--brackets-rates",
        parser=parsers.rate,
        help=(
            "Tax rate of each bracket, in the same order as --brackets-mins."
            " (env: SYRIANTAXES_BRACKET_TAX_RATES)"
        ),
        rich_help_panel=RULES_PANEL,
    ),
]
MinSalaryOpt = Annotated[
    Decimal | None,
    typer.Option(
        "--min-allowed-salary",
        parser=parsers.amount,
        help=(
            "Minimum salary; a net target below it can't be calculated."
            " (env: SYRIANTAXES_MIN_ALLOWED_SALARY)"
        ),
        rich_help_panel=RULES_PANEL,
    ),
]
CompensationTaxRateOpt = Annotated[
    Decimal | None,
    typer.Option(
        "--fixed-tax-rate",
        parser=parsers.rate,
        help="Flat tax rate on compensations. (env: SYRIANTAXES_FIXED_TAX_RATE)",
        rich_help_panel=RULES_PANEL,
    ),
]
TaxRoundingMethodOpt = Annotated[
    RoundingMethod | None,
    typer.Option(
        "--taxes-rounding-method",
        case_sensitive=False,
        metavar="METHOD",
        help=(
            "How taxes are rounded, e.g. ROUND_HALF_UP or ROUND_CEILING."
            " (env: SYRIANTAXES_TAXES_ROUNDING_METHOD)"
        ),
        rich_help_panel=RULES_PANEL,
    ),
]
TaxRoundToOpt = Annotated[
    Decimal | None,
    typer.Option(
        "--taxes-round-to-nearest",
        parser=parsers.number,
        help=(
            "Taxes are rounded to a multiple of this amount."
            " (env: SYRIANTAXES_TAXES_ROUND_TO_NEAREST)"
        ),
        rich_help_panel=RULES_PANEL,
    ),
]


# --------------------
# Social security
# --------------------

SsEnabledOpt = Annotated[
    bool | None,
    typer.Option(
        "--ss/--no-ss",
        help=(
            "Deduct social security from the salary before taxing it. (env: SYRIANTAXES_SS_ENABLED)"
        ),
        rich_help_panel=SS_PANEL,
        show_default=False,
    ),
]
SsRateOpt = Annotated[
    Decimal | None,
    typer.Option(
        "--ss-deduction-rate",
        parser=parsers.rate,
        help="Social security deduction rate. (env: SYRIANTAXES_SS_DEDUCTION_RATE)",
        rich_help_panel=SS_PANEL,
    ),
]
SsMinSalaryOpt = Annotated[
    Decimal | None,
    typer.Option(
        "--min-ss-allowed-salary",
        parser=parsers.amount,
        help="Minimum insured salary. (env: SYRIANTAXES_MIN_SS_ALLOWED_SALARY)",
        rich_help_panel=SS_PANEL,
    ),
]
SsRoundingMethodOpt = Annotated[
    RoundingMethod | None,
    typer.Option(
        "--ss-rounding-method",
        case_sensitive=False,
        metavar="METHOD",
        help=(
            "How the social security deduction is rounded, e.g. ROUND_HALF_UP."
            " (env: SYRIANTAXES_SS_ROUNDING_METHOD)"
        ),
        rich_help_panel=SS_PANEL,
    ),
]
SsRoundToOpt = Annotated[
    Decimal | None,
    typer.Option(
        "--ss-round-to-nearest",
        parser=parsers.number,
        help=(
            "The social security deduction is rounded to a multiple of this amount."
            " (env: SYRIANTAXES_SS_ROUND_TO_NEAREST)"
        ),
        rich_help_panel=SS_PANEL,
    ),
]


# --------------------
# Calculation inputs
# --------------------

CompensationShareOpt = Annotated[
    Decimal | None,
    typer.Option(
        "-r",
        "--compensations-rate",
        parser=parsers.rate,
        help="Share of the net paid as compensation, from 0 to 1 (e.g. 0.25).",
        show_default="net.compensation_share",
    ),
]
