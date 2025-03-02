import typing as t
from contextlib import suppress
from types import UnionType

from term._cli import type_util


def dash_to_snake(s: str) -> str:
    return s.replace("-", "_")


def parse_as_attr(arg: str) -> tuple[bool, str]:
    if arg.startswith("--"):
        arg = arg.removeprefix("--")
        return True, dash_to_snake(arg)

    if arg.startswith("-"):
        arg = arg.removeprefix("-")
        return True, dash_to_snake(arg)

    return False, arg


def _parse_builtin(builtin: type, value: t.Any):
    if isinstance(value, list):
        value = value[0]
    return builtin(value)


def _parse_value_as_list(value: t.Any, _type: t.Any):
    if not isinstance(value, list):
        raise ValueError(f"Don't know how to parse {value} as {_type}")

    inner_type = _type.__args__[0]
    return [parse_value_as_type(x, inner_type) for x in value]


def parse_value_as_type(value: t.Any, _type: t.Any):
    if _type in (int, float, str, bool):
        return _parse_builtin(_type, value)

    if type_util.is_collection(_type):
        return _parse_value_as_list(value, _type)

    if isinstance(_type, UnionType):
        for a in _type.__args__:
            with suppress(ValueError, TypeError):
                return parse_value_as_type(value, a)

    raise ValueError(f"Don't know how to parse as {_type}")
