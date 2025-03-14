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
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 50
