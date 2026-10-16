import tomllib
from collections.abc import Sequence
from decimal import Decimal
from pathlib import Path

import pytest

from syriantaxescli.core import RoundingMethod
from syriantaxescli.core.config import (
    ConfigError,
    Layer,
    LoadedSettings,
    brackets_layer,
    config_files,
    default_preset,
    dump_toml,
    env_layer,
    find_project_file,
    list_presets,
    load_preset,
    load_settings,
    merge,
    parse_set,
    preset_settings,
    read_toml,
)
from syriantaxescli.core.settings import Output, Settings

D = Decimal


@pytest.fixture
def home(tmp_path: Path) -> Path:
    path = tmp_path / "home"
    path.mkdir(exist_ok=True)
    return path


@pytest.fixture
def project(tmp_path: Path) -> Path:
    path = tmp_path / "project"
    path.mkdir(exist_ok=True)
    return path


def _load(
    project: Path,
    home: Path,
    environ: dict[str, str] | None = None,
    *,
    config_path: Path | None = None,
    cli_layer: Layer | None = None,
    set_items: Sequence[str] = (),
) -> LoadedSettings:
    return load_settings(
        cwd=project,
        user_dir=home,
        environ=environ or {},
        config_path=config_path,
        cli_layer=cli_layer,
        set_items=set_items,
    )


# --------------------
# Presets
# --------------------


def test_there_is_a_default_preset() -> None:
    assert default_preset() in list_presets()
    assert default_preset() == max(list_presets())


@pytest.mark.parametrize("name", list_presets())
def test_every_preset_is_complete_on_its_own(name: str) -> None:
    settings = Settings.model_validate({**load_preset(name), "preset": name})

    assert settings.tax.to_rules().brackets


def test_unknown_preset_lists_the_available_ones() -> None:
    with pytest.raises(ConfigError, match=f"unknown preset 'nope'; available: {default_preset()}"):
        load_preset("nope")


def test_default_preset_values() -> None:
    settings = preset_settings()

    assert settings.preset == default_preset()
    assert [b.lower for b in settings.tax.brackets] == [0, 837_000, 850_000, 1_100_000]
    assert [b.rate for b in settings.tax.brackets] == [0, D("0.11"), D("0.13"), D("0.15")]
    assert settings.tax.min_salary == 837_000
    assert settings.tax.rounding.method is RoundingMethod.HALF_UP
    assert settings.tax.social_security.enabled is False
    assert settings.net.compensation_share == 0
    assert settings.output.format is Output.TABLE
    assert settings.range.max_size == 1000


def test_rules_can_force_social_security_on_or_off() -> None:
    tax = preset_settings().tax

    assert tax.to_rules().social_security is None
    assert tax.to_rules(social_security=True).social_security is not None
    assert tax.social_security.to_rules().rate == D("0.07")


# --------------------
# Precedence
# --------------------


def test_with_nothing_set_the_preset_is_used(project: Path, home: Path) -> None:
    loaded = _load(project, home)

    assert loaded.settings == preset_settings()
    assert [source.name for source in loaded.sources] == [f"preset {default_preset()}"]
    assert loaded.origin(("tax", "min_salary")) == f"preset {default_preset()}"
    assert loaded.origin(("preset",)) == "default"


def test_each_layer_overrides_the_one_before(project: Path, home: Path, tmp_path: Path) -> None:
    def write(path: Path, value: int) -> Path:
        path.write_text(f"[tax]\nmin_salary = {value}\n", encoding="utf-8")
        return path

    write(home / "config.toml", 1)
    loaded = _load(project, home)
    assert loaded.settings.tax.min_salary == 1

    project_file = write(project / "sytax.toml", 2)
    assert _load(project, home).settings.tax.min_salary == 2

    extra = write(tmp_path / "extra.toml", 3)
    assert _load(project, home, config_path=extra).settings.tax.min_salary == 3

    env = {"SYRIANTAXES_MIN_ALLOWED_SALARY": "4"}
    assert _load(project, home, env, config_path=extra).settings.tax.min_salary == 4

    cli = {"tax": {"min_salary": 5}}
    assert _load(project, home, env, config_path=extra, cli_layer=cli).settings.tax.min_salary == 5

    loaded = _load(
        project, home, env, config_path=extra, cli_layer=cli, set_items=["tax.min_salary=6"]
    )
    assert loaded.settings.tax.min_salary == 6
    assert loaded.origin(("tax", "min_salary")) == "--set tax.min_salary=6"
    assert [source.name for source in loaded.sources][1:] == [
        str(home / "config.toml"),
        str(project_file),
        str(extra),
        "environment variables",
        "command-line options",
        "--set tax.min_salary=6",
    ]


