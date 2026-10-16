import io
import sys
from collections.abc import Iterable
from typing import IO, Any

from typer_di import TyperDI
from typer_swissknife import add_typer, get_ascii_help_text

from syriantaxescli.cli.callback import callback
from syriantaxescli.cli.commands import amount_range, config, gross, net, rules


def create_app() -> TyperDI:
    app = TyperDI(
        callback=callback,
        help=get_ascii_help_text(
            "SyTax",
            body="Calculate Syrian salary and compensation taxes.",
        ),
        no_args_is_help=True,
    )

    add_typer(app, gross.app)
    add_typer(app, net.app)
    add_typer(app, amount_range.app)
    add_typer(app, rules.app)
    add_typer(
        app,
        config.app,
        name="config",
        aliases=("cfg",),
        ascii_name="config",
        no_args_is_help=True,
    )

    return app


app = create_app()


def use_utf8(streams: Iterable[IO[Any]]) -> None:
    """Write UTF-8 so the ASCII-art banners don't crash when output is piped on Windows."""
    for stream in streams:
        if isinstance(stream, io.TextIOWrapper) and stream.encoding.lower() != "utf-8":
            stream.reconfigure(encoding="utf-8")


def main() -> None:
    use_utf8([sys.stdout, sys.stderr])
    app()
