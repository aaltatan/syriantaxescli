import pytest

from tests.conftest import Invoke, InvokeJSON


def test_default_rules(invoke_json: InvokeJSON) -> None:
    assert invoke_json("rules") == {
        "brackets": [
            {"lower": 0, "upper": 837_000, "rate": 0},
            {"lower": 837_000, "upper": 850_000, "rate": 0.11},
            {"lower": 850_000, "upper": 1_100_000, "rate": 0.13},
            {"lower": 1_100_000, "upper": None, "rate": 0.15},
        ],
        "min_salary": 837_000,
        "compensation_tax_rate": 0.05,
        "rounding": "HALF_UP to 100",
        "social_security": {
            "enabled": False,
            "rate": 0.07,
            "min_salary": 750_000,
            "rounding": "HALF_UP to 1",
        },
    }


def test_table_output(invoke: Invoke) -> None:
    result = invoke("rules")

    assert result.exit_code == 0
    assert "Salary Tax Brackets" in result.output
    assert "and above" in result.output
    assert "HALF_UP to 100" in result.output
    assert "│ Social security          │            off │" in result.output


def test_options_change_the_rules(invoke_json: InvokeJSON) -> None:
    data = invoke_json(
        "--brackets-mins",
        "0",
        "--brackets-mins",
        "1000000",
        "--brackets-rates",
        "0",
        "--brackets-rates",
        "0.2",
        "--fixed-tax-rate",
        "0.1",
        "--taxes-rounding-method",
        "round_ceiling",
        "--taxes-round-to-nearest",
        "1",
        "--ss",
        "rules",
    )

    assert data["brackets"] == [
        {"lower": 0, "upper": 1_000_000, "rate": 0},
        {"lower": 1_000_000, "upper": None, "rate": 0.2},
    ]
    assert data["compensation_tax_rate"] == 0.1
    assert data["rounding"] == "CEILING to 1"
    assert data["social_security"]["enabled"] is True


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (("--brackets-mins", "0", "--brackets-rates", "0", "--brackets-rates", "0.1"), "every"),
        (("--brackets-mins", "100", "--brackets-rates", "0.1"), "must start with a bracket"),
        (
            ("--brackets-mins", "0", "--brackets-mins", "0", *("--brackets-rates", "0") * 2),
            "strictly increasing",
        ),
        (("--brackets-mins", "0", "--brackets-rates", "1"), "tax.brackets.0.rate: Input should be"),
        (("--fixed-tax-rate", "1"), "tax.compensation_tax_rate: Input should be less than 1"),
        (("--fixed-tax-rate", "-0.1"), "tax.compensation_tax_rate: Input should be greater than"),
        (("--taxes-round-to-nearest", "0"), "tax.rounding.step: Input should be greater than 0"),
        (("--taxes-rounding-method", "ROUND_SIDEWAYS"), "Invalid value for '--taxes-rounding"),
        (("--ss-deduction-rate", "1.5"), "tax.social_security.rate: Input should be less than 1"),
        (("--ss-round-to-nearest", "-1"), "social_security.rounding.step: Input should be greater"),
        (("--min-allowed-salary", "-1"), "must not be negative"),
    ],
)
def test_invalid_rules(invoke: Invoke, args: tuple[str, ...], message: str) -> None:
    result = invoke(*args, "rules")

    assert result.exit_code == 2
    assert message in result.output
