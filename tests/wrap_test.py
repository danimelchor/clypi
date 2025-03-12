import pytest

from clypi import OverflowStyle, wrap


@pytest.mark.parametrize(
    "s,overflow_style,expected",
    [
        ("a", "ellipsis", ["a"]),
        ("a" * 20, "ellipsis", ["a" * 20]),
        ("a" * 21, "ellipsis", ["a" * 19 + "…"]),
        ("a", "wrap", ["a"]),
        ("a" * 20, "wrap", ["a" * 20]),
        ("a" * 21, "wrap", ["a" * 20, "a"]),
        ("a" * 45, "wrap", ["a" * 20, "a" * 20, "a" * 5]),
    ],
)
def test_wrapping(s: str, overflow_style: OverflowStyle, expected: str):
    width = 20
    result = wrap(s, width, overflow_style)
    assert result == expected
    assert len(result) <= width
