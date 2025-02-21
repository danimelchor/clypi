from __future__ import annotations

import builtins
import datetime as dt
import re
import typing as t
from abc import ABC, abstractmethod
from contextlib import suppress
from datetime import date, datetime, timedelta

from typing_extensions import override


class UnsupportedTypeException(Exception):
    pass


T = t.TypeVar("T")
P = t.TypeVar("P")


class Klass(ABC, t.Generic[T]):
    @abstractmethod
    def parse(self, x: str) -> T: ...

    def __call__(self, x: str) -> T:
        return self.parse(x)

    def __or__(self, other: Klass[P]) -> _Union[T, P]:
        return _Union(self, other)

    @override
    def __repr__(self):
        return self.__class__.__name__


L = t.TypeVar("L")
R = t.TypeVar("R")


class _Union(Klass[L | R], t.Generic[L, R]):
    def __init__(self, left: Klass[L], right: Klass[R]):
        self.left = left
        self.right = right
        super().__init__()

    @override
    def parse(self, x: str) -> L | R:
        try:
            return self.left(x)
        except ValueError:
            return self.right(x)

    @override
    def __repr__(self):
        return f"{self.left} | {self.right}"


class Str(Klass[str]):
    @override
    def parse(self, x: str) -> str:
        return x


class Int(Klass[int]):
    @override
    def parse(self, x: str) -> int:
        return int(x)


class Float(Klass[float]):
    @override
    def parse(self, x: str) -> float:
        return float(x)


class Bool(Klass[bool]):
    @override
    def parse(self, x: str) -> bool:
        if x.lower() in ("true", "yes", "y"):
            return True
        if x.lower() in ("false", "no", "n"):
            return False
        raise ValueError(f"Invalid boolean value: {x}")


class TimeDelta(Klass[timedelta]):
    @override
    def parse(self, x: str) -> timedelta:
        valid_timedelta_units = {
            ("d", "day", "days"): "days",
            ("h", "hour", "hours"): "hours",
            ("m", "minute", "minutes"): "minutes",
            ("w", "week", "weeks"): "weeks",
        }
        if (m := re.match(r"^(\d+)\s*([a-zA-Z]+)$", x)) is None:
            raise ValueError(f"Invalid timedelta: {x}")

        value, unit = m.groups()
        try:
            unit = next(v for k, v in valid_timedelta_units.items() if unit in k)
            return timedelta(**{unit: int(value)})
        except StopIteration:
            raise ValueError(f"Invalid timedelta unit: {unit}")


class DateTime(Klass[datetime]):
    def __init__(self, fmts: list[str] | None = None):
        self.fmts = fmts or ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"]
        super().__init__()

    @override
    def parse(self, x: str) -> datetime:
        for fmt in self.fmts:
            with suppress(ValueError):
                return datetime.strptime(x, fmt)
        raise ValueError(
            f"Invalid datetime. {x} does not match any of the formats: {self.fmts}"
        )


class Date(Klass[date]):
    def __init__(self, fmts: list[str] | None = None):
        self.fmts = fmts or ["%Y-%m-%d", "%Y/%m/%d"]
        super().__init__()

    @override
    def parse(self, x: str) -> date:
        for fmt in self.fmts:
            with suppress(ValueError):
                return datetime.strptime(x, fmt).date()
        raise ValueError(
            f"Invalid date. {x} does not match any of the formats: {self.fmts}"
        )


def parse_klass(value: t.Type[T] | Klass[T]) -> Klass[T]:
    """
    Convert a type to a Klass instance.

    E.g.: str | int -> _Union[Str, Int]
    """

    # Matches in Python are not very good yet so we need casts
    match value:
        case builtins.str:
            return t.cast(Klass[T], Str())
        case builtins.int:
            return t.cast(Klass[T], Int())
        case builtins.float:
            return t.cast(Klass[T], Float())
        case builtins.bool:
            return t.cast(Klass[T], Bool())
        case dt.timedelta:
            return t.cast(Klass[T], TimeDelta())
        case dt.datetime:
            return t.cast(Klass[T], DateTime())
        case dt.date:
            return t.cast(Klass[T], Date())
        case Klass():
            return value
        case _:
            raise UnsupportedTypeException(f"Unsupported type: {t} ({type(t)})")
