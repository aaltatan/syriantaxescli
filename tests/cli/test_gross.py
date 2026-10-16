import pytest

from tests.conftest import Invoke, InvokeJSON


def test_gross_salary_and_compensation(invoke_json: InvokeJSON) -> None:
    data = invoke_json("gross", "1000000", "100000")

    assert data == {
        "salary": 1_000_000,
        "compensation": 100_000,
        "total": 1_100_000,
        "social_security": 0,
        "salary_tax": 20_900,
        "compensation_tax": 5_000,
        "taxes": 25_900,
        "deductions": 25_900,
        "net": 1_074_100,
        "compensation_ratio": pytest.approx(1 / 11),
    }


def test_compensation_defaults_to_zero(invoke_json: InvokeJSON) -> None:
    data = invoke_json("gross", "1000000")

    assert data["compensation"] == 0
    assert data["net"] == 979_100


def test_alias(invoke_json: InvokeJSON) -> None:
    assert invoke_json("g", "1000000") == invoke_json("gross", "1000000")


def test_table_output(invoke: Invoke) -> None:
    result = invoke("gross", "1000000", "100000")

    assert result.exit_code == 0
    assert "Gross Salary" in result.output
    assert "1,074,100.00" in result.output
    assert "9.09%" in result.output


@pytest.mark.parametrize("amount", ["1,000,000", "1_000_000", "1e6", "1000000.00"])
def test_amounts_can_be_written_in_several_ways(invoke_json: InvokeJSON, amount: str) -> None:
    assert invoke_json("gross", amount)["salary"] == 1_000_000


def test_insured_salary_turns_on_social_security(invoke_json: InvokeJSON) -> None:
    data = invoke_json("gross", "1000000", "100000", "-i", "750000")

    assert data["social_security"] == 52_500
    assert data["salary_tax"] == 14_100
    assert data["net"] == 1_028_400


def test_ss_flag_insures_the_gross_salary(invoke_json: InvokeJSON) -> None:
    data = invoke_json("--ss", "gross", "1000000")

    assert data["social_security"] == 70_000


def test_ss_flag_with_insured_salary(invoke_json: InvokeJSON) -> None:
    data = invoke_json("--ss", "gross", "1000000", "--insured-salary", "800000")

    assert data["social_security"] == 56_000


def test_no_ss_by_default(invoke_json: InvokeJSON) -> None:
    assert invoke_json("gross", "1000000")["social_security"] == 0


def test_social_security_options(invoke_json: InvokeJSON) -> None:
    data = invoke_json(
        "--ss",
        "--ss-deduction-rate",
        "0.1",
        "--ss-rounding-method",
        "ROUND_CEILING",
        "--ss-round-to-nearest",
        "1000",
        "gross",
        "1000000",
    )

    assert data["social_security"] == 100_000


def test_zero_salary(invoke_json: InvokeJSON) -> None:
    data = invoke_json("gross", "0")

    assert data["net"] == 0
    assert data["compensation_ratio"] == 0


def test_salary_below_the_minimum_is_untaxed(invoke_json: InvokeJSON) -> None:
    assert invoke_json("gross", "500000")["salary_tax"] == 0


# --------------------
# Errors
# --------------------


def test_salary_is_required(invoke: Invoke) -> None:
    result = invoke("gross")

    assert result.exit_code == 2
    assert "Missing argument 'salary'" in result.output


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (("abc",), "'abc' is not a valid number"),
        (("--", "-1"), "'-1' must not be negative"),
        (("--", "1000000", "-5"), "'-5' must not be negative"),
        (("1000000", "-5"), "No such option: -5"),
        (("nan",), "is not a finite number"),
        (("1000000", "-i", "-750000"), "must not be negative"),
    ],
)
def test_invalid_amounts(invoke: Invoke, args: tuple[str, ...], message: str) -> None:
    result = invoke("gross", *args)

    assert result.exit_code == 2
    assert message in result.output


def test_insured_salary_below_the_minimum(invoke: Invoke) -> None:
    result = invoke("gross", "1000000", "-i", "500000")

    assert result.exit_code == 2
    assert "insured salary must be at least 750000" in result.output


def test_ss_with_a_salary_below_the_insured_minimum(invoke: Invoke) -> None:
    result = invoke("--ss", "gross", "500000")

    assert result.exit_code == 2
    assert "insured salary must be at least 750000" in result.output


def test_too_many_arguments(invoke: Invoke) -> None:
    result = invoke("gross", "1", "2", "3")

    assert result.exit_code == 2
    assert "unexpected extra argument" in result.output
