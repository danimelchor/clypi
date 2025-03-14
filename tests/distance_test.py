import pytest

from clypi._distance import closest, distance


@pytest.mark.parametrize(
    "this,other,expected",
    [
        ("a", "a", 0),
        ("a", "A", 0.5),
        ("a", "b", 1),
        ("aa", "bb", 2),
        ("ab", "bb", 1),
        ("", "bb", 2),
        ("aa", "", 2),
        ("wrapped", "tapped", 2),
        ("version", "vresion", 2),
    ],
)
def test_distance(this: str, other: str, expected: str):
    assert distance(this, other) == expected
    assert distance(other, this) == expected


@pytest.mark.parametrize(
    "this,others,expected",
    [
        ("v", ["v", "version", "foo"], ("v", 0)),
        ("v", ["V", "version", "foo"], ("V", 0.5)),
        ("a", ["b", "version", "foo"], ("b", 1)),
        ("vresion", ["version", "foo"], ("version", 2)),
    ],
)
def test_closest(this: str, others: list[str], expected: tuple[str, int]):
    assert closest(this, others) == expected
