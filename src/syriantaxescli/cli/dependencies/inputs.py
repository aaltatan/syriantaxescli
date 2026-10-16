from decimal import Decimal
from typing import Annotated

from typer_di import Depends

from syriantaxescli.cli.options import CompensationShareOpt

from .settings import SettingsDI


def _get_compensation_share(
    settings: SettingsDI, compensation_share: CompensationShareOpt = None
) -> Decimal:
    if compensation_share is None:
        return settings.net.compensation_share
    return compensation_share


CompensationShareDI = Annotated[Decimal, Depends(_get_compensation_share)]
