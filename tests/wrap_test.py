from textwrap import dedent

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


def test_long_sentence_wrap():
    sentence = dedent(
        """
        This is a very long sentence which should ideally split by the words "sentence",
        "should", "by", "sentence", etc.
        """
    ).strip()
    res = wrap(sentence, width=20, overflow_style="wrap")
    assert res == [
        "This is a very long",
        "sentence which",
        "should ideally split",
        "by the words",
        '"sentence",',
        '"should", "by",',
        '"sentence", etc.',
    ]
