from dataclasses import dataclass
from enum import Enum


@dataclass
class Box:
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
)


class Boxes(Enum):
    HEAVY = _HEAVY
