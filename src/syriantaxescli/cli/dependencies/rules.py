from typing import Annotated

from syriantaxes import TaxRules
from typer_di import Depends

from .settings import SettingsDI


def _get_tax_rules(settings: SettingsDI) -> TaxRules:
    return settings.tax.to_rules()


TaxRulesDI = Annotated[TaxRules, Depends(_get_tax_rules)]