def test_later_set_items_win(project: Path, home: Path) -> None:
    loaded = _load(project, home, set_items=["tax.min_salary=1", "tax.min_salary=2"])

    assert loaded.settings.tax.min_salary == 2


def test_tables_merge_and_keep_other_keys(project: Path, home: Path) -> None:
    (project / "sytax.toml").write_text("[tax.rounding]\nstep = 1000\n", encoding="utf-8")

    rounding = _load(project, home).settings.tax.rounding

    assert rounding.step == 1000
    assert rounding.method is RoundingMethod.HALF_UP


def test_lists_are_replaced_not_merged(project: Path, home: Path) -> None:
    (project / "sytax.toml").write_text(
        "[[tax.brackets]]\nlower = 0\nrate = 0\n\n[[tax.brackets]]\nlower = 2000000\nrate = 0.2\n",
        encoding="utf-8",
    )

    brackets = _load(project, home).settings.tax.brackets

    assert [b.lower for b in brackets] == [0, 2_000_000]


def test_project_file_is_found_in_a_parent_folder(project: Path, home: Path) -> None:
    (project / "sytax.toml").write_text("[tax]\nmin_salary = 1\n", encoding="utf-8")
    nested = project / "2026" / "october"
    nested.mkdir(parents=True)

    assert find_project_file(nested) == project / "sytax.toml"
    assert _load(nested, home).settings.tax.min_salary == 1


def test_no_project_file(project: Path) -> None:
    assert find_project_file(project) is None


def test_dotenv_file_is_read_and_real_env_vars_win(project: Path, home: Path) -> None:
    (project / ".env").write_text(
        "SYRIANTAXES_MIN_ALLOWED_SALARY=1\nSYRIANTAXES_FIXED_TAX_RATE=0.04\nOTHER\n",
        encoding="utf-8",
    )

    settings = _load(project, home, {"SYRIANTAXES_MIN_ALLOWED_SALARY": "2"}).settings

    assert settings.tax.min_salary == 2
    assert settings.tax.compensation_tax_rate == D("0.04")


def test_config_env_var_names_an_extra_file(project: Path, home: Path, tmp_path: Path) -> None:
    extra = tmp_path / "company.toml"
    extra.write_text("[tax]\nmin_salary = 7\n", encoding="utf-8")

    settings = _load(project, home, {"SYRIANTAXES_CONFIG": str(extra)}).settings

    assert settings.tax.min_salary == 7


# --------------------
# Presets chosen by layers
# --------------------


def test_preset_can_come_from_any_layer(project: Path, home: Path) -> None:
    preset = default_preset()
    (home / "config.toml").write_text(f'preset = "{preset}"\n', encoding="utf-8")

    loaded = _load(project, home)

    assert loaded.settings.preset == preset
    assert loaded.origin(("preset",)) == str(home / "config.toml")


def test_unknown_preset_from_a_layer(project: Path, home: Path) -> None:
    with pytest.raises(ConfigError, match="unknown preset 'syria-1990'"):
        _load(project, home, {"SYRIANTAXES_PRESET": "syria-1990"})


def test_preset_must_be_a_name(project: Path, home: Path) -> None:
    with pytest.raises(ConfigError, match="preset must be a name, got 5"):
        _load(project, home, set_items=["preset=5"])


# --------------------
# Errors
# --------------------


def test_unknown_key_names_the_file(project: Path, home: Path) -> None:
    path = project / "sytax.toml"
    path.write_text("[tax]\nmin_salry = 1\n", encoding="utf-8")

    with pytest.raises(ConfigError) as exc_info:
        _load(project, home)

    assert f"tax.min_salry: unknown setting; `sytax config show` lists them (from {path})" in str(
        exc_info.value
    )


