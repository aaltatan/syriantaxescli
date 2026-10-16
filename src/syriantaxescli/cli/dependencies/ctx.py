from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer
from rich.console import Console
from typer_di import Depends

from syriantaxescli.cli.exporters import exporters
from syriantaxescli.cli.renderers import render_json, render_table
from syriantaxescli.core import Salary
from syriantaxescli.core.config import LoadedSettings
from syriantaxescli.core.settings import Output

if TYPE_CHECKING:
    from .output import OutputOptions


@dataclass(frozen=True)
class ConfigLocation:
    """Where settings are looked for in this run."""

    cwd: Path
    user_dir: Path
    environ: Mapping[str, str]
    config_path: Path | None


@dataclass(frozen=True)
class ContextObject:
    console: Console
    load: Callable[[], LoadedSettings]
    location: ConfigLocation

    def print(self, *objects: object) -> None:
        self.console.print(*objects)

    def echo(self, text: str) -> None:
        """Print `text` as is: no markup, highlighting or wrapping, for machine output."""
        self.console.out(text, highlight=False)

    def show(
        self, result: Salary | Sequence[Salary], *, title: str, options: "OutputOptions"
    ) -> None:
        """Export `result` if an export file was given, else print it."""
        if options.export_path is not None:
            salaries = [result] if isinstance(result, Salary) else list(result)
            exporters.export(salaries, options.export_path)
            self.print(f"[green]Exported {len(salaries)} row(s) to {options.export_path}[/]")
            return

        if options.format is Output.JSON:
            self.echo(render_json(result, indent=options.json_indent))
        else:
            self.print(render_table(result, title=title))


def _get_context_object(ctx: typer.Context) -> ContextObject:
    return ContextObject(
        console=ctx.obj["console"], load=ctx.obj["load"], location=ctx.obj["location"]
    )


ContextDI = Annotated[ContextObject, Depends(_get_context_object)]
