from __future__ import annotations

import enum
import re
import typing as t
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path as _Path

from typing_extensions import override

from clypi._cli import type_util as tu

T = t.TypeVar("T", covariant=True)
X = t.TypeVar("X")
Y = t.TypeVar("Y")


class UnparseableException(Exception):
    pass


class Parser(t.Protocol[T]):
    def __call__(self, raw: str | list[str], /) -> T: ...


class CannotParseAs(Exception):
    def __init__(self, value: t.Any, parser: Parser) -> None:
        message = f"Cannot parse {value!r} as {parser}"
        super().__init__(message)


class ClypiParser(ABC, t.Generic[X]):
    @abstractmethod
    def __call__(self, raw: str | list[str], /) -> X: ...

    def _repr_args(self) -> str | None:
        return None

    def __repr__(self):
        name = self.__class__.__name__.lower()
        args_str = self._repr_args()
        if args_str is None:
            return name
        return f"{name}({args_str})"

    def __or__(self, other: ClypiParser[Y]) -> Union[X, Y]:
        return Union(self, other)

    def __eq__(self, other: t.Any):
        if not isinstance(other, ClypiParser):
            return False
        if self.__class__ != other.__class__:
            return False
        # TODO: fix this comparison. Only for tests so it's ok for now
        return str(self) == str(other)


class Int(ClypiParser[int]):
    def __call__(self, raw: str | list[str], /) -> int:
        if isinstance(raw, list):
            raise CannotParseAs(raw, self)
        if int(raw) != float(raw):
            raise ValueError(f"The value {raw!r} is not a valid integer.")
        return int(raw)


class Float(ClypiParser[float]):
    def __call__(self, raw: str | list[str], /) -> float:
        if isinstance(raw, list):
            raise CannotParseAs(raw, self)
        return float(raw)


class Bool(ClypiParser[bool]):
    TRUE_BOOL_STR_LITERALS: set[str] = {"true", "yes", "y"}
    FALSE_BOOL_STR_LITERALS: set[str] = {"false", "no", "n"}

    def __call__(self, raw: str | list[str], /) -> bool:
        if isinstance(raw, list):
            raise CannotParseAs(raw, self)

        raw_lower = raw.lower()
        both = self.TRUE_BOOL_STR_LITERALS | self.FALSE_BOOL_STR_LITERALS
        if raw_lower not in both:
            raise ValueError(
                f"The string {raw!r} is not valid boolean! The only allowed values are: {both}."
            )
        return raw_lower in self.TRUE_BOOL_STR_LITERALS


class Str(ClypiParser[str]):
    def __call__(self, raw: str | list[str], /) -> str:
        if isinstance(raw, list):
            raise CannotParseAs(raw, self)
        return raw


class DateTime(ClypiParser[datetime]):
    def __call__(self, raw: str | list[str], /) -> datetime:
        from dateutil.parser import parse

        if isinstance(raw, list):
            raise CannotParseAs(raw, self)
        return parse(raw)


class TimeDelta(ClypiParser[timedelta]):
    TIMEDELTA_UNITS = {
        ("weeks", "week", "w"): "weeks",
        ("days", "day", "d"): "days",
        ("hours", "hour", "h"): "hours",
        ("minutes", "minute", "m"): "minutes",
        ("seconds", "second", "s"): "seconds",
        ("milliseconds", "millisecond", "ms"): "milliseconds",
        ("microseconds", "microsecond", "us"): "microseconds",
    }
    TIMEDELTA_REGEX = re.compile(r"^(\d+)\s*(\w+)$")

    def __call__(self, raw: str | list[str], /) -> timedelta:
        if isinstance(raw, timedelta):
            return raw

        if not isinstance(raw, str):
            raise ValueError(
                f"Cannot parse {raw!r} as timedelta. Expected str or timedelta, got {type(raw).__name__}"
            )

        match = self.TIMEDELTA_REGEX.match(raw)
        if match is None:
            raise ValueError(f"Invalid timedelta {raw!r}.")

        value, unit = match.groups()
        for units in self.TIMEDELTA_UNITS:
            if unit in units:
                return timedelta(**{self.TIMEDELTA_UNITS[units]: int(value)})

        raise ValueError(f"Invalid timedelta {raw!r}.")


class Path(ClypiParser[_Path]):
    def __init__(self, *, exists: bool = False) -> None:
        self.exists = exists

    def __call__(self, raw: str | list[str], /) -> _Path:
        if isinstance(raw, list):
            raise CannotParseAs(raw, self)
        p = _Path(raw)

        # Validations on the path
        if self.exists and not p.exists():
            raise ValueError(f"File {p.resolve()} does not exist!")

        return p


