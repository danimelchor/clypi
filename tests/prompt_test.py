from __future__ import annotations

import datetime as dt
import io
import sys
import typing as t
from contextlib import contextmanager, suppress
from datetime import date, datetime, timedelta
from enum import Enum

import pytest
from pytest import mark

import clypi
from clypi import AbortException, MaxAttemptsException, get_config


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


def assert_prompted_times(prompted: io.StringIO, times: int):
    __tracebackhide__ = True
    text = prompted.getvalue()
    lines = list(filter(None, text.split(": ")))
    assert len(lines) == times


def _raise_error(x: str | list[str]) -> None:
    raise ValueError(f"Invalid number {x}")


class _TestEnum(Enum):
    QA = 1
    PROD = 2


class TestCase:
    def setup_method(self):
        conf = get_config()
        conf.help_on_fail = False
        conf.nice_errors = tuple()
        conf.disable_colors = True

    @mark.parametrize(
        "expected",
        [True, False],
    )
    def test_confirm_with_default(self, expected: bool):
        with replace_stdin("\n") as _:
            assert clypi.confirm("What's your name?", default=expected) == expected

    @mark.parametrize(
        "answer, expected",
        [
            ("y", True),
            ("Yes", True),
            ("true", True),
            ("N", False),
            ("no", False),
            ("False", False),
        ],
    )
    def test_confirm(self, answer: str, expected: bool):
        with replace_stdin(answer) as _:
            assert clypi.confirm("What's your name?") == expected

    def test_confirm_aborts(self):
        with replace_stdin("n") as _:
            with pytest.raises(AbortException):
                _ = clypi.confirm("What's your name?", abort=True)

    @mark.parametrize(
        "answer,expected",
        [
            ("Alice\n", "Alice"),
            ("\n", "John Doe"),
        ],
    )
    def test_prompt_with_default(self, answer: str, expected: str):
        with replace_stdin(answer) as _:
            assert clypi.prompt("What's your name?", default="John Doe") == expected

    @mark.parametrize(
        "answers,expected,times",
        [
            (["Alice"], "Alice", 1),
            (["", "", "Alice"], "Alice", 3),
        ],
    )
    def test_prompt_with_no_default(
        self, answers: list[str], expected: str, times: int
    ):
        with replace_stdin(answers) as _, replace_stdout() as stdout:
            assert clypi.prompt("What's your name?") == expected
            assert_prompted_times(stdout, times)

    def test_prompt_with_parser(self):
        with replace_stdin("42") as _:
            res = clypi.prompt("Some prompt", parser=int)
            assert isinstance(res, int)

    @mark.parametrize(
        "answer,parser",
        [
            ("Alice", int),
            ("42 days", int),
            ("42 asd", timedelta),
            ("42", timedelta),
            ("202-01-01", date),
            ("2021-01-01T00:00", datetime),
            ("1 q", timedelta | None),
        ],
        ids=[
            "Str as Int",
            "TimeDelta as Int",
            "Invalid TimeDelta",
            "Int as TimeDelta",
            "Invalid Date",
            "Invalid DateTime",
            "Invalid TimeDelta or None",
        ],
    )
    def test_prompt_with_parser_fails(self, answer: str, parser: type):
        with replace_stdin(answer) as _, pytest.raises(MaxAttemptsException):
            clypi.prompt("Some prompt", parser=parser, max_attempts=1)

    def test_prompt_with_good_parser(self):
        with replace_stdin("2") as _:
            res = clypi.prompt(
                "Some prompt",
                parser=lambda x: int(x) * 2 if isinstance(x, str) else len(x),
            )
            assert res == 4

    def test_prompt_with_bad_validate(self):
        with replace_stdin("2") as _, pytest.raises(MaxAttemptsException):
            clypi.prompt("Some prompt", parser=_raise_error, max_attempts=1)

    @mark.parametrize(
        "default,expected",
        [
            (False, "y/N"),
            (True, "Y/n"),
            (_TestEnum.QA, "qa"),
            (_TestEnum.PROD, "prod"),
            (dt.datetime(2025, 1, 1), "2025-01-01 00:00:00"),
            (dt.timedelta(days=1), "1 day, 0:00:00"),
        ],
    )
    def test_prompt_default_repr(self, default: t.Any, expected: str):
        with (
            replace_stdin(["", ""]) as _,
            replace_stdout() as stdout,
            suppress(MaxAttemptsException),
        ):
            clypi.prompt("Some prompt", max_attempts=1, default=default)
            assert stdout.getvalue() == f"Some prompt [{expected}]: "
