from __future__ import annotations

import os
from enum import Enum, auto

from clypi._colors import remove_style


class Unset(Enum):
    TOKEN = auto()


UNSET = Unset.TOKEN


def visible_width(s: str) -> int:
    s = remove_style(s)
    return len(s)


def get_term_width():
    if width := os.getenv("CLYPI_TERM_WIDTH"):
        return int(width)

    try:
        return os.get_terminal_size().columns
    except OSError:
        from clypi._configuration import get_config

        return get_config().fallback_term_width


def trim_split_collection(s: str):
    if ", " in s:
        return s.split(", ")
    return s.split(",")
