from __future__ import annotations

from enum import Enum, auto

from clypi.colors import remove_style


class Unset(Enum):
    TOKEN = auto()


UNSET = Unset.TOKEN


def visible_width(s: str) -> int:
    s = remove_style(s)
    return len(s)
