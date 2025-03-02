import re
import typing as t
from dataclasses import dataclass
from pathlib import Path
from types import NoneType, UnionType

from term._cli import type_util


class UnparseableException(Exception):
    pass


def dash_to_snake(s: str) -> str:
    return re.sub(r"^-+", "", s).replace("-", "_")


def snake_to_dash(s: str) -> str:
    return s.replace("_", "-")


def normalize_args(args: t.Sequence[str]):
    new_args = []
    for a in args:
        if a.startswith("-") and "=" in a:
            new_args.extend(a.split("=", 1))
        else:
            new_args.append(a)
    return new_args


@dataclass
class Arg:
    value: str
    orig: str
    arg_type: t.Literal["opt", "short-opt", "pos"]

    def is_pos(self):
        return self.arg_type == "pos"

    def is_short_opt(self):
        return self.arg_type == "short-opt"


def parse_as_attr(arg: str) -> Arg:
    if arg.startswith("--") and len(arg) > 3:
        return Arg(value=dash_to_snake(arg), orig=arg, arg_type="opt")

    if arg.startswith("-") and len(arg) == 2:
        return Arg(value=dash_to_snake(arg), orig=arg, arg_type="short-opt")

    return Arg(value=arg, orig=arg, arg_type="pos")


def _parse_builtin(builtin: type, value: t.Any):
    if isinstance(value, list):
        value = value[0]
    return builtin(value)


def _parse_value_as_list(value: t.Any, _type: t.Any):
    if not isinstance(value, list):
        raise ValueError(
            f"Don't know how to parse {value} as {type_util.type_to_str(_type)}"
        )

    inner_type = _type.__args__[0]
    return [parse_value_as_type(x, inner_type) for x in value]


def _parse_value_as_tuple(value: t.Any, _type: t.Any):
    if not isinstance(value, tuple | list):
        raise ValueError(
            f"Don't know how to parse {value} as {type_util.type_to_str(_type)}"
        )

    # TODO: can be made more efficient
    inner_types = _type.__args__
    if inner_types[-1] is Ellipsis:
        inner_types = [inner_types[0]] * len(value)

    if len(inner_types) > len(value):
        raise ValueError(
            f"Not enough arguments for type {type_util.type_to_str(_type)} (got {value})"
        )

    ret = []
    for val, inner_type in zip(value, inner_types):
        ret.append(parse_value_as_type(val, inner_type))
    return tuple(ret)


def _parse_value_as_literal(value: t.Any, _type: t.Any):
    if isinstance(value, list):
        value = value[0]

    for a in _type.__args__:
        if a == value:
            return value

    raise ValueError(
        f"Value {value} is not a valid choice between {type_util.type_to_str(_type)}"
    )


def parse_value_as_type(value: t.Any, _type: t.Any):
    if _type in (int, float, str, Path, bool):
        return _parse_builtin(_type, value)

    if type_util.is_collection(_type):
        return _parse_value_as_list(value, _type)

    if type_util.is_tuple(_type):
        return _parse_value_as_tuple(value, _type)

    errors = []
    if isinstance(_type, UnionType):
        for a in _type.__args__:
            try:
                return parse_value_as_type(value, a)
            except (ValueError, TypeError) as e:
                errors.append(e)
            except UnparseableException:
                pass

    if t.get_origin(_type) == t.Literal:
        return _parse_value_as_literal(value, _type)

    if _type is NoneType and value is None:
        return None

    if errors:
        raise errors[0]

    raise UnparseableException(
        f"Don't know how to parse as {type_util.type_to_str(_type)} ({type(_type)})"
    )


Nargs: t.TypeAlias = t.Literal["*", "+"] | float


@dataclass
class CurrentCtx:
    name: str = ""
    nargs: Nargs = 0

    def has_more(self) -> bool:
        if isinstance(self.nargs, float):
            return self.nargs > 0
        return True

    def needs_more(self) -> bool:
        if isinstance(self.nargs, float):
            return self.nargs > 0
        elif self.nargs == "+":
            return True
        return False

    def use(self) -> None:
        if isinstance(self.nargs, float):
            self.nargs -= 1
        elif self.nargs == "+":
            self.nargs = "*"

    def __bool__(self) -> bool:
        return bool(self.name)
