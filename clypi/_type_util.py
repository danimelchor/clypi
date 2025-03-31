import inspect
import typing as t
from enum import Enum
from types import NoneType, UnionType

P = t.ParamSpec("P")
R = t.TypeVar("R")


def ignore_annotated(fun: t.Callable[P, R]) -> t.Callable[P, R]:
    def inner(*args: P.args, **kwargs: P.kwargs) -> R:
        if t.get_origin(args[0]) == t.Annotated:
            args_ls = list(args)
            args_ls[0] = t.get_args(args[0])[0]
            args = tuple(args_ls)  # type: ignore
        return fun(*args, **kwargs)

    return inner


@ignore_annotated
def is_list(_type: t.Any) -> t.TypeGuard[list[t.Any]]:
    return t.get_origin(_type) in (list, t.Sequence)


@ignore_annotated
def list_inner(_type: t.Any) -> t.Any:
    return t.get_args(_type)[0]


@ignore_annotated
def is_tuple(_type: t.Any) -> t.TypeGuard[tuple[t.Any]]:
    return t.get_origin(_type) is tuple


@ignore_annotated
def tuple_inner(_type: t.Any) -> tuple[list[t.Any], int | None]:
    """
    Returns the list of types for the tuple and how many items
    it accepts
    """
    # TODO: can be made more efficient
    inner_types = list(t.get_args(_type))
    if inner_types[-1] is Ellipsis:
        return [inner_types[0]], None
    return inner_types, len(inner_types)


@ignore_annotated
def is_union(_type: t.Any) -> t.TypeGuard[UnionType]:
    return t.get_origin(_type) in (UnionType, t.Union)


@ignore_annotated
def union_inner(_type: t.Any) -> list[t.Any]:
    return list(t.get_args(_type))


@ignore_annotated
def is_literal(_type: t.Any) -> bool:
    return t.get_origin(_type) == t.Literal


@ignore_annotated
def is_optional(_type: t.Any) -> bool:
    """Check type for <type>|None"""
    if not is_union(_type):
        return False
    inner = union_inner(_type)
    if len(inner) != 2:
        return False
    if NoneType not in inner:
        return False
    return True


@ignore_annotated
def literal_inner(_type: t.Any) -> list[t.Any]:
    return list(t.get_args(_type))


@ignore_annotated
def tuple_size(_type: t.Any) -> float:
    args = _type.__args__
    if args[-1] is Ellipsis:
        return float("inf")
    return len(args)


@ignore_annotated
def is_none(_type: t.Any) -> t.TypeGuard[type[None]]:
    return _type is NoneType


@ignore_annotated
def is_enum(_type: t.Any) -> t.TypeGuard[type[Enum]]:
    return inspect.isclass(_type) and issubclass(_type, Enum)


@ignore_annotated
def has_metavar(_type: t.Any) -> bool:
    return is_enum(_type) or is_literal(_type)
