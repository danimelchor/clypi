import typing as t

from clypi._colors import ColorType, Styler
from clypi._components.align import AlignType
from clypi._components.align import align as _align
from clypi._components.wraps import wrap
from clypi._data.boxes import Boxes as _Boxes
from clypi._util import get_term_width, visible_width

Boxes = _Boxes


T = t.TypeVar("T", bound=list[str] | str)


def boxed(
    lines: T,
    width: t.Literal["auto", "max"] | int = "auto",
    style: Boxes = Boxes.HEAVY,
    align: AlignType = "left",
    title: str | None = None,
    color: ColorType | None = None,
) -> T:
    box = style.value
    c = Styler(fg=color)

    def _iter_box(
        lines: t.Iterable[str],
        width: int,
    ):
        # Top bar
        nonlocal title
        top_bar_width = width - 3
        if title:
            top_bar_width = width - 5 - visible_width(title)
            title = f" {title} "
        else:
            title = ""
        yield c(box.tl + box.x + title + box.x * top_bar_width + box.tr)

        # Body
        for line in lines:
            # Remove two on each side due to the box edge and padding
            max_text_width = -2 + width - 2

            # Wrap it in case each line is longer than expected
            wrapped = wrap(line, max_text_width)
            for sub_line in wrapped:
                aligned = _align(sub_line, align, max_text_width)
                yield c(box.y) + " " + aligned + " " + c(box.y)

        # Footer
        yield c(box.bl + box.x * (width - 2) + box.br)

    def _get_width(lines: list[str]):
        if isinstance(width, int):
            return width

        if width == "max":
            return get_term_width()

        # Width is auto
        max_visible_width = max(visible_width(line) for line in lines)
        # Add two on each side for the box edge and padding
        return 2 + max_visible_width + 2

    if isinstance(lines, list):
        computed_width = _get_width(lines)
        return t.cast(T, list(_iter_box(lines, width=computed_width)))

    act_lines = lines.split("\n")
    computed_width = _get_width(act_lines)
    return t.cast(T, "\n".join(_iter_box(act_lines, width=computed_width)))
