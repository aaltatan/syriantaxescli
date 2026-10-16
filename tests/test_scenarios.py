"""End-to-end stories of how people use `sytax`."""

import json
import os
from pathlib import Path

import openpyxl
import pytest

from syriantaxescli.core import config
from syriantaxescli.core.config import default_preset, dump_toml, load_preset, merge
from tests.conftest import Invoke, InvokeJSON


def test_hr_checks_an_employees_payslip(invoke_json: InvokeJSON) -> None:
    """An HR officer checks a 1M salary, 100K compensations payslip, insured at 750K."""
    payslip = invoke_json("gross", "1,000,000", "100,000", "--insured-salary", "750,000")

    assert payslip["social_security"] == 52_500
    assert payslip["salary_tax"] == 14_100
    assert payslip["compensation_tax"] == 5_000
    assert payslip["net"] == 1_028_400


def test_a_candidate_asks_for_a_net_salary(invoke_json: InvokeJSON) -> None:
    """A candidate wants 1,500,000 net. HR finds the gross, then checks it the other way."""
    offer = invoke_json("net", "1500000")

    check = invoke_json("gross", str(offer["salary"]), str(offer["compensation"]))

    assert check == offer
    assert check["net"] >= 1_500_000


def test_payroll_exports_a_salary_scale_to_excel(invoke: Invoke, tmp_path: Path) -> None:
    """Payroll builds a scale from 1M to 2M net, a quarter as compensations, for Excel."""
    path = tmp_path / "scale-2026.xlsx"

    result = invoke("range", "1000000", "2000000", "100000", "-r", "0.25", "-e", str(path))
    assert result.exit_code == 0, result.output

    ws = openpyxl.load_workbook(path).active
    assert ws is not None
    rows = list(ws.iter_rows(values_only=True))
    headers, body = rows[0], rows[1:]
    net = headers.index("Net")
    assert len(body) == 11
    assert [row[0] for row in body] == list(range(1, 12))
    # Each net is close to its target (see the strict xfail on compensations in core tests).
    for index, row in enumerate(body):
        value = row[net]
        assert isinstance(value, int | float)
        assert abs(value - (1_000_000 + index * 100_000)) < 200

    # Running it again must not silently replace the file.
    again = invoke("range", "1000000", "2000000", "100000", "-e", str(path))
    assert again.exit_code == 2


def test_the_law_changes_and_the_company_sets_new_rules_once(invoke_json: InvokeJSON) -> None:
    """New brackets are set once with environment variables; every command follows."""
    env = {
        "SYRIANTAXES_BRACKET_TAX_MINS": "0 1000000 2000000",
        "SYRIANTAXES_BRACKET_TAX_RATES": "0 0.1 0.2",
        "SYRIANTAXES_MIN_ALLOWED_SALARY": "1000000",
        "SYRIANTAXES_FIXED_TAX_RATE": "0.04",
        "SYRIANTAXES_TAXES_ROUNDING_METHOD": "ROUND_CEILING",
        "SYRIANTAXES_TAXES_ROUND_TO_NEAREST": "1000",
    }

    rules = invoke_json("rules", env=env)
    assert [bracket["lower"] for bracket in rules["brackets"]] == [0, 1_000_000, 2_000_000]
    assert rules["rounding"] == "CEILING to 1000"

    # 10% of 500,000 = 50,000; 4% of 100,000 = 4,000.
    payslip = invoke_json("gross", "1500000", "100000", env=env)
    assert payslip["salary_tax"] == 50_000
    assert payslip["compensation_tax"] == 4_000

    # An option still wins over the environment for a one-off check.
    one_off = invoke_json("--fixed-tax-rate", "0.05", "gross", "1500000", "100000", env=env)
    assert one_off["compensation_tax"] == 5_000


def test_social_security_is_turned_on_for_everyone(invoke_json: InvokeJSON) -> None:
    env = {"SYRIANTAXES_SS_ENABLED": "1", "SYRIANTAXES_SS_DEDUCTION_RATE": "0.09"}

    assert invoke_json("rules", env=env)["social_security"]["enabled"] is True
    assert invoke_json("gross", "1000000", env=env)["social_security"] == 90_000
    assert invoke_json("--no-ss", "gross", "1000000", env=env)["social_security"] == 0


