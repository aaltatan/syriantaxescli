"""Run every `sytax` command in the docs and check the output they show.

- In ```console blocks, a `$ sytax ...` line is a command and the lines under it are its
  output: each one must appear in the real output, in order, ignoring the spaces and the
  edge of an error panel around it. A line holding `...` stands for any lines.
- In ```bash blocks, every `sytax ...` line must succeed.

The commands of one block run in order, in one copy of `examples/`. conftest keeps the user
config and `SYRIANTAXES_*` variables out, so the preset alone decides the results.
"""

import re
import shlex
import shutil
import textwrap
from pathlib import Path

import pytest
from typer.testing import CliRunner

from syriantaxescli.main import app

ROOT = Path(__file__).parent.parent

PAGES = sorted((ROOT / "docs").rglob("*.md"))

# docs indent code blocks inside tabs and admonitions, so the fence may be indented
FENCE = re.compile(r"^([ \t]*)```(console|bash)\n(.*?)^\1```", re.DOTALL | re.MULTILINE)

type Step = tuple[list[str], list[str] | None]
"""A command's arguments, and the output lines it must show (None: it must succeed)."""


def console_steps(block: str) -> list[Step]:
    steps: list[Step] = []

    for line in block.splitlines():
        if line.startswith("$ sytax "):
            steps.append((shlex.split(line.removeprefix("$ sytax ")), []))

        elif steps and (expected := steps[-1][1]) is not None and line.strip():
            expected.append(line.rstrip())

    return steps


def bash_steps(block: str) -> list[Step]:
    return [
        (shlex.split(line, comments=True)[1:], None)
        for line in block.splitlines()
        if line.startswith("sytax ")
    ]


BLOCKS = [
    (f"{page.relative_to(ROOT / 'docs').as_posix()}:{number}", steps)
    for page in PAGES
    for number, (_, kind, block) in enumerate(FENCE.findall(page.read_text(encoding="utf-8")), 1)
    if (steps := (console_steps if kind == "console" else bash_steps)(textwrap.dedent(block)))
]


def normalize(line: str) -> str:
    """Drop the spaces and the edge of an error panel around a line, its width varies."""
    return line.strip().strip("│").strip()


def contains_in_order(output: list[str], expected: list[str]) -> bool:
    """Whether every expected line is in `output`, in order; `...` lines match anything."""
    lines = iter(normalize(line) for line in output)

    return all("..." in want or any(line == normalize(want) for line in lines) for want in expected)


def test_the_docs_have_commands() -> None:
    assert sum(len(steps) for _, steps in BLOCKS) > 60


@pytest.mark.parametrize("steps", [steps for _, steps in BLOCKS], ids=[i for i, _ in BLOCKS])
def test_docs_block(steps: list[Step], work_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # conftest's _isolate_config already cleared SYRIANTAXES_* and the user config
    shutil.copytree(ROOT / "examples", work_dir, dirs_exist_ok=True)

    monkeypatch.setenv("COLUMNS", "140")

    for args, expected in steps:
        result = CliRunner().invoke(app, args)
        command = shlex.join(["sytax", *args])

        if expected is None:
            assert result.exit_code == 0, f"{command}\n{result.output}"

            continue

        output = [line.rstrip() for line in result.output.splitlines()]

        assert contains_in_order(output, expected), f"{command}\n{result.output}"


def test_the_presets_page_shows_the_bundled_preset() -> None:
    """docs/guide/presets.md quotes syria-2024.toml whole; a law change must update both."""
    page = (ROOT / "docs" / "guide" / "presets.md").read_text(encoding="utf-8")
    shown = re.search(r"## The preset `syria-2024`\n\n```toml\n(.*?)```", page, re.DOTALL)
    preset = ROOT / "src" / "syriantaxescli" / "presets" / "syria-2024.toml"

    assert shown is not None
    assert shown.group(1).splitlines() == preset.read_text(encoding="utf-8").splitlines()
