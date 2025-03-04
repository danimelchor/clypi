from dataclasses import dataclass
from enum import Enum


@dataclass
class Box:
    """
    tl  x myt x  tr
    y             y
    mxl x mm  x mxr
    y             y
    bl  x myb x  br
    """

    tl: str
    tr: str
    bl: str
    br: str
    x: str
    y: str


_ROUNDED = Box(
    tl="╭",
    tr="╮",
    bl="╰",
    br="╯",
    x="─",
    y="│",
)

_THIN = Box(
    tl="┌",
    tr="┐",
    bl="└",
    br="┘",
    x="─",
    y="│",
)

_HEAVY = Box(
    tl="┏",
    tr="┓",
    bl="┗",
    br="┛",
    x="━",
    y="┃",
)


class Boxes(Enum):
    ROUNDED = _ROUNDED
    THIN = _THIN
    HEAVY = _HEAVY

    def human_name(self):
        name = self.name
        return " ".join(p.capitalize() for p in name.split("_"))
