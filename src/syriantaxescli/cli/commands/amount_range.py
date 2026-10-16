from decimal import Decimal
from typing import Annotated

import typer
from syriantaxes import SalaryBelowMinimumError
from typer_di import Depends, TyperDI
from typer_swissknife import command

from syriantaxescli.cli import parsers
from syriantaxescli.cli.dependencies.ctx import ContextDI
from syriantaxescli.cli.dependencies.inputs import CompensationShareDI
from syriantaxescli.cli.dependencies.output import OutputOptionsDI
from syriantaxescli.cli.dependencies.rules import TaxRulesDI
from syriantaxescli.cli.dependencies.settings import SettingsDI
from syriantaxescli.core import amount_range, calculate_net_range

app = TyperDI()

StartArg = Annotated[
    Decimal,
    typer.Argument(parser=parsers.amount, help="First net total.", show_default=False),
]
StopArg = Annotated[
    Decimal | None,
    typer.Argument(
        parser=parsers.amount,
        help="Last net total (inclusive).",
        show_default="START x range.stop_factor",
    ),
]
StepArg = Annotated[
    Decimal | None,
    typer.Argument(
        parser=parsers.amount,
        help="Gap between net totals.",
        show_default="START / range.step_divisor",
    ),
]


def _get_nets(
    settings: SettingsDI, start: StartArg, stop: StopArg = None, step: StepArg = None
) -> list[Decimal]:
    try:
        return amount_range(
            start,
            stop,
            step,
            max_size=settings.range.max_size,
            stop_factor=settings.range.stop_factor,
            step_divisor=settings.range.step_divisor,
        )
    except ValueError as e:
        raise typer.BadParameter(str(e)) from e


NetsDI = Annotated[list[Decimal], Depends(_get_nets)]


@command(app, name="range", aliases=("ar", "r"), ascii_name="range")
def range_cmd(
    ctx: ContextDI,
    rules: TaxRulesDI,
    output_options: OutputOptionsDI,
    nets: NetsDI,
    compensation_share: CompensationShareDI,
) -> None:
    """Build a salary scale: the gross salary and compensations for a range of net totals.

    Example: sytax range 1000000 2000000 100000 -r 0.25 -e scale.xlsx
    """
    try:
        salaries = calculate_net_range(rules, nets, compensation_share)
    except SalaryBelowMinimumError as e:
        raise typer.BadParameter(str(e), param_hint="'START'") from e
    except ValueError as e:
        raise typer.BadParameter(str(e)) from e

    ctx.show(salaries, title="Salary Scale", options=output_options)
