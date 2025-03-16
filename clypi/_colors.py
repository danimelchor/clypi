import builtins
import re
import typing as t
from dataclasses import dataclass
from enum import Enum

ESC = "\033["
ANSI_ESCAPE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
END = "m"

FG_OFFSET = 30
BG_OFFSET = 40
BRIGHT_OFFSET = 60

STYLE_ON_OFFSET = 0
STYLE_OFF_OFFSET = 20

ColorType: t.TypeAlias = t.Literal[
    "black",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "white",
    "default",
    "bright_black",
    "bright_red",
    "bright_green",
    "bright_yellow",
    "bright_blue",
    "bright_magenta",
    "bright_cyan",
    "bright_white",
    "bright_default",
]
ALL_COLORS = tuple(t.get_args(ColorType))

_color_codes = {
    "black": 0,
    "red": 1,
    "green": 2,
    "yellow": 3,
    "blue": 4,
    "magenta": 5,
    "cyan": 6,
    "white": 7,
    "default": 9,
}


def _code(code: int) -> str:
    return f"{ESC}{code}{END}"


def _color_code(color: ColorType, offset: int) -> int:
    """
    Given a color name and an offset (e.g.: fg, bright bg, etc.)
    it returns the actual color code that will need to be used

    Example:
      _color_code("bright_green", FG_OFFSET) -> 42
      Since: 2(green) + 10(bright) + 30(fg offset)
    """

    key = str(color)
    if color.startswith("bright_"):
        key = color.removeprefix("bright_")
        offset += BRIGHT_OFFSET
    return _color_codes[key] + offset


def _apply_color(s: str, color: ColorType, offset: int) -> str:
    start = _color_code(color, offset)
    end = _color_code("default", offset)
    return f"{_code(start)}{s}{_code(end)}"


def _apply_fg(text: str, fg: ColorType):
    return _apply_color(text, fg, FG_OFFSET)


def _apply_bg(text: str, bg: ColorType):
    return _apply_color(text, bg, BG_OFFSET)


class StyleCode(Enum):
    BOLD = 1
    DIM = 2
    ITALIC = 3
    UNDERLINE = 4
    BLINK = 5
    REVERSE = 7
    STRIKETHROUGH = 9


def _apply_style(s: str, style: StyleCode) -> str:
    start = style.value + STYLE_ON_OFFSET
    return f"{_code(start)}{s}{_code(0)}"


def _reset(s: str) -> str:
    return f"{_code(0)}{s}"


def remove_style(s: str):
    return ANSI_ESCAPE.sub("", s)


@dataclass
class Styler:
    fg: ColorType | None = None
    bg: ColorType | None = None
    bold: bool = False
    italic: bool = False
    dim: bool = False
    underline: bool = False
    blink: bool = False
    reverse: bool = False
    strikethrough: bool = False
    reset: bool = False
    hide: bool = False

    def __call__(self, *messages: t.Any) -> str:
        # Utility so that strings can be dynamically removed
        if self.hide:
            return ""

        text = " ".join(str(m) for m in messages)
        text = _apply_fg(text, self.fg) if self.fg else text
        text = _apply_bg(text, self.bg) if self.bg else text
        text = _apply_style(text, StyleCode.BOLD) if self.bold else text
        text = _apply_style(text, StyleCode.ITALIC) if self.italic else text
        text = _apply_style(text, StyleCode.DIM) if self.dim else text
        text = _apply_style(text, StyleCode.UNDERLINE) if self.underline else text
        text = _apply_style(text, StyleCode.BLINK) if self.blink else text
        text = _apply_style(text, StyleCode.REVERSE) if self.reverse else text
        text = (
            _apply_style(text, StyleCode.STRIKETHROUGH) if self.strikethrough else text
        )
        text = _reset(text) if self.reset else text
        return text


def style(
    *messages: t.Any,
    fg: ColorType | None = None,
    bg: ColorType | None = None,
    bold: bool = False,
    italic: bool = False,
    dim: bool = False,
    underline: bool = False,
    blink: bool = False,
    reverse: bool = False,
    strikethrough: bool = False,
    reset: bool = False,
    hide: bool = False,
) -> str:
    return Styler(
        fg=fg,
        bg=bg,
        bold=bold,
        italic=italic,
        dim=dim,
        underline=underline,
        blink=blink,
        reverse=reverse,
        strikethrough=strikethrough,
        reset=reset,
        hide=hide,
    )(*messages)


class SupportsWrite(t.Protocol):
    def write(self, s: t.Any, /) -> object: ...


def cprint(
    *messages: t.Any,
    fg: ColorType | None = None,
    bg: ColorType | None = None,
    bold: bool = False,
    italic: bool = False,
    dim: bool = False,
    underline: bool = False,
    blink: bool = False,
    reverse: bool = False,
    strikethrough: bool = False,
    reset: bool = False,
    hide: bool = False,
    file: SupportsWrite | None = None,
    end: str | None = "\n",
):
    text = style(
        *messages,
        fg=fg,
        bg=bg,
        bold=bold,
        italic=italic,
        dim=dim,
        underline=underline,
        blink=blink,
        reverse=reverse,
        strikethrough=strikethrough,
        reset=reset,
        hide=hide,
    )
    builtins.print(text, end=end, file=file)