class List(ClypiParser[list[X]]):
    def __init__(self, inner: Parser[X]) -> None:
        self._inner = inner

    def __call__(self, raw: str | list[str], /) -> list[X]:
        if isinstance(raw, str):
            raw = raw.split(",")
        return [self._inner(item) for item in raw]

    @override
    def _repr_args(self):
        return str(self._inner)


class Tuple(ClypiParser[tuple[t.Any]]):
    def __init__(self, *inner: Parser[t.Any], num: int | None = None) -> None:
        self._inner = list(inner)
        self._num = num

    # TODO: can we return the right type here?
    def __call__(self, raw: str | list[str], /) -> tuple[t.Any, ...]:
        if isinstance(raw, str):
            raw = raw.split(",")

        if self._num and len(raw) != self._num:
            raise ValueError(
                f"Expected tuple of length {self._num} but instead got {len(raw)} items"
            )

        # Get all parsers for each item in the tuple (or reuse if tuple[T, ...])
        if not self._num:
            inner_parsers = [self._inner[0]] * len(raw)
        else:
            inner_parsers = self._inner

        # Parse each item with it's corresponding parser
        return tuple(parser(raw_item) for parser, raw_item in zip(inner_parsers, raw))

    @override
    def _repr_args(self) -> str | None:
        return ", ".join(str(it) for it in self._inner)


class Union(ClypiParser[t.Union[X, Y]]):
    def __init__(self, left: Parser[X], right: Parser[Y]) -> None:
        self._left = left
        self._right = right

    def __call__(self, raw: str | list[str], /) -> t.Union[X, Y]:
        try:
            return self._left(raw)
        except Exception:
            return self._right(raw)

    def _parts(self):
        """
        Some recursive magic here to "flatten" unions
        """
        left = self._left._parts() if isinstance(self._left, Union) else str(self._left)
        right = (
            self._right._parts() if isinstance(self._right, Union) else str(self._right)
        )
        return f"{left}|{right}"

    def __repr__(self):
        return "(" + self._parts() + ")"


class Literal(ClypiParser[t.Any]):
    def __init__(self, *values: t.Any) -> None:
        self._values = values

    # TODO: can we return the right type here?
    def __call__(self, raw: str | list[str], /) -> t.Any:
        for v in self._values:
            if v == raw:
                return v
        raise CannotParseAs(raw, self)

    def __repr__(self):
        values = "|".join(str(v) for v in self._values)
        return "{" + values + "}"


class NoneParser(ClypiParser[None]):
    def __call__(self, raw: str | list[str], /) -> t.Any:
        raise UnparseableException()

    def __repr__(self):
        return "NONE"


class Enum(ClypiParser[type[enum.Enum]]):
    def __init__(self, _type: type[enum.Enum]) -> None:
        self._type = _type

    def __call__(self, raw: str | list[str], /) -> t.Any:
        if not isinstance(raw, str):
            raise CannotParseAs(raw, self)

        for enum_val in self._type:
            if raw.lower() == enum_val.name.lower():
                return enum_val

        raise ValueError(f"Value {raw} is not a valid choice between {self}")

    def __repr__(self):
        values = "|".join(v.name.lower() for v in self._type)
        return "{" + values + "}"


@tu.ignore_annotated
def from_type(_type: type) -> Parser[t.Any]:
    if _type is bool:
        return Bool()

    if _type is int:
        return Int()

    if _type is float:
        return Float()

    if _type is str:
        return Str()

    if _type is _Path:
        return Path()

    if _type is datetime:
        return DateTime()

    if _type is timedelta:
        return TimeDelta()

    if tu.is_list(_type):
        inner = from_type(tu.list_inner(_type))
        return List(inner)

    if tu.is_tuple(_type):
        inner_types, num = tu.tuple_inner(_type)
        inner_parsers = [from_type(it) for it in inner_types]
        return Tuple(*inner_parsers, num=num)

    if tu.is_union(_type):
        union_inner = tu.union_inner(_type)
        trav = Union(from_type(union_inner[0]), from_type(union_inner[1]))
        for rest in union_inner[2:]:
            trav = Union(trav, from_type(rest))
        return trav

    if tu.is_literal(_type):
        return Literal(*tu.literal_inner(_type))

    if tu.is_none(_type):
        return NoneParser()

    if tu.is_enum(_type):
        return Enum(_type)

    raise UnparseableException(f"Don't know how to parse as {_type}")
