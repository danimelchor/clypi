import typing as t
from types import NoneType

import pytest

from clypi._type_util import (
    is_list,
    is_literal,
    is_optional,
    is_tuple,
    is_union,
    literal_inner,
    tuple_inner,
    union_inner,
)


@pytest.mark.parametrize(
    "_type",
    [
        list[str],
        list[tuple[int]],
        t.Annotated[list[str], 1],
    ],
)
def test_is_list(_type: t.Any):
    assert is_list(_type)


@pytest.mark.parametrize(
    "_type",
    [
        tuple[str],
        tuple[list[int]],
        t.Annotated[tuple[str], 1],
    ],
)
def test_is_tuple(_type: t.Any):
    assert is_tuple(_type)


@pytest.mark.parametrize(
    "_type",
    [
        str | int,
        str | int | bool,
        t.Union[int, bool],
        t.Annotated[str | int, 1],
        t.Annotated[t.Union[str | int], 1],
    ],
)
def test_is_union(_type: t.Any):
    assert is_union(_type)


@pytest.mark.parametrize(
    "_type",
    [
        t.Literal["a"],
        t.Literal["a", 1],
        t.Annotated[t.Literal["a", 1], 1],
    ],
)
def test_is_literal(_type: t.Any):
    assert is_literal(_type)


@pytest.mark.parametrize(
    "_type",
    [bool | None, None | bool, t.Optional[bool]],
)
def test_is_optional(_type: t.Any):
    assert is_optional(_type)


@pytest.mark.parametrize(
    "_type,inner_t,num",
    [
        (tuple[str], [str], 1),
        (tuple[str, int], [str, int], 2),
        (tuple[str, ...], [str], None),
    ],
)
def test_tuple_inner(_type: t.Any, inner_t: t.Any, num: int):
    assert tuple_inner(_type) == (inner_t, num)


@pytest.mark.parametrize(
    "_type,inner_t",
    [
        (str | int, [str, int]),
        (str | int | None, [str, int, NoneType]),
        (t.Union[str, int, None], [str, int, NoneType]),
    ],
)
def test_union_inner(_type: t.Any, inner_t: t.Any):
    assert union_inner(_type) == inner_t


@pytest.mark.parametrize(
    "_type,inner",
    [
        (t.Literal["a"], ["a"]),
        (t.Literal["a", 1], ["a", 1]),
    ],
)
def test_literal_inner(_type: t.Any, inner: t.Any):
    assert literal_inner(_type) == inner
