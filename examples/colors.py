from __future__ import annotations

from typing import Generator, cast

from term import colors


# --- DEMO UTILS ---
def _title(msg: str, char: str = "=", start: bool = True):
    if start:
        print("\n\n")

    sep = len(msg) + 4
    print(char * sep)
    print(char, msg.upper(), char)
    print(char * sep)


def _all_colors() -> Generator[tuple[colors.ColorType, ...], None, None]:
    for color in colors._color_codes:
        yield (
            cast(colors.ColorType, f"{color}"),
            cast(colors.ColorType, f"bright_{color}"),
        )


# --- DEMO START ---
def main() -> None:
    _title("Foregrounds", start=False)
    for color, bright_color in _all_colors():
        colors.print("██ " + color.ljust(9), fg=color, end=" ")
        colors.print("██ " + bright_color.ljust(16), fg=bright_color)

    _title("Backgrounds")
    for color, bright_color in _all_colors():
        colors.print(color.ljust(9), bg=color, end=" ")
        colors.print(bright_color.ljust(16), bg=bright_color)

    _title("text styles")
    colors.print("I am bold", bold=True)
    colors.print("I am dim", dim=True)
    colors.print("I am underline", underline=True)
    colors.print("I am blink", blink=True)
    colors.print("I am reverse", reverse=True)
    colors.print("I am strikethrough", strikethrough=True)


if __name__ == "__main__":
    main()
