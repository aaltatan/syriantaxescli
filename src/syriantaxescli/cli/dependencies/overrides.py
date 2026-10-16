"""The global tax-rule options, as a settings layer."""

from typing import Annotated

import typer
from typer_di import Depends

from syriantaxescli.cli.options import (
    BracketLowersOpt,
    BracketRatesOpt,
    CompensationTaxRateOpt,
    MinSalaryOpt,
    SsEnabledOpt,
    SsMinSalaryOpt,
    SsRateOpt,
    SsRoundingMethodOpt,
    SsRoundToOpt,
    TaxRoundingMethodOpt,
    TaxRoundToOpt,
)
from syriantaxescli.core.config import ConfigError, Layer, brackets_layer, set_path


def _get_cli_layer(  # noqa: PLR0913
    bracket_lowers: BracketLowersOpt = None,
    bracket_rates: BracketRatesOpt = None,
    min_salary: MinSalaryOpt = None,
    compensation_tax_rate: CompensationTaxRateOpt = None,
    tax_rounding_method: TaxRoundingMethodOpt = None,
    tax_round_to: TaxRoundToOpt = None,
    ss_enabled: SsEnabledOpt = None,
    ss_rate: SsRateOpt = None,
    ss_min_salary: SsMinSalaryOpt = None,
    ss_rounding_method: SsRoundingMethodOpt = None,
    ss_round_to: SsRoundToOpt = None,
) -> Layer:
    values = {
        ("tax", "min_salary"): min_salary,
        ("tax", "compensation_tax_rate"): compensation_tax_rate,
        ("tax", "rounding", "method"): tax_rounding_method,
        ("tax", "rounding", "step"): tax_round_to,
        ("tax", "social_security", "enabled"): ss_enabled,
        ("tax", "social_security", "rate"): ss_rate,
        ("tax", "social_security", "min_salary"): ss_min_salary,
        ("tax", "social_security", "rounding", "method"): ss_rounding_method,
        ("tax", "social_security", "rounding", "step"): ss_round_to,
    }

    layer: Layer = {}
    for path, value in values.items():
        if value is not None:
            set_path(layer, path, value)

    if bracket_lowers or bracket_rates:
        try:
            brackets = brackets_layer(bracket_lowers or [], bracket_rates or [])
        except ConfigError as e:
            raise typer.BadParameter(
                str(e), param_hint="'--brackets-mins' / '--brackets-rates'"
            ) from e
        set_path(layer, ("tax", "brackets"), brackets)

    return layer


CliLayerDI = Annotated[Layer, Depends(_get_cli_layer)]
