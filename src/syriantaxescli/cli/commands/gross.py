from decimal import Decimal
from typing import Annotated

import typer
from typer_di import TyperDI
from typer_swissknife import command

from syriantaxescli.cli import parsers
from syriantaxescli.cli.dependencies.ctx import ContextDI
from syriantaxescli.cli.dependencies.output import OutputOptionsDI
from syriantaxescli.cli.dependencies.settings import SettingsDI
from syriantaxescli.core import calculate_gross

app = TyperDI()

SalaryArg = Annotated[
    Decimal,
    typer.Argument(parser=parsers.amount, help="Gross salary.", show_default=False),
]
CompensationArg = Annotated[
    Decimal,
    typer.Argument(parser=parsers.amount, help="Gross compensations."),
]
InsuredSalaryOpt = Annotated[
    Decimal | None,
    typer.Option(
        "-i",
        "--insured-salary",
        parser=parsers.amount,
        help="Salary that social security is based on. Implies --ss.",
        show_default="the gross salary",
    ),
]


@command(app, name="gross", aliases=("g",), ascii_name="gross")
def gross_cmd(  # noqa: PLR0913
    ctx: ContextDI,
    settings: SettingsDI,
    output_options: OutputOptionsDI,
    salary: SalaryArg,
    compensation: CompensationArg = Decimal(0),
    insured_salary: InsuredSalaryOpt = None,
) -> None:
    """Calculate the taxes and net of a gross salary and compensations.

    Example: sytax gross 1000000 100000
    """
    # An insured salary only makes sense with social security, so it turns it on.
    rules = settings.tax.to_rules(social_security=True if insured_salary is not None else None)

    try:
        result = calculate_gross(rules, salary, compensation, insured_salary=insured_salary)
    except ValueError as e:
        raise typer.BadParameter(str(e)) from e

    ctx.show(result, title="Gross Salary", options=output_options)
