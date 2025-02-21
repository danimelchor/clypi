from __future__ import annotations

from typing import Generator, cast

import term
from term.colors import ColorType, _color_codes


# --- DEMO UTILS ---
def _title(msg: str, char: str = "=", start: bool = True):
    if start:
        print("\n\n")

    sep = len(msg) + 4
    print(char * sep)
    print(char, msg.upper(), char)
    print(char * sep)


def _all_colors() -> Generator[tuple[ColorType, ...], None, None]:
    for color in _color_codes:
        yield (
            cast(ColorType, f"{color}"),
            cast(ColorType, f"bright_{color}"),
        )


# --- DEMO START ---
def main() -> None:
    _title("Foregrounds", start=False)
    for color, bright_color in _all_colors():
        term.print("██ " + color.ljust(9), fg=color, end=" ")
        term.print("██ " + bright_color.ljust(16), fg=bright_color)

    _title("Backgrounds")
    for color, bright_color in _all_colors():
        term.print(color.ljust(9), bg=color, end=" ")
        term.print(bright_color.ljust(16), bg=bright_color)

    _title("text styles")
    term.print("I am bold", bold=True)
    term.print("I am dim", dim=True)
    term.print("I am underline", underline=True)
    term.print("I am blink", blink=True)
    term.print("I am reverse", reverse=True)
    term.print("I am strikethrough", strikethrough=True)


if __name__ == "__main__":
    main()
