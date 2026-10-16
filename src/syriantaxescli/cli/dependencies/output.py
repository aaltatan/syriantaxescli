from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Final

import typer
from typer_di import Depends

from syriantaxescli.cli.exporters import ExtensionNotSupportedError, exporters, get_extension
from syriantaxescli.core.settings import Output

from .settings import SettingsDI

OUTPUT_PANEL: Final = "Output"

OutputOpt = Annotated[
    Output | None,
    typer.Option(
        "-o",
        "--output",
        case_sensitive=False,
        help="How to print the results.",
        show_default="output.format",
        rich_help_panel=OUTPUT_PANEL,
    ),
]


@dataclass
class OutputFlags:
    output: OutputOpt = None

    json_indent: Annotated[
        int | None,
        typer.Option(
            "--json-indent",
            min=0,
            help="Indentation of JSON output; 0 prints it on one line.",
            show_default="output.json_indent",
            rich_help_panel=OUTPUT_PANEL,
        ),
    ] = None

    export_path: Annotated[
        Path | None,
        typer.Option(
            "-e",
            "--export",
            "--write-path",
            dir_okay=False,
            resolve_path=True,
            help="Write the results to a .xlsx, .csv, .json or .jsonl file instead of printing.",
            rich_help_panel=OUTPUT_PANEL,
        ),
    ] = None

    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite",
            help="Replace the export file if it already exists.",
            rich_help_panel=OUTPUT_PANEL,
        ),
    ] = False

    def __post_init__(self) -> None:
        path = self.export_path

        if path is None:
            return

        hint = "'-e' / '--export'"

        try:
            exporters[get_extension(path)]
        except ExtensionNotSupportedError as e:
            raise typer.BadParameter(str(e), param_hint=hint) from e

        if not path.parent.is_dir():
            message = f"The folder '{path.parent}' does not exist."
            raise typer.BadParameter(message, param_hint=hint)

        if path.exists() and not self.overwrite:
            message = f"The file '{path}' already exists; pass --overwrite to replace it."
            raise typer.BadParameter(message, param_hint=hint)


@dataclass(frozen=True)
class OutputOptions:
    """The output flags, with unset ones filled in from the settings."""

    format: Output
    json_indent: int
    export_path: Path | None


def _get_output_options(
    flags: Annotated[OutputFlags, Depends(OutputFlags)], settings: SettingsDI
) -> OutputOptions:
    return OutputOptions(
        format=settings.output.format if flags.output is None else flags.output,
        json_indent=settings.output.json_indent if flags.json_indent is None else flags.json_indent,
        export_path=flags.export_path,
    )


OutputOptionsDI = Annotated[OutputOptions, Depends(_get_output_options)]
