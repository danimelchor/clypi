from __future__ import annotations

import enum
import re
import typing as t
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path as _Path

from clypi import _type_util as tu

T = t.TypeVar("T", covariant=True)
X = t.TypeVar("X")
Y = t.TypeVar("Y")


class UnparseableException(Exception):
    pass


class Parser(t.Protocol[T]):
    def __call__(self, raw: str | list[str], /) -> T: ...


CATCH_ERRORS: tuple[type[Exception], ...] = (
    ValueError,
    TypeError,
    IndexError,
)


class CannotParseAs(Exception):
    def __init__(self, value: t.Any, parser: Parser[t.Any]) -> None:
        message = f"Cannot parse {value!r} as {parser}"
        super().__init__(message)


class ClypiParser(ABC, t.Generic[X]):
    name: str | None = None

    @abstractmethod
    def __call__(self, raw: str | list[str], /) -> X: ...

    def __or__(self, other: ClypiParser[Y]) -> Union[X, Y]:
        return Union(self, other)

    def __eq__(self, other: t.Any):
        if not isinstance(other, ClypiParser):
            return False
        if self.__class__ != other.__class__:
            return False
        # TODO: fix this comparison. Only for tests so it's ok for now
        return str(self) == str(other)


def a(cond: bool, value: t.Any, error_msg: str):
    """
    Short hand for assertions with error messages
    """
    if not cond:
        raise ValueError(f"{value} {error_msg}")


@dataclass
class Int(ClypiParser[int]):
    gt: int | None = None
    gte: int | None = None
    lt: int | None = None
    lte: int | None = None
    max: int | None = None
    min: int | None = None
    positive: bool = False
    nonpositive: bool = False
    negative: bool = False
    nonnegative: bool = False

    def __call__(self, raw: str | list[str], /) -> int:
        if isinstance(raw, list):
            raise CannotParseAs(raw, self)
        if int(raw) != float(raw):
            raise ValueError(f"The value {raw!r} is not a valid integer.")

        parsed = int(raw)
        if self.gt is not None:
            a(parsed > self.gt, parsed, f"is not greater than {self.gt}")
        if self.gte is not None:
            a(parsed >= self.gte, parsed, f"is not greater than or equal to {self.gte}")
        if self.lt is not None:
            a(parsed < self.lt, parsed, f"is not less than {self.lt}")
        if self.lte is not None:
            a(parsed <= self.lte, parsed, f"is not less than or equal to {self.lte}")
        if self.max is not None:
            a(parsed <= self.max, parsed, f"is not less than or equal to {self.max}")
        if self.min is not None:
            a(parsed >= self.min, parsed, f"is not greater than or equal to {self.min}")
        if self.positive:
            a(parsed > 0, parsed, "is not positive")
        if self.nonpositive:
            a(parsed <= 0, parsed, "is not non-positive")
        if self.negative:
            a(parsed < 0, parsed, "is not negative")
        if self.nonnegative:
            a(parsed >= 0, parsed, "is non non-negative")

        return parsed

    def __repr__(self) -> str:
        return "integer"


@dataclass
class Float(ClypiParser[float]):
    gt: float | None = None
    gte: float | None = None
    lt: float | None = None
    lte: float | None = None
    max: float | None = None
    min: float | None = None
    positive: bool = False
    nonpositive: bool = False
    negative: bool = False
    nonnegative: bool = False

    def __call__(self, raw: str | list[str], /) -> float:
        if isinstance(raw, list):
            raise CannotParseAs(raw, self)

        parsed = float(raw)
        if self.gt is not None:
            a(parsed > self.gt, parsed, f"is not greater than {self.gt}")
        if self.gte is not None:
            a(parsed >= self.gte, parsed, f"is not greater than or equal to {self.gte}")
        if self.lt is not None:
            a(parsed < self.lt, parsed, f"is not less than {self.lt}")
        if self.lte is not None:
            a(parsed <= self.lte, parsed, f"is not less than or equal to {self.lte}")
        if self.max is not None:
            a(parsed <= self.max, parsed, f"is not less than or equal to {self.max}")
        if self.min is not None:
            a(parsed >= self.min, parsed, f"is not greater than or equal to {self.min}")
        if self.positive:
            a(parsed > 0, parsed, "is not positive")
        if self.nonpositive:
            a(parsed <= 0, parsed, "is not non-positive")
        if self.negative:
            a(parsed < 0, parsed, "is not negative")
        if self.nonnegative:
            a(parsed >= 0, parsed, "is non non-negative")
        return parsed

    def __repr__(self) -> str:
        return "float"


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

    def __repr__(self):
        return "{yes|no}"

    def _parts(self):
        """
        Required so that it can be flattened when inside unions or literals
        """
        return ["yes", "no"]


