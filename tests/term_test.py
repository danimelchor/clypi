from __future__ import annotations

import io
import re
import sys
from contextlib import contextmanager
from datetime import date, datetime, timedelta

import pytest
from pytest import mark

import term
from term.input import MaxAttemptsException, Parser


@contextmanager
def replace_stdin(answers: list[str] | str = []):
    answers = [answers] if isinstance(answers, str) else answers
    target = "\n".join(answers)

    orig = sys.stdin
    sys.stdin = io.StringIO(target)
    yield
    sys.stdin = orig


@contextmanager
def replace_stdout():
    orig = sys.stdout
    new = io.StringIO()
    sys.stdout = new
    yield new
    sys.stdout = orig


def _escape_ansi(line: str) -> str:
    """
    https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python
    """
    ansi_escape = re.compile(r"(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]")
    return ansi_escape.sub("", line)


def assert_prompted_times(prompted: io.StringIO, times: int):
    __tracebackhide__ = True
    text = _escape_ansi(prompted.getvalue())
    lines = list(filter(None, text.split(": ")))
    assert len(lines) == times


@mark.parametrize(
    "answer,expected",
    [
        ("Alice\n", "Alice"),
        ("\n", "John Doe"),
    ],
)
def test_prompt_with_default(answer: str, expected: str):
    with replace_stdin(answer) as _:
        assert term.prompt("What's your name?", default="John Doe") == expected


@mark.parametrize(
    "answers,expected,times",
    [
        (["Alice"], "Alice", 1),
        (["", "", "Alice"], "Alice", 3),
    ],
)
def test_prompt_with_no_default(answers: list[str], expected: str, times: int):
    with replace_stdin(answers) as _, replace_stdout() as stdout:
        assert term.prompt("What's your name?") == expected
        assert_prompted_times(stdout, times)


@mark.parametrize(
    "answer,parser,_type",
    [
        ("Alice", str, str),
        ("42", int, int),
        ("42 days", timedelta, timedelta),
        ("Yes", bool, bool),
        ("N", bool, bool),
        ("2021-01-01", date, date),
        ("2021-01-01T00:00:00", datetime, datetime),
    ],
    ids=[
        "Str",
        "Int",
        "TimeDelta",
        "Bool Full",
        "Bool Short",
        "Date",
        "DateTime",
    ],
)
def test_prompt_with_parser(answer: str, parser: Parser, _type: type):
    with replace_stdin(answer) as _:
        res = term.prompt("Some prompt", parser=parser)
        assert isinstance(res, _type)


@mark.parametrize(
    "answer,_type",
    [
        ("Alice", str),
        ("42", int),
        ("42 days", timedelta),
        ("2021-01-01", date),
        ("2021-01-01T00:00:00", datetime),
    ],
    ids=[
        "str",
        "int",
        "timedelta",
        "date",
        "datetime",
    ],
)
def test_prompt_with_native_type(answer: str, _type: type):
    with replace_stdin(answer) as _:
        res = term.prompt("Some prompt", parser=_type)
        assert isinstance(res, _type)


@mark.parametrize(
    "answer,parser",
    [
        ("Alice", int),
        ("42 days", int),
        ("42 asd", timedelta),
        ("42", timedelta),
        ("42", bool),
        ("202-01-01", date),
        ("2021-01-01T00:00", datetime),
    ],
    ids=[
        "Str as Int",
        "TimeDelta as Int",
        "Invalid TimeDelta",
        "Int as TimeDelta",
        "Int as Bool",
        "Invalid Date",
        "Invalid DateTime",
    ],
)
def test_prompt_with_parser_fails(answer: str, parser: Parser):
    with replace_stdin(answer) as _, pytest.raises(MaxAttemptsException):
        term.prompt("Some prompt", parser=parser, max_attempts=1)


def test_prompt_with_good_parser():
    with replace_stdin("2") as _:
        res = term.prompt("Some prompt", parser=lambda x: int(x) * 2)
        assert res == 4


def _raise_error(x: int) -> None:
    raise ValueError(f"Invalid number {x}")


def test_prompt_with_bad_validate():
    with replace_stdin("2") as _, pytest.raises(MaxAttemptsException):
        term.prompt("Some prompt", parser=_raise_error, max_attempts=1)


def test_prompt_with_provided():
    with replace_stdin() as _:
        res = term.prompt("Some prompt", parser=int, provided=42)
        assert res == 42
        assert isinstance(res, int)
