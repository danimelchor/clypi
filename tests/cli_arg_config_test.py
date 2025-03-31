import typing as t

import pytest

from clypi._cli.arg_config import Nargs, _get_nargs  # type: ignore


@pytest.mark.parametrize(
    "_type,expected",
    [
        (bool, 0),
        (t.Literal["a"], 1),
        (t.Optional[bool], 1),
        (list[bool], "*"),
        (list[bool] | None, "*"),
        (list[bool] | None, "*"),
        (bool | int, 1),
    ],
)
def test_get_nargs(_type: t.Any, expected: Nargs):
    assert _get_nargs(_type) == expected
