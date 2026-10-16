from decimal import Decimal
from typing import Annotated

import typer
from syriantaxes import SalaryBelowMinimumError
from typer_di import TyperDI
from typer_swissknife import command

from syriantaxescli.cli import parsers
from syriantaxescli.cli.dependencies.ctx import ContextDI
from syriantaxescli.cli.dependencies.inputs import CompensationShareDI
from syriantaxescli.cli.dependencies.output import OutputOptionsDI
from syriantaxescli.cli.dependencies.rules import TaxRulesDI
from syriantaxescli.core import calculate_net

app = TyperDI()

TargetArg = Annotated[
    Decimal,
    typer.Argument(parser=parsers.amount, help="Wanted net total.", show_default=False),
]


@command(app, name="net", aliases=("n",), ascii_name="net")
def net_cmd(
    ctx: ContextDI,
    rules: TaxRulesDI,
    output_options: OutputOptionsDI,
    target: TargetArg,
    compensation_share: CompensationShareDI,
) -> None:
    """Find the gross salary and compensations that pay a wanted net total.

    Example: sytax net 1500000 -r 0.25
    """
    try:
        result = calculate_net(rules, target, compensation_share)
    except SalaryBelowMinimumError as e:
        raise typer.BadParameter(str(e), param_hint="'TARGET'") from e
    except ValueError as e:
        raise typer.BadParameter(str(e)) from e

    ctx.show(result, title="Net Salary", options=output_options)
