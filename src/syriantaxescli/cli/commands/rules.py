import json
from decimal import Decimal
from itertools import pairwise
from typing import Any

from rich.console import Group
from rich.table import Table
from syriantaxes import SocialSecurity, TaxRules
from typer_di import TyperDI
from typer_swissknife import command

from syriantaxescli.cli.dependencies.ctx import ContextDI
from syriantaxescli.cli.dependencies.output import OutputOpt
from syriantaxescli.cli.dependencies.settings import SettingsDI
from syriantaxescli.cli.serializers import format_amount, format_ratio, to_json_number
from syriantaxescli.core.settings import Output

app = TyperDI()


def _bands(rules: TaxRules) -> list[tuple[Decimal, Decimal | None, Decimal]]:
    """Return each bracket as (lower, upper, rate); the last one has no upper."""
    lowers = [bracket.lower for bracket in rules.brackets]
    uppers: list[Decimal | None] = [upper for _, upper in pairwise(lowers)]
    return [
        (bracket.lower, upper, bracket.rate)
        for bracket, upper in zip(rules.brackets, [*uppers, None], strict=True)
    ]


def _render_table(rules: TaxRules, social_security: SocialSecurity) -> Group:
    brackets = Table(title="Salary Tax Brackets")
    brackets.add_column("#", justify="right")
    brackets.add_column("From", justify="right")
    brackets.add_column("To", justify="right")
    brackets.add_column("Rate", justify="right", style="cyan")

    for index, (lower, upper, rate) in enumerate(_bands(rules), start=1):
        to = "and above" if upper is None else format_amount(upper)
        brackets.add_row(str(index), format_amount(lower), to, format_ratio(rate))

    settings = Table(title="Settings")
    settings.add_column("Setting")
    settings.add_column("Value", justify="right", style="cyan")
    settings.add_row("Minimum salary", format_amount(rules.min_salary))
    settings.add_row("Compensation tax rate", format_ratio(rules.compensation_tax_rate))
    settings.add_row("Tax rounding", str(rules.rounding))
    settings.add_row("Social security", "on" if rules.social_security else "off")
    settings.add_row("Social security rate", format_ratio(social_security.rate))
    settings.add_row("Minimum insured salary", format_amount(social_security.min_salary))
    settings.add_row("Social security rounding", str(social_security.rounding))

    return Group(brackets, settings)


def _to_dict(rules: TaxRules, social_security: SocialSecurity) -> dict[str, Any]:
    return {
        "brackets": [
            {
                "lower": to_json_number(lower),
                "upper": None if upper is None else to_json_number(upper),
                "rate": to_json_number(rate),
            }
            for lower, upper, rate in _bands(rules)
        ],
        "min_salary": to_json_number(rules.min_salary),
        "compensation_tax_rate": to_json_number(rules.compensation_tax_rate),
        "rounding": str(rules.rounding),
        "social_security": {
            "enabled": rules.social_security is not None,
            "rate": to_json_number(social_security.rate),
            "min_salary": to_json_number(social_security.min_salary),
            "rounding": str(social_security.rounding),
        },
    }


@command(app, name="rules", ascii_name="rules")
def rules_cmd(ctx: ContextDI, settings: SettingsDI, output: OutputOpt = None) -> None:
    """Show the tax rules in use, after config files, environment variables and options."""
    rules = settings.tax.to_rules()
    social_security = settings.tax.social_security.to_rules()

    if (output or settings.output.format) is Output.JSON:
        indent = settings.output.json_indent or None
        ctx.echo(json.dumps(_to_dict(rules, social_security), indent=indent))
    else:
        ctx.print(_render_table(rules, social_security))
