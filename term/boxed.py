import os
import typing as t

from term._data.boxes import Boxes as _Boxes
from term.colors import ColorType, remove_style, styler

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


def _align(s: str, align: t.Literal["left", "center", "right"], width: int):
    if align == "left":
        return _ljust(s, width)
    if align == "right":
        return _rjust(s, width)
    return _center(s, width)


T = t.TypeVar("T", bound=t.Iterable[str] | list[str] | str)


def boxed(
    lines: T,
    width: int | None = None,
    style: Boxes = Boxes.HEAVY,
    padding_y: int = 1,
    align: t.Literal["left", "center", "right"] = "left",
    title: str | None = None,
    color: ColorType = "bright_white",
) -> T:
    width = width or os.get_terminal_size().columns
    box = style.value

    c = styler(fg=color)

    # Top bar
    def iter(lines: t.Iterable[str]):
        nonlocal title

        top_bar_width = width - 3
        if title:
            top_bar_width = width - 5 - len(title)
            title = f" {title} "
        else:
            title = ""
        yield c(box.tl + box.x + title + box.x * top_bar_width + box.tr)

        # Body
        for line in lines:
            aligned = _align(line, align, width - 2 - padding_y * 2)
            yield c(box.y) + padding_y * " " + aligned + padding_y * " " + c(box.y)

        # Footer
        yield c(box.bl + box.x * (width - 2) + box.br)

    if isinstance(lines, list):
        return t.cast(T, list(iter(lines)))
    if isinstance(lines, str):
        return t.cast(T, "\n".join(iter([lines])))
    return t.cast(T, iter(lines))
