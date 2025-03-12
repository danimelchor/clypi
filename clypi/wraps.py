import typing as t

from clypi._util import UNSET, Unset

OverflowStyle = t.Literal["ellipsis", "wrap"]


def wrap(
    s: str, width: int, overflow_style: OverflowStyle | Unset = UNSET
) -> list[str]:
    """
    If a string is larger than width, it either wraps the string into new
    lines or appends an ellipsis
    """
    s = s.rstrip()
    if len(s) <= width:
        return [s]

    if overflow_style is UNSET:
        from clypi.configuration import get_config

        overflow_style = get_config().overflow_style

    if overflow_style == "ellipsis":
        return [s[: width - 1] + "…"]

    res = []
    for i in range(0, len(s), width):
        res.append(s[i : i + width])

    return res