def test_invalid_value_names_the_layer(project: Path, home: Path) -> None:
    with pytest.raises(
        ConfigError,
        match=r"compensation_tax_rate: Input should be less than 1 \(from environment variables\)",
    ):
        _load(project, home, {"SYRIANTAXES_FIXED_TAX_RATE": "1"})


def test_invalid_brackets(project: Path, home: Path) -> None:
    with pytest.raises(ConfigError, match="brackets must start with a bracket whose lower is 0"):
        _load(project, home, set_items=["tax.brackets=[{lower = 5, rate = 0}]"])


def test_invalid_toml(project: Path, home: Path) -> None:
    (project / "sytax.toml").write_text("[tax\n", encoding="utf-8")

    with pytest.raises(ConfigError, match="is not valid TOML"):
        _load(project, home)


def test_missing_extra_file(project: Path, home: Path, tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="can't read"):
        _load(project, home, config_path=tmp_path / "missing.toml")


def test_read_toml(tmp_path: Path) -> None:
    path = tmp_path / "a.toml"
    path.write_text("a = 1\n", encoding="utf-8")

    assert read_toml(path) == {"a": 1}


# --------------------
# Environment variables
# --------------------


def test_env_layer_maps_every_variable() -> None:
    layer = env_layer(
        {
            "SYRIANTAXES_PRESET": "p",
            "SYRIANTAXES_MIN_ALLOWED_SALARY": "1",
            "SYRIANTAXES_FIXED_TAX_RATE": "2",
            "SYRIANTAXES_TAXES_ROUNDING_METHOD": "3",
            "SYRIANTAXES_TAXES_ROUND_TO_NEAREST": "4",
            "SYRIANTAXES_SS_ENABLED": "5",
            "SYRIANTAXES_SS_DEDUCTION_RATE": "6",
            "SYRIANTAXES_MIN_SS_ALLOWED_SALARY": "7",
            "SYRIANTAXES_SS_ROUNDING_METHOD": "8",
            "SYRIANTAXES_SS_ROUND_TO_NEAREST": "9",
            "SYRIANTAXES_BRACKET_TAX_MINS": "0 100",
            "SYRIANTAXES_BRACKET_TAX_RATES": "0 0.1",
            "UNRELATED": "x",
        }
    )

    assert layer == {
        "preset": "p",
        "tax": {
            "min_salary": "1",
            "compensation_tax_rate": "2",
            "rounding": {"method": "3", "step": "4"},
            "social_security": {
                "enabled": "5",
                "rate": "6",
                "min_salary": "7",
                "rounding": {"method": "8", "step": "9"},
            },
            "brackets": [{"lower": "0", "rate": "0"}, {"lower": "100", "rate": "0.1"}],
        },
    }


def test_env_layer_ignores_empty_values() -> None:
    assert env_layer({"SYRIANTAXES_MIN_ALLOWED_SALARY": ""}) == {}


@pytest.mark.parametrize(
    "environ",
    [{"SYRIANTAXES_BRACKET_TAX_MINS": "0 100"}, {"SYRIANTAXES_BRACKET_TAX_RATES": "0 0.1"}],
)
def test_env_brackets_need_both_variables(environ: dict[str, str]) -> None:
    with pytest.raises(ConfigError, match="set both SYRIANTAXES_BRACKET_TAX_MINS"):
        env_layer(environ)


def test_brackets_layer_needs_matching_counts() -> None:
    assert brackets_layer([0], [0]) == [{"lower": 0, "rate": 0}]
    with pytest.raises(ConfigError, match="every bracket needs both"):
        brackets_layer([0, 1], [0])


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1,000,000", D(1_000_000)),
        ("1_000_000", D(1_000_000)),
        (" 900000 ", D(900_000)),
    ],
)
def test_amounts_from_text_may_have_separators(
    project: Path, home: Path, value: str, expected: Decimal
) -> None:
    settings = _load(project, home, {"SYRIANTAXES_MIN_ALLOWED_SALARY": value}).settings

    assert settings.tax.min_salary == expected


