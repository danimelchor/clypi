from typing import Generator, Iterable, Literal

from term._data.boxes import Boxes as _Boxes
from term.colors import remove_style

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


def _align(s: str, align: Literal["left", "center", "right"], width: int):
    if align == "left":
        return _ljust(s, width)
    if align == "right":
        return _rjust(s, width)
    return _center(s, width)


def boxed(
    lines: Iterable[str],
    width: int = 30,
    style: Boxes = Boxes.HEAVY,
    padding_y: int = 1,
    align: Literal["left", "center", "right"] = "center",
    has_title: bool = False,
) -> Generator[str, None, None]:
    box = style.value

    yield box.tl + box.x * (width - 2) + box.tr
    for idx, line in enumerate(lines):
        aligned = _align(line, align, width - 2 - padding_y * 2)
        yield box.y + padding_y * " " + aligned + padding_y * " " + box.y

        if idx == 0 and has_title:
            yield box.mxl + box.x * (width - 2) + box.mxr
    yield box.bl + box.x * (width - 2) + box.br