@dataclass
class Str(ClypiParser[str]):
    length: int | None = None
    max: int | None = None
    min: int | None = None
    startswith: str | None = None
    endswith: str | None = None
    regex: str | None = None
    regex_group: int | None = None

    def __call__(self, raw: str | list[str], /) -> str:
        if isinstance(raw, list):
            raise CannotParseAs(raw, self)

        if self.length is not None:
            a(len(raw) == self.length, len, f"'s length is not {self.length}")
        if self.max is not None:
            a(len(raw) <= self.max, len, f"'s length is not less than {self.max}")
        if self.min is not None:
            a(len(raw) >= self.min, len, f"'s length is not greater than {self.min}")
        if self.startswith is not None:
            a(
                raw.startswith(self.startswith),
                raw,
                f"does not start with {self.startswith}",
            )
        if self.endswith is not None:
            a(raw.endswith(self.endswith), raw, f"does not end with {self.endswith}")
        if self.regex is not None:
            m = re.search(self.regex, raw)
            a(m is not None, raw, f"does not match the regular expression {self.regex}")
            if m and self.regex_group is not None:
                val = m.group(self.regex_group)
                assert isinstance(val, str)
                raw = val

        return raw

    def __repr__(self) -> str:
        return "text"


@dataclass
class DateTime(ClypiParser[datetime]):
    tz: timezone | None = None

    def __call__(self, raw: str | list[str], /) -> datetime:
        from dateutil.parser import parse

        if isinstance(raw, list):
            raise CannotParseAs(raw, self)

        parsed = parse(raw)
        if self.tz is not None:
            parsed = parsed.astimezone(self.tz)

        return parsed

    def __repr__(self) -> str:
        return "datetime"


@dataclass
class TimeDelta(ClypiParser[timedelta]):
    gt: timedelta | None = None
    gte: timedelta | None = None
    lt: timedelta | None = None
    lte: timedelta | None = None
    max: timedelta | None = None
    min: timedelta | None = None

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
        parsed = None
        for units in self.TIMEDELTA_UNITS:
            if unit in units:
                parsed = timedelta(**{self.TIMEDELTA_UNITS[units]: int(value)})
                break

        if parsed is None:
            raise ValueError(f"Invalid timedelta {raw!r}.")

        if self.gt is not None:
            a(parsed > self.gt, parsed, f"is not greater than {self.gt}")
        if self.gte is not None:
            a(parsed >= self.gte, parsed, f"is not greater than or equal to {self.gte}")
        if self.lt is not None:
            a(parsed < self.lt, parsed, f"is not less than {self.lt}")
        if self.lte is not None:
            a(parsed <= self.lte, parsed, f"is not less than or equal to {self.lte}")
        if self.max is not None:
            a(parsed <= self.max, parsed, f"is not less than or equal to {self.max}")
        if self.min is not None:
            a(parsed >= self.min, parsed, f"is not greater than or equal to {self.min}")

        return parsed

    def __repr__(self) -> str:
        return "timedelta"


@dataclass
class Path(ClypiParser[_Path]):
    exists: bool = False

    def __call__(self, raw: str | list[str], /) -> _Path:
        if isinstance(raw, list):
            raise CannotParseAs(raw, self)
        p = _Path(raw)

        # Validations on the path
        if self.exists and not p.exists():
            raise ValueError(f"File {p.resolve()} does not exist!")

        return p

    def __repr__(self) -> str:
        return "path"


class List(ClypiParser[list[X]]):
    def __init__(self, inner: Parser[X]) -> None:
        self._inner = inner

    def __call__(self, raw: str | list[str], /) -> list[X]:
        if isinstance(raw, str):
            raw = raw.split(",")
        return [self._inner(item) for item in raw]

    def __repr__(self) -> str:
        return f"list({self._inner})"


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

    def __repr__(self) -> str:
        args = ", ".join(str(it) for it in self._inner)
        return f"tuple({args})"


class Union(ClypiParser[t.Union[X, Y]]):
    def __init__(self, left: Parser[X], right: Parser[Y]) -> None:
        self._left = left
        self._right = right

    def __call__(self, raw: str | list[str], /) -> t.Union[X, Y]:
        # Str classes are catch-alls, so we de-prioritize them in unions
        # so that the other type is parsed first
        first, second = self._left, self._right
        if isinstance(first, Str):
            first, second = self._right, self._left

        try:
            return first(raw)
        except Exception:
            return second(raw)

    def _parts(self):
        """
        Some recursive magic here to "flatten" unions
        """
        parts: list[str] = []
        if left_parts := getattr(self._left, "_parts", None):
            parts.extend(left_parts())
        else:
            parts.append(str(self._left))

        if right_parts := getattr(self._right, "_parts", None):
            parts.extend(right_parts())
        else:
            parts.append(str(self._right))

        return parts

    def __repr__(self):
        return "(" + "|".join(self._parts()) + ")"


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
    def __call__(self, raw: str | list[str], /) -> None:
        if not raw:
            return None
        if isinstance(raw, str) and raw.lower() == "none":
            return None
        raise UnparseableException()

    def __repr__(self):
        return "none"


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
