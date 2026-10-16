import pytest

from tests.conftest import Invoke, InvokeJSON


def test_range_of_nets(invoke_json: InvokeJSON) -> None:
    data = invoke_json("range", "1000000", "1500000", "100000", "-r", "0.25")

    assert len(data) == 6
    assert [row["net"] >= 1_000_000 + i * 100_000 for i, row in enumerate(data)] == [True] * 6


def test_aliases(invoke_json: InvokeJSON) -> None:
    expected = invoke_json("range", "1000000", "1200000", "100000")

    assert invoke_json("ar", "1000000", "1200000", "100000") == expected
    assert invoke_json("r", "1000000", "1200000", "100000") == expected


def test_stop_and_step_default_from_start(invoke_json: InvokeJSON) -> None:
    data = invoke_json("range", "1000000")

    assert len(data) == 91
    assert data[-1]["net"] >= 10_000_000


def test_step_defaults_from_start(invoke_json: InvokeJSON) -> None:
    assert len(invoke_json("range", "1000000", "2000000")) == 11


def test_single_net(invoke_json: InvokeJSON) -> None:
    data = invoke_json("range", "1000000", "1000000", "1")

    assert len(data) == 1
    assert data[0]["salary"] == 1_024_100


def test_table_has_one_row_per_net(invoke: Invoke) -> None:
    result = invoke("range", "1000000", "1200000", "100000")

    assert result.exit_code == 0
    assert "Salary Scale" in result.output
    assert "1,024,100.00" in result.output
    assert len([line for line in result.output.splitlines() if "│ 3 │" in line]) == 1


# --------------------
# Errors
# --------------------


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (("2000000", "1000000", "1000"), "must not be less than start"),
        (("1000000", "2000000", "0"), "step must be greater than 0"),
        (("1000000", "2000000", "1"), "at most 1,000 are allowed"),
        (("0",), "step must be greater than 0"),
    ],
)
def test_invalid_ranges(invoke: Invoke, args: tuple[str, ...], message: str) -> None:
    result = invoke("range", *args)

    assert result.exit_code == 2
    assert message in result.output


def test_start_below_the_minimum_salary(invoke: Invoke) -> None:
    result = invoke("range", "500000", "1000000", "100000")

    assert result.exit_code == 2
    assert "Invalid value for 'START'" in result.output


def test_invalid_share(invoke: Invoke) -> None:
    result = invoke("range", "1000000", "-r", "2")

    assert result.exit_code == 2
    assert "compensation_share must be between 0 and 1" in result.output
