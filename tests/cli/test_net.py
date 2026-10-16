import pytest

from tests.conftest import Invoke, InvokeJSON


def test_net_without_compensation(invoke_json: InvokeJSON) -> None:
    data = invoke_json("net", "1000000")

    assert data["salary"] == 1_024_100
    assert data["compensation"] == 0
    assert data["net"] == 1_000_000


def test_net_with_a_compensation_share(invoke_json: InvokeJSON) -> None:
    data = invoke_json("net", "4000000", "-r", "0.75")

    assert data["salary"] == 1_024_100
    assert data["compensation"] == 3_157_900
    assert data["net"] == 4_000_000


def test_long_option_and_alias(invoke_json: InvokeJSON) -> None:
    assert invoke_json("n", "4000000", "--compensations-rate", "0.75") == invoke_json(
        "net", "4000000", "-r", "0.75"
    )


def test_all_compensation_still_pays_the_minimum_salary(invoke_json: InvokeJSON) -> None:
    data = invoke_json("net", "2000000", "-r", "1")

    assert data["salary"] == 837_000
    assert data["net"] >= 2_000_000


def test_exactly_the_minimum_salary(invoke_json: InvokeJSON) -> None:
    data = invoke_json("net", "837000")

    assert data["salary"] == 837_000
    assert data["salary_tax"] == 0


def test_with_social_security(invoke_json: InvokeJSON) -> None:
    data = invoke_json("--ss", "net", "1000000")

    assert data["social_security"] > 0
    assert data["net"] >= 1_000_000


def test_table_output(invoke: Invoke) -> None:
    result = invoke("net", "1000000")

    assert result.exit_code == 0
    assert "Net Salary" in result.output
    assert "1,024,100.00" in result.output


def test_custom_minimum_salary(invoke_json: InvokeJSON) -> None:
    data = invoke_json("--min-allowed-salary", "500000", "net", "600000")

    assert data["net"] >= 600_000


# --------------------
# Errors
# --------------------


def test_target_below_the_minimum_salary(invoke: Invoke) -> None:
    result = invoke("net", "500000")

    assert result.exit_code == 2
    assert "Invalid value for 'TARGET'" in result.output
    assert "less than 837000" in result.output


@pytest.mark.parametrize("share", ["1.5", "-0.1"])
def test_share_outside_zero_to_one(invoke: Invoke, share: str) -> None:
    result = invoke("net", "1000000", "-r", share)

    assert result.exit_code == 2
    assert "compensation_share must be between 0 and 1" in result.output


def test_target_is_required(invoke: Invoke) -> None:
    result = invoke("net")

    assert result.exit_code == 2
    assert "Missing argument 'target'" in result.output
