import pytest

from ggrep.excel import int_to_excel_column


def test_zero():
    with pytest.raises(AssertionError):
        int_to_excel_column(0)


@pytest.mark.parametrize(
    "number, expected",
    (
        (1, "A"),
        (2, "B"),
        (26, "Z"),
        (27, "AA"),
        (52, "AZ"),
        (26 * 26, "YZ"),
        (26 * 26 + 1, "ZA"),
        (26 * 26 * 26, "YYZ"),
        (26 * 26 * 26 + 1, "YZA"),
    )
)
def test_label(number, expected):
    assert int_to_excel_column(number) == expected
