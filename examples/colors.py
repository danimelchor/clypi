from __future__ import annotations

from typing import Generator, cast

import clypi
from clypi.colors import ColorType, _color_codes


# --- DEMO UTILS ---
def _all_colors() -> Generator[tuple[ColorType, ...], None, None]:
    for color in _color_codes:
        yield (
            cast(ColorType, f"{color}"),
            cast(ColorType, f"bright_{color}"),
        )


# --- DEMO START ---
def main() -> None:
    fg_block = []
    for color, bright_color in _all_colors():
        fg_block.append(
            clypi.style("██ " + color.ljust(9), fg=color)
            + clypi.style("██ " + bright_color.ljust(16), fg=bright_color)
        )

    bg_block = []
    for color, bright_color in _all_colors():
        bg_block.append(
            clypi.style(color.ljust(9), bg=color)
            + " "
            + clypi.style(bright_color.ljust(16), bg=bright_color)
        )

    style_block = []
    style_block.append(clypi.style("I am bold", bold=True))
    style_block.append(clypi.style("I am dim", dim=True))
    style_block.append(clypi.style("I am underline", underline=True))
    style_block.append(clypi.style("I am blink", blink=True))
    style_block.append(clypi.style("I am reverse", reverse=True))
    style_block.append(clypi.style("I am strikethrough", strikethrough=True))

    stacked_colors = clypi.stack(
        clypi.boxed(fg_block, width=35, title="Foregrounds"),
        clypi.boxed(bg_block, width=30, title="Backgrounds"),
        clypi.boxed(style_block, width=22, title="Styles"),
    )
    print(stacked_colors)


if __name__ == "__main__":
    main()