@pytest.mark.parametrize("method", ["ROUND_CEILING", "round_ceiling", "ceiling", " Ceiling "])
def test_rounding_methods_in_any_spelling(project: Path, home: Path, method: str) -> None:
    settings = _load(project, home, {"SYRIANTAXES_TAXES_ROUNDING_METHOD": method}).settings

    assert settings.tax.rounding.method is RoundingMethod.CEILING


def test_rounding_method_must_be_text(project: Path, home: Path) -> None:
    with pytest.raises(ConfigError, match=r"tax.rounding.method: Input should be"):
        _load(project, home, set_items=["tax.rounding.method=5"])


@pytest.mark.parametrize(("value", "expected"), [("1", True), ("true", True), ("0", False)])
def test_booleans_from_env(project: Path, home: Path, value: str, *, expected: bool) -> None:
    settings = _load(project, home, {"SYRIANTAXES_SS_ENABLED": value}).settings

    assert settings.tax.social_security.enabled is expected


# --------------------
# --set
# --------------------


@pytest.mark.parametrize(
    ("item", "expected"),
    [
        ("tax.min_salary=900000", {"tax": {"min_salary": 900000}}),
        ("tax.compensation_tax_rate=0.04", {"tax": {"compensation_tax_rate": 0.04}}),
        ('tax.compensation_tax_rate="0.04"', {"tax": {"compensation_tax_rate": "0.04"}}),
        ("tax.social_security.enabled=true", {"tax": {"social_security": {"enabled": True}}}),
        ("output.format=json", {"output": {"format": "json"}}),
        (" output.format = json ", {"output": {"format": "json"}}),
        ("preset=syria-2024", {"preset": "syria-2024"}),
        ("a=x=y", {"a": "x=y"}),
        ("tax.rounding={step = 1}", {"tax": {"rounding": {"step": 1}}}),
    ],
)
def test_parse_set(item: str, expected: Layer) -> None:
    assert parse_set(item) == expected


@pytest.mark.parametrize("item", ["tax.min_salary", "=1", "tax..min=1", "tax.=1"])
def test_parse_set_needs_key_and_value(item: str) -> None:
    with pytest.raises(ConfigError, match="must look like KEY=VALUE"):
        parse_set(item)


def test_set_any_setting(project: Path, home: Path) -> None:
    settings = _load(
        project,
        home,
        set_items=["output.format=json", "range.max_size=10", "net.compensation_share=0.25"],
    ).settings

    assert settings.output.format is Output.JSON
    assert settings.range.max_size == 10
    assert settings.net.compensation_share == D("0.25")


# --------------------
# Helpers
# --------------------


def test_merge() -> None:
    base = {"a": {"b": 1, "c": 2}, "list": [1, 2], "x": 1}
    override = {"a": {"b": 3}, "list": [9], "y": 2}

    assert merge(base, override) == {"a": {"b": 3, "c": 2}, "list": [9], "x": 1, "y": 2}
    assert base == {"a": {"b": 1, "c": 2}, "list": [1, 2], "x": 1}


def test_merge_replaces_a_table_with_a_value() -> None:
    assert merge({"a": {"b": 1}}, {"a": 1}) == {"a": 1}


def test_config_files(project: Path, home: Path, tmp_path: Path) -> None:
    files = config_files(cwd=project, user_dir=home, environ={})

    assert files.user == home / "config.toml"
    assert files.extra is None
    assert files.dotenv == project / ".env"

    extra = tmp_path / "x.toml"
    assert config_files(cwd=project, user_dir=home, environ={}, config_path=extra).extra == extra
    assert (
        config_files(cwd=project, user_dir=home, environ={"SYRIANTAXES_CONFIG": str(extra)}).extra
        == extra
    )


def test_dump_toml_round_trips_the_settings() -> None:
    data = preset_settings().model_dump(mode="python")

    text = dump_toml(data)

    assert Settings.model_validate(tomllib.loads(text)) == preset_settings()
    assert "[[tax.brackets]]" in text
    assert 'method = "ROUND_HALF_UP"' in text
    assert "enabled = false" in text


def test_dump_toml_values() -> None:
    text = dump_toml({"flag": True, "ratio": 0.5, "items": [1, "a"], "empty": []})

    assert tomllib.loads(text) == {"flag": True, "ratio": 0.5, "items": [1, "a"], "empty": []}
