import inspect
import typing as t
from enum import Enum
from types import NoneType, UnionType


def ignore_annotated(fun: t.Callable[[t.Any], t.Any]):
    def inner(_type: t.Any):
        if t.get_origin(_type) == t.Annotated:
            _type = _type.__args__[0]
        return fun(_type)

    return inner


@ignore_annotated
def is_list(_type: t.Any) -> t.TypeGuard[list[t.Any]]:
    return t.get_origin(_type) in (list, t.Sequence)


@ignore_annotated
def is_tuple(_type: t.Any) -> t.TypeGuard[tuple[t.Any]]:
    return t.get_origin(_type) is tuple


@ignore_annotated
def tuple_size(_type: t.Any) -> float:
    args = _type.__args__
    if args[-1] is Ellipsis:
        return float("inf")
    return len(args)


@ignore_annotated
def remove_optionality(_type: t.Any) -> t.Any:
    if not isinstance(_type, UnionType):
        return _type

    new_args: list[t.Any] = []
    for arg in _type.__args__:
        if arg is not NoneType:
            new_args.append(arg)

    if len(new_args) == 1:
        return new_args[0]

    return t.Union[*new_args]


@ignore_annotated
def type_to_str(_type: t.Any) -> str:
    _map = {
        "bool": "boolean",
        "int": "integer",
        "float": "float",
        "str": "string",
        "Path": "Path",
    }
    if inspect.isclass(_type) and _type.__name__ in _map:
        return _map[_type.__name__]

    if t.get_origin(_type) is t.Literal:
        return "{" + "|".join(type_to_str(tp) for tp in _type.__args__) + "}"

    if inspect.isclass(_type) and issubclass(_type, Enum):
        return "{" + "|".join(tp.name for tp in _type) + "}"

    if isinstance(_type, UnionType):
        return "[" + "|".join(type_to_str(tp) for tp in _type.__args__) + "]"

    if is_tuple(_type):
        args = t.get_args(_type)
        if args[-1] is Ellipsis:
            return "(" + type_to_str(args[0]) + ", ...)"
        else:
            inner = ", ".join(type_to_str(tp) for tp in args)
            maybe_comma = "," if len(args) == 1 else ""  # E.g.: ("foo",)
            return "(" + inner + maybe_comma + ")"

    if is_list(_type):
        return "list[" + ", ".join(type_to_str(tp) for tp in t.get_args(_type)) + "]"

    return str(_type)
