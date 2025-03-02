import inspect
import typing as t
from types import NoneType, UnionType


def is_collection(_type: t.Any) -> bool:
    return t.get_origin(_type) in (list, t.Sequence)


def is_tuple(_type: t.Any) -> bool:
    return t.get_origin(_type) is tuple


def tuple_size(_type: t.Any) -> float:
    args = _type.__args__
    if args[-1] is Ellipsis:
        return float("inf")
    return len(args)


def remove_optionality(_type: t.Any) -> t.Any:
    if not isinstance(_type, UnionType):
        return _type

    new_args = []
    for arg in _type.__args__:
        if arg is not NoneType:
            new_args.append(arg)

    if len(new_args) == 1:
        return new_args[0]

    return t.Union[*new_args]


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

    if isinstance(_type, UnionType):
        return "[" + "|".join(type_to_str(tp) for tp in _type.__args__) + "]"

    if is_tuple(_type):
        if _type.__args__[1] is Ellipsis:
            return "(" + type_to_str(_type.__args__[0]) + ", ...)"
        else:
            return "(" + ", ".join(type_to_str(tp) for tp in _type.__args__) + ")"

    if is_collection(_type):
        return "list[" + ", ".join(type_to_str(tp) for tp in _type.__args__) + "]"

    return str(_type)