def test_rounding_method_from_an_old_config_still_works(invoke_json: InvokeJSON) -> None:
    """0.1 configs used the decimal constant names, in any case."""
    env = {"SYRIANTAXES_TAXES_ROUNDING_METHOD": "round_half_even"}

    assert invoke_json("rules", env=env)["rounding"] == "HALF_EVEN to 100"


def test_a_script_reads_json_lines(invoke: Invoke, tmp_path: Path) -> None:
    """A script exports a scale as JSON lines and reads it back line by line."""
    path = tmp_path / "scale.jsonl"

    result = invoke("range", "1000000", "1500000", "250000", "--export", str(path))
    assert result.exit_code == 0

    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert [record["net"] >= 1_000_000 for record in records] == [True, True, True]


def test_typos_get_helpful_errors_and_change_nothing(invoke: Invoke, tmp_path: Path) -> None:
    path = tmp_path / "scale.xlsx"

    typo = invoke("range", "1,000,00O", "-e", str(path))
    assert typo.exit_code == 2
    assert "'1,000,00O' is not a valid number" in typo.output

    mismatch = invoke("--brackets-mins", "0", "--brackets-mins", "900000", "gross", "1000000")
    assert mismatch.exit_code == 2
    assert "2 bracket lower bound(s) but 0 rate(s)" in mismatch.output

    too_low = invoke("net", "800000")
    assert too_low.exit_code == 2
    assert "less than 837000" in too_low.output

    assert not path.exists()


# --------------------
# Configuration stories
# --------------------


def test_a_company_configures_sytax_once(invoke: Invoke, invoke_json: InvokeJSON) -> None:
    """The company raises the minimum salary in its user config; every command follows."""
    assert invoke("config", "init", "--user").exit_code == 0
    config = Path(os.environ["SYRIANTAXES_CONFIG_HOME"]) / "config.toml"
    config.write_text(
        config.read_text(encoding="utf-8").replace("# min_salary = 837000", "min_salary = 900000"),
        encoding="utf-8",
    )

    assert invoke_json("rules")["min_salary"] == 900_000
    too_low = invoke("net", "850000")
    assert too_low.exit_code == 2
    assert "less than 900000" in too_low.output


def test_a_payroll_folder_overrides_the_company_config(
    invoke: Invoke, invoke_json: InvokeJSON, work_dir: Path, user_dir: Path
) -> None:
    """One branch pays a quarter as compensations; its folder says so, the company file doesn't."""
    (user_dir / "config.toml").write_text("[tax]\nmin_salary = 900000\n", encoding="utf-8")
    branch = work_dir / "branch-aleppo"
    branch.mkdir()
    (branch / "sytax.toml").write_text("[net]\ncompensation_share = 0.25\n", encoding="utf-8")

    os.chdir(branch)
    offer = invoke_json("net", "2000000")
    shown = invoke("config", "show", "-o", "json", "--sources")
    sources = json.loads(shown.stdout)["sources"]

    assert offer["compensation"] > 0
    assert invoke_json("rules")["min_salary"] == 900_000
    assert sources["net.compensation_share"] == str(branch / "sytax.toml")
    assert sources["tax.min_salary"] == str(user_dir / "config.toml")


def test_last_years_payslip_is_reproduced_with_a_preset(
    invoke_json: InvokeJSON, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """When the law changes, a new preset becomes the default; old ones stay available."""
    presets = tmp_path / "presets"
    presets.mkdir()
    current = load_preset(default_preset())
    (presets / "syria-2099.toml").write_text(dump_toml(current), encoding="utf-8")
    older = merge(current, {"tax": {"compensation_tax_rate": 0.1}})
    (presets / "syria-2098.toml").write_text(dump_toml(older), encoding="utf-8")
    monkeypatch.setattr(config, "files", lambda _package: presets)

    this_year = invoke_json("gross", "1000000", "100000")
    last_year = invoke_json("--preset", "syria-2098", "gross", "1000000", "100000")

    assert this_year["compensation_tax"] == 5_000
    assert last_year["compensation_tax"] == 10_000


def test_a_one_off_what_if(invoke_json: InvokeJSON) -> None:
    """What if compensations were taxed at 3%? Try it without touching any file."""
    today = invoke_json("gross", "1000000", "100000")
    what_if = invoke_json("-s", "tax.compensation_tax_rate=0.03", "gross", "1000000", "100000")

    assert what_if["net"] - today["net"] == 2_000
