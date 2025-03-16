import typing as t

from clypi._colors import ColorType, Styler
from clypi._util import get_term_width, visible_width


def separator(
    separator: str = "━",
    width: t.Literal["max"] | int = "max",
    title: str | None = None,
    color: ColorType | None = None,
) -> str:
    if width == "max":
        width = get_term_width()

    c = Styler(fg=color)

    if not title:
        return c(separator * width)

    num_chars = width - 2 - visible_width(title)
    left_chars = num_chars // 2
    right_chars = num_chars - left_chars
    return c(separator * left_chars + " " + title + " " + separator * right_chars)
