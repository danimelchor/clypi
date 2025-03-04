import typing as t

from clypi._data.boxes import Boxes as _Boxes
from clypi.colors import remove_style

Boxes = _Boxes


def _real_len(s: str) -> int:
    s = remove_style(s)
    return len(s)


def _ljust(s: str, width: int):
    len = _real_len(s)
    diff = max(0, width - len)
    return s + " " * diff


def _rjust(s: str, width: int):
    len = _real_len(s)
    diff = max(0, width - len)
    return " " * diff + s


def _center(s: str, width: int):
    len = _real_len(s)
    diff = max(0, width - len)
    right = diff // 2
    left = diff - right
    return " " * left + s + " " * right


AlignType: t.TypeAlias = t.Literal["left", "center", "right"]


def align(s: str, alignment: AlignType, width: int) -> str:
    if alignment == "left":
        return _ljust(s, width)
    if alignment == "right":
        return _rjust(s, width)
    return _center(s, width)
