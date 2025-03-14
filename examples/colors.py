from __future__ import annotations

from typing import Generator

from clypi import ALL_COLORS, ColorType, boxed, stack, style


# --- DEMO UTILS ---
def _all_colors() -> Generator[tuple[ColorType, ...], None, None]:
    mid = len(ALL_COLORS) // 2
    normal, bright = ALL_COLORS[:mid], ALL_COLORS[mid:]
    for color in zip(normal, bright):
        yield color


# --- DEMO START ---
def main() -> None:
    fg_block: list[str] = []
    for color, bright_color in _all_colors():
        fg_block.append(
            style("██ " + color.ljust(9), fg=color)
            + style("██ " + bright_color.ljust(16), fg=bright_color)
        )

    bg_block: list[str] = []
    for color, bright_color in _all_colors():
        bg_block.append(
            style(color.ljust(9), bg=color)
            + " "
            + style(bright_color.ljust(16), bg=bright_color)
        )

    style_block: list[str] = []
    style_block.append(style("I am bold", bold=True))
    style_block.append(style("I am dim", dim=True))
    style_block.append(style("I am underline", underline=True))
    style_block.append(style("I am blink", blink=True))
    style_block.append(style("I am reverse", reverse=True))
    style_block.append(style("I am strikethrough", strikethrough=True))

    stacked_colors = stack(
        boxed(fg_block, title="Foregrounds"),
        boxed(bg_block, title="Backgrounds"),
        boxed(style_block, title="Styles"),
    )
    print(stacked_colors)


if __name__ == "__main__":
    main()
