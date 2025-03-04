import os
import typing as t

import clypi
from clypi._data.boxes import Boxes as _Boxes
from clypi.align import AlignType
from clypi.colors import ColorType, styler

Boxes = _Boxes


T = t.TypeVar("T", bound=t.Iterable[str] | list[str] | str)


def boxed(
    lines: T,
    width: int | None = None,
    style: Boxes = Boxes.HEAVY,
    padding_y: int = 1,
    alignment: AlignType = "left",
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
            aligned = clypi.align(line, alignment, width - 2 - padding_y * 2)
            yield c(box.y) + padding_y * " " + aligned + padding_y * " " + c(box.y)

        # Footer
        yield c(box.bl + box.x * (width - 2) + box.br)

    if isinstance(lines, list):
        return t.cast(T, list(iter(lines)))
    if isinstance(lines, str):
        return t.cast(T, "\n".join(iter([lines])))
    return t.cast(T, iter(lines))
