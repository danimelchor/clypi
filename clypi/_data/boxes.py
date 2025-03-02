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
    myt: str
    myb: str
    mxl: str
    mxr: str
    mm: str


_HEAVY = Box(
    tl="┏",
    tr="┓",
    bl="┗",
    br="┛",
    x="━",
    y="┃",
    myt="┳",
    myb="┻",
    mxl="┣",
    mxr="┫",
    mm="╋",
)


class Boxes(Enum):
    HEAVY = _HEAVY
