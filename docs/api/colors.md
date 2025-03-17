### `ColorType`

```python
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
```

### `Styler`
```python
class Styler(
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
)
```
Returns a reusable function to style text.

Examples:
<!--- mdtest -->
> ```python
> wrong = clypi.Styler(fg="red", strikethrough=True)
> print("The old version said", wrong("Pluto was a planet"))
> print("The old version said", wrong("the Earth was flat"))
> ```

### `style`
```python
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
) -> str
```
Styles text and returns the styled string.

Examples:
<!--- mdtest -->
> ```python
> print(clypi.style("This is blue", fg="blue"), "and", clypi.style("this is red", fg="red"))
> ```

### `print`

```python
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
) -> None
```
Styles and prints colored and styled text directly.

Examples:
<!--- mdtest -->
> ```python
> clypi.cprint("Some colorful text", fg="green", reverse=True, bold=True, italic=True)
> ```
