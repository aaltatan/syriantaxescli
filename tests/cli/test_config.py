import json
import tomllib
from pathlib import Path

from syriantaxescli.core.config import default_preset
from tests.conftest import Invoke


def test_no_subcommand_shows_help(invoke: Invoke) -> None:
    result = invoke("config")

    assert "show (s)" in result.output
    assert "init" in result.output


# --------------------
# show
# --------------------


def test_show_table(invoke: Invoke) -> None:
    result = invoke("config", "show")

    assert result.exit_code == 0, result.output
    assert "tax.min_salary" in result.output
    assert "837000" in result.output
    assert "0 @ 0, 837000 @ 0.11" in result.output
    assert "ROUND_HALF_UP" in result.output
    assert "false" in result.output
    assert "Source" not in result.output


def test_show_sources(invoke: Invoke, work_dir: Path) -> None:
    (work_dir / "sytax.toml").write_text("[tax]\nmin_salary = 900000\n", encoding="utf-8")

    result = invoke("cfg", "s", "--sources")

    assert result.exit_code == 0, result.output
    assert "Source" in result.output
    assert f"preset {default_preset()}" in result.output
    assert "sytax.toml" in result.output


def test_show_json(invoke: Invoke) -> None:
    result = invoke("config", "show", "-o", "json")

    data = json.loads(result.stdout)
    assert data["tax"]["min_salary"] == 837_000
    assert data["tax"]["brackets"][1] == {"lower": 837_000, "rate": 0.11}
    assert data["output"]["format"] == "table"


def test_show_json_with_sources(invoke: Invoke) -> None:
    result = invoke("-s", "range.max_size=50", "config", "show", "-o", "json", "--sources")

    data = json.loads(result.stdout)
    assert data["settings"]["range"]["max_size"] == 50
    assert data["sources"]["range.max_size"] == "--set range.max_size=50"
    assert data["sources"]["tax.min_salary"] == f"preset {default_preset()}"


def test_show_toml_can_be_used_as_a_config_file(invoke: Invoke, work_dir: Path) -> None:
    result = invoke("config", "show", "-o", "toml")

    (work_dir / "sytax.toml").write_text(result.stdout, encoding="utf-8")
    assert tomllib.loads(result.stdout)["tax"]["min_salary"] == 837_000
    assert invoke("config", "show").exit_code == 0


def test_show_reports_broken_config(invoke: Invoke, work_dir: Path) -> None:
    (work_dir / "sytax.toml").write_text("[tax]\nmin_salry = 1\n", encoding="utf-8")

    result = invoke("config", "show")

    assert result.exit_code == 2
    assert "tax.min_salry: unknown setting" in result.output


def test_broken_config_does_not_break_help(invoke: Invoke, work_dir: Path) -> None:
    (work_dir / "sytax.toml").write_text("not toml [", encoding="utf-8")

    assert invoke("gross", "--help").exit_code == 0
    assert invoke("config", "path").exit_code == 0
    assert invoke("gross", "1").exit_code == 2


# --------------------
# path
# --------------------


def test_path(invoke: Invoke) -> None:
    result = invoke("config", "path")

    assert result.exit_code == 0, result.output
    assert "no sytax.toml in" in result.output
    assert "not given" in result.output
    assert "yes" not in result.output


def test_path_marks_found_files(invoke: Invoke, work_dir: Path, user_dir: Path) -> None:
    (work_dir / "sytax.toml").write_text("", encoding="utf-8")
    (user_dir / "config.toml").write_text("", encoding="utf-8")
    extra = work_dir / "extra.toml"
    extra.write_text("", encoding="utf-8")

    result = invoke("--config", str(extra), "config", "p")

    assert result.exit_code == 0, result.output
    assert result.output.count("yes") == 3


# --------------------
# init
# --------------------


def test_init_project_file(invoke: Invoke, work_dir: Path) -> None:
    result = invoke("config", "init")

    path = work_dir / "sytax.toml"
    assert result.exit_code == 0, result.output
    assert "Created" in result.output
    text = path.read_text(encoding="utf-8")
    assert f'preset = "{default_preset()}"' in text
    assert "\n[tax]\n# min_salary = 837000\n" in text
    assert "# [[tax.brackets]]" in text
    # Only the preset is set; everything else stays commented out.
    assert tomllib.loads(text) == {
        "preset": default_preset(),
        "tax": {"rounding": {}, "social_security": {"rounding": {}}},
        "net": {},
        "output": {},
        "range": {},
    }


