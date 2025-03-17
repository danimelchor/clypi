import enum
import typing as t
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

import clypi.parsers as cp
from clypi import Positional


class Color(enum.Enum):
    RED = 1
    BLUE = 2


SUCCESS_PRIMITIVES = [
    ("1", cp.Int(), 1),
    ("1", cp.Float(), 1),
    ("1.2", cp.Float(), 1.2),
    ("y", cp.Bool(), True),
    ("yes", cp.Bool(), True),
    ("tRUe", cp.Bool(), True),
    ("n", cp.Bool(), False),
    ("No", cp.Bool(), False),
    ("faLse", cp.Bool(), False),
    ("", cp.Str(), ""),
    ("a", cp.Str(), "a"),
    ("2025-03-12", cp.DateTime(), datetime(2025, 3, 12)),
    ("2025/3/12", cp.DateTime(), datetime(2025, 3, 12)),
    (
        "2025-03-12T00:00:00Z",
        cp.DateTime(),
        datetime(2025, 3, 12, 0, 0, 0, tzinfo=UTC),
    ),
    ("1d", cp.TimeDelta(), timedelta(days=1)),
    ("1 day", cp.TimeDelta(), timedelta(days=1)),
    ("2weeks", cp.TimeDelta(), timedelta(weeks=2)),
    ("./tests/parsers_test.py", cp.Path(), Path("./tests/parsers_test.py")),
    (
        "./tests/parsers_test.py",
        cp.Path(exists=True),
        Path("./tests/parsers_test.py"),
    ),
    ("y", cp.Union(cp.Int(), cp.Bool()), True),
    ("1", cp.Union(cp.Int(), cp.Bool()), 1),
    ("1", cp.Literal("1", "foo"), "1"),
    ("foo", cp.Literal("1", "foo"), "foo"),
    ("red", cp.Enum(Color), Color.RED),
    ("blue", cp.Enum(Color), Color.BLUE),
    ("none", cp.NoneParser(), None),
    ("", cp.NoneParser(), None),
    ("", cp.Str() | cp.NoneParser(), None),
    ("", cp.NoneParser() | cp.Str(), None),
]

FAILURE_PRIMITIVES = [
    ("a", cp.Int()),
    ("1.1", cp.Int()),
    ("a", cp.Float()),
    ("p", cp.Bool()),
    ("falsey", cp.Bool()),
    ("", cp.Bool()),
    ("lsf2", cp.DateTime()),
    ("1 month", cp.TimeDelta()),
    ("1y", cp.TimeDelta()),
    (
        "./tests/parsers_test2.py",
        cp.Path(exists=True),
    ),
    ("a", cp.Union(cp.Int(), cp.Bool())),
    ("2", cp.Literal("1", "foo")),
    ("green", cp.Enum(Color)),
    ("a", cp.NoneParser()),
]


@pytest.mark.parametrize("value,parser,expected", SUCCESS_PRIMITIVES)
def test_successfull_parsers(value: t.Any, parser: cp.Parser[t.Any], expected: t.Any):
    assert parser(value) == expected


@pytest.mark.parametrize("value,parser", FAILURE_PRIMITIVES)
def test_failed_parsers(value: t.Any, parser: cp.Parser[t.Any]):
    with pytest.raises(Exception):
        parser(value)


@pytest.mark.parametrize(
    "value,parser,expected", [(v, cp.List(p), [e]) for (v, p, e) in SUCCESS_PRIMITIVES]
)
def test_successfull_list_parsers(
    value: t.Any, parser: cp.Parser[t.Any], expected: t.Any
):
    assert parser(value) == expected


@pytest.mark.parametrize(
    "value,parser", [(v, cp.List(p)) for (v, p) in FAILURE_PRIMITIVES]
)
def test_failed_list_parsers(value: t.Any, parser: cp.Parser[t.Any]):
    with pytest.raises(Exception):
        parser(value)


@pytest.mark.parametrize(
    "value,parser,expected",
    [(v + "," + v, cp.List(p), [e, e]) for (v, p, e) in SUCCESS_PRIMITIVES],
)
def test_successfull_two_item_list_parsers(
    value: t.Any, parser: cp.Parser[t.Any], expected: t.Any
):
    assert parser(value) == expected


@pytest.mark.parametrize(
    "value,parser,expected",
    [(v, cp.Tuple(p, num=1), (e,)) for (v, p, e) in SUCCESS_PRIMITIVES],
)
def test_successfull_tuple_parsers(
    value: t.Any, parser: cp.Parser[t.Any], expected: t.Any
):
    assert parser(value) == expected


@pytest.mark.parametrize(
    "value,parser",
    [(v, cp.Tuple(p, num=1)) for (v, p) in FAILURE_PRIMITIVES],
)
def test_failed_tuple_parsers(value: t.Any, parser: cp.Parser[t.Any]):
    with pytest.raises(Exception):
        parser(value)


@pytest.mark.parametrize(
    "value,parser,expected",
    [(v + "," + v, cp.Tuple(p, p, num=2), (e, e)) for (v, p, e) in SUCCESS_PRIMITIVES],
)
def test_successfull_two_item_tuple_parsers(
    value: t.Any, parser: cp.Parser[t.Any], expected: t.Any
):
    assert parser(value) == expected


@pytest.mark.parametrize(
    "_type,expected",
    [
        (Positional[int], cp.Int()),
        (int, cp.Int()),
        (float, cp.Float()),
        (bool, cp.Bool()),
        (str, cp.Str()),
        (datetime, cp.DateTime()),
        (timedelta, cp.TimeDelta()),
        (Path, cp.Path()),
        (int | bool, cp.Union(cp.Int(), cp.Bool())),
        (int | bool | str, cp.Int() | cp.Bool() | cp.Str()),
        (t.Literal[1, "foo"], cp.Literal("1", "foo")),
        (Color, cp.Enum(Color)),
        (int | None, cp.Union(cp.Int(), cp.NoneParser())),
    ],
)
def test_parser_from_type(_type: t.Any, expected: cp.Parser[t.Any]):
    assert cp.from_type(_type) == expected


@pytest.mark.parametrize(
    "parser,expected",
    [
        (cp.Int(), "integer"),
        (cp.Float(), "float"),
        (cp.Bool(), "{yes|no}"),
        (cp.Str(), "text"),
        (cp.DateTime(), "datetime"),
        (cp.TimeDelta(), "timedelta"),
        (cp.Path(), "path"),
        (cp.Union(cp.Int(), cp.Bool()), "(integer|yes|no)"),
        (cp.Int() | cp.Bool() | cp.Str(), "(integer|yes|no|text)"),
        (cp.Literal("1", "foo"), "{1|foo}"),
        (cp.Enum(Color), "{red|blue}"),
    ],
)
def test_parser_str(parser: cp.Parser[t.Any], expected: cp.Parser[t.Any]):
    assert str(parser) == expected
