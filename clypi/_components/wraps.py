import typing as t

from clypi._util import UNSET, Unset, visible_width

OverflowStyle = t.Literal["ellipsis", "wrap"]


def wrap(
    s: str, width: int, overflow_style: OverflowStyle | Unset = UNSET
) -> list[str]:
    """
    If a string is larger than width, it either wraps the string into new
    lines or appends an ellipsis
    """
    if visible_width(s) <= width:
        return [s]

    if overflow_style is UNSET:
        from clypi._configuration import get_config

        overflow_style = get_config().overflow_style

    if overflow_style == "ellipsis":
        return [s[: width - 1] + "…"]

    res: list[str] = []
    while s:
        res.append(s[:width])
        s = s[width:].strip()

    return res