def test_init_file_works_unchanged_and_after_uncommenting(invoke: Invoke, work_dir: Path) -> None:
    invoke("config", "init")
    path = work_dir / "sytax.toml"
    assert invoke("gross", "1000000").exit_code == 0

    path.write_text(
        path.read_text(encoding="utf-8").replace("# min_salary = 837000", "min_salary = 900000"),
        encoding="utf-8",
    )

    result = invoke("config", "show", "-o", "json")
    assert json.loads(result.stdout)["tax"]["min_salary"] == 900_000


def test_init_user_file(invoke: Invoke, user_dir: Path) -> None:
    result = invoke("config", "init", "--user")

    assert result.exit_code == 0, result.output
    assert (user_dir / "config.toml").is_file()


def test_init_creates_the_user_folder(invoke: Invoke, user_dir: Path) -> None:
    user_dir.rmdir()

    assert invoke("config", "init", "--user").exit_code == 0
    assert (user_dir / "config.toml").is_file()


def test_init_refuses_to_overwrite(invoke: Invoke, work_dir: Path) -> None:
    path = work_dir / "sytax.toml"
    path.write_text("keep", encoding="utf-8")

    result = invoke("config", "init")

    assert result.exit_code == 2
    assert "already exists; pass --force" in result.output
    assert path.read_text(encoding="utf-8") == "keep"


def test_init_force(invoke: Invoke, work_dir: Path) -> None:
    (work_dir / "sytax.toml").write_text("keep", encoding="utf-8")

    assert invoke("config", "init", "--force").exit_code == 0
    assert "preset" in (work_dir / "sytax.toml").read_text(encoding="utf-8")


def test_init_unknown_preset(invoke: Invoke) -> None:
    result = invoke("config", "init", "--preset", "syria-1990")

    assert result.exit_code == 2
    assert "unknown preset" in result.output


def test_init_with_preset(invoke: Invoke) -> None:
    assert invoke("config", "init", "--preset", default_preset()).exit_code == 0


# --------------------
# presets
# --------------------


def test_presets(invoke: Invoke) -> None:
    result = invoke("config", "presets")

    assert result.exit_code == 0
    assert default_preset() in result.output
    assert "yes" in result.output


# --------------------
# Global options
# --------------------


def test_preset_option(invoke: Invoke) -> None:
    result = invoke("--preset", default_preset(), "config", "show", "--sources")

    assert result.exit_code == 0
    assert "command-line options" in result.output


def test_unknown_preset_option(invoke: Invoke) -> None:
    result = invoke("--preset", "syria-1990", "gross", "1000000")

    assert result.exit_code == 2
    assert "unknown preset 'syria-1990'" in result.output


def test_set_option(invoke: Invoke) -> None:
    result = invoke("-s", "output.format=json", "-s", "output.json_indent=0", "gross", "1000000")

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["net"] == 979_100
    assert result.stdout.count("\n") == 1


def test_bad_set_option(invoke: Invoke) -> None:
    result = invoke("--set", "tax.min_salary", "gross", "1000000")

    assert result.exit_code == 2
    assert "must look like KEY=VALUE" in result.output


def test_missing_config_option_file(invoke: Invoke, work_dir: Path) -> None:
    result = invoke("--config", str(work_dir / "missing.toml"), "gross", "1")

    assert result.exit_code == 2
    assert "does not exist" in result.output


def test_settings_change_command_defaults(invoke: Invoke, work_dir: Path) -> None:
    (work_dir / "sytax.toml").write_text(
        "[net]\ncompensation_share = 0.5\n\n[range]\nmax_size = 3\n", encoding="utf-8"
    )

    net = invoke("net", "2000000", "-o", "json")
    assert json.loads(net.stdout)["compensation"] > 0
    assert json.loads(invoke("net", "2000000", "-r", "0", "-o", "json").stdout)["compensation"] == 0

    too_many = invoke("range", "1000000", "1400000", "100000")
    assert too_many.exit_code == 2
    assert "at most 3 are allowed" in too_many.output


def test_rules_output_follows_settings(invoke: Invoke) -> None:
    result = invoke("-s", "output.format=json", "-s", "output.json_indent=0", "rules")

    assert json.loads(result.stdout)["min_salary"] == 837_000
    assert result.stdout.count("\n") == 1
