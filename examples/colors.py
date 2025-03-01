from __future__ import annotations

from typing import Generator, cast

import term
from examples import _utils
from term.boxed import boxed
from term.colors import ColorType, _color_codes


# --- DEMO UTILS ---
def _all_colors() -> Generator[tuple[ColorType, ...], None, None]:
    for color in _color_codes:
        yield (
            cast(ColorType, f"{color}"),
            cast(ColorType, f"bright_{color}"),
        )


# --- DEMO START ---
def main() -> None:
    fg_block = ["Foregrounds"]
    for color, bright_color in _all_colors():
        fg_block.append(
            term.style("██ " + color.ljust(9), fg=color)
            + term.style("██ " + bright_color.ljust(16), fg=bright_color)
        )

    bg_block = ["Backgrounds"]
    for color, bright_color in _all_colors():
        bg_block.append(
            term.style(color.ljust(9), bg=color)
            + " "
            + term.style(bright_color.ljust(16), bg=bright_color)
        )

    style_block = ["Text Styles"]
    style_block.append(term.style("I am bold", bold=True))
    style_block.append(term.style("I am dim", dim=True))
    style_block.append(term.style("I am underline", underline=True))
    style_block.append(term.style("I am blink", blink=True))
    style_block.append(term.style("I am reverse", reverse=True))
    style_block.append(term.style("I am strikethrough", strikethrough=True))

    for line in _utils.assemble(
        boxed(fg_block, width=35, has_title=True),
        boxed(bg_block, width=30, has_title=True),
        boxed(style_block, width=22, has_title=True),
    ):
        print(line)


if __name__ == "__main__":
    main()
