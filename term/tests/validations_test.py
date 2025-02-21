from __future__ import annotations

from pytest import mark

from term import validations as v


@mark.parametrize(
    "input,expected",
    [
        (1, True),
        (2, True),
        (0, False),
        (3, False),
    ],
)
def test_range_validation(input, expected):
    assert v.Range(1, 2).test(input) == expected


@mark.parametrize(
    "input,expected",
    [
        ("foo1", True),
        ("f1", True),
        ("z1", False),
        ("f", False),
    ],
)
def test_intersection_validation(input, expected):
    val = v.ReSearch(r"[0-9]+$") & v.StartsWith("f")
    assert val.test(input) == expected


@mark.parametrize(
    "input,expected",
    [
        ("foo12", True),
        ("z12", True),
        ("ffff", True),
        ("abc", False),
    ],
)
def test_union_validation(input, expected):
    val = v.ReSearch(r"[0-9]{2}$") | v.StartsWith("f")
    assert val.test(input) == expected


def test_union_and_intersection():
    val = v.ReSearch(r"[0-9]{2}$") | v.StartsWith("f") & v.EndsWith("2")
    assert val.test("12")
    assert val.test("f2")
    assert val.test("f12")
    assert not val.test("z2")


@mark.parametrize(
    "input,expected",
    [
        (1, True),
        (2, False),
        (3, False),
    ],
)
def test_choices_validation(input, expected):
    assert v.Choices([1]).test(input) == expected


def _custom_validation(x: int) -> None:
    if x % 3 != 0:
        raise ValueError("Value must be divisible by 3")


@mark.parametrize(
    "input,expected",
    [
        (3, True),
        (6, True),
        (4, False),
        (5, False),
    ],
)
def test_custom_validation(input, expected):
    assert v.Custom(_custom_validation).test(input) == expected
