import typing as t

from clypi import wrap
from clypi._data.boxes import Boxes as _Boxes
from clypi._util import get_term_width
from clypi.align import AlignType
from clypi.align import align as _align
from clypi.colors import ColorType, Styler

Boxes = _Boxes


T = t.TypeVar("T", bound=t.Iterable[str] | list[str] | str)


def boxed(
    lines: T,
    width: int | None = None,
    style: Boxes = Boxes.HEAVY,
    align: AlignType = "left",
    title: str | None = None,
    color: ColorType | None = None,
) -> T:
    width = width or get_term_width()
    box = style.value

    c = Styler(fg=color)

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
            # Bar, space, text..., space, bar
            max_text_width = width - 2 - 2

            # Wrap it in case each line is longer than expected
            wrapped = wrap(line, max_text_width)
            for sub_line in wrapped:
                aligned = _align(sub_line, align, max_text_width)
                yield c(box.y) + " " + aligned + " " + c(box.y)

        # Footer
        yield c(box.bl + box.x * (width - 2) + box.br)

    if isinstance(lines, list):
        return t.cast(T, list(iter(lines)))
    if isinstance(lines, str):
        return t.cast(T, "\n".join(iter(lines.split("\n"))))
    return t.cast(T, iter(lines))
