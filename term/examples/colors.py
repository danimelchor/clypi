from __future__ import annotations

from typing import Generator, cast

import term
from term.colors import ColorType, _color_codes
from term.examples import _utils


# --- DEMO UTILS ---
def _title(msg: str, char: str = "=", width: int | None = None) -> list[str]:
    ret = []
    sep = width or (len(msg) + 4)
    ret.append("┏" + "━" * (sep - 2) + "┓")
    ret.append("┃ " + msg.upper().center(sep - 4) + " ┃")
    ret.append("┗" + "━" * (sep - 2) + "┛")
    return ret


def _all_colors() -> Generator[tuple[ColorType, ...], None, None]:
    for color in _color_codes:
        yield (
            cast(ColorType, f"{color}"),
            cast(ColorType, f"bright_{color}"),
        )


# --- DEMO START ---
def main() -> None:
    fg_block = _title("Foregrounds", width=29)
    for color, bright_color in _all_colors():
        fg_block.append(
            term.style("██ " + color.ljust(9), fg=color)
            + term.style("██ " + bright_color.ljust(16), fg=bright_color)
        )

    bg_block = _title("Backgrounds", width=25)
    for color, bright_color in _all_colors():
        bg_block.append(
            term.style(color.ljust(9), bg=color)
            + term.style(bright_color.ljust(16), bg=bright_color)
        )

    style_block = _title("text styles", width=18)
    style_block.append(term.style("I am bold", bold=True))
    style_block.append(term.style("I am dim", dim=True))
    style_block.append(term.style("I am underline", underline=True))
    style_block.append(term.style("I am blink", blink=True))
    style_block.append(term.style("I am reverse", reverse=True))
    style_block.append(term.style("I am strikethrough", strikethrough=True))

    for line in _utils.assemble(fg_block, bg_block, style_block):
        print(line)
