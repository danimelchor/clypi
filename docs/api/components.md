### Spinners

#### `Spin`

```python
class Spin(Enum): ...
```

The spinning animation you'd like to use. The spinners are sourced from the NPM [cli-spinners](https://www.npmjs.com/package/cli-spinners) package.

You can see all the spinners in action by running `uv run -m examples.spinner`. The full list can be found in the code [here](https://github.com/danimelchor/clypi/blob/master/clypi/_data/spinners.py).

#### `Spinner`

A spinner indicating that something is happening behind the scenes. It can be used as a context manager or [like a decorator](#spinner-decorator). The context manager usage is like so:

<!--- mdtest -->
```python
import asyncio
from clypi import Spinner

async def main():
    async with Spinner("Doing something", capture=True) as s:
        await asyncio.sleep(1)
        s.title = "Slept for a bit"
        print("I slept for a bit, will sleep a bit more")
        await asyncio.sleep(1)

asyncio.run(main())
```

##### `Spinner.__init__()`

```python
def __init__(
    self,
    title: str,
    animation: Spin | list[str] = Spin.DOTS,
    prefix: str = " ",
    suffix: str = "…",
    speed: float = 1,
    capture: bool = False,
)
```
Parameters:

- `title`: the initial text to display as the spinner spins
- `animation`: a provided [`Spin`](#spin) animation or a list of frames to display
- `prefix`: text or padding displayed before the icon
- `suffix`: text or padding displayed after the icon
- `speed`: a multiplier to speed or slow down the frame rate of the animation
- `capture`: if enabled, the Spinner will capture all stdout and stderr and display it nicely

##### `done`

```python
async def done(self, msg: str | None = None)
```
Mark the spinner as done early and optionally display a message.

##### `fail`

```python
async def fail(self, msg: str | None = None)
```
Mark the spinner as failed early and optionally display an error message.

##### `log`

```python
async def log(self, msg: str | None = None)
```
Display extra log messages to the user as the spinner spins and your work progresses.

##### `pipe`

```python
async def pipe(
    self,
    pipe: asyncio.StreamReader | None,
    color: ColorType = "blue",
    prefix: str = "",
)
```
Pipe the output of an async subprocess into the spinner and display the stdout or stderr
with a particular color and prefix.

Examples:
<!--- mdtest -->
> ```python
> async def main():
>     async with Spinner("Doing something") as s:
>         proc = await asyncio.create_subprocess_shell(
>             "for i in $(seq 1 10); do date && sleep 0.4; done;",
>             stdout=asyncio.subprocess.PIPE,
>             stderr=asyncio.subprocess.PIPE,
>         )
>         await asyncio.gather(
>             s.pipe(proc.stdout, color="blue", prefix="(stdout)"),
>             s.pipe(proc.stderr, color="red", prefix="(stdout)"),
>         )
> ```

#### `spinner` (decorator)

This is just a utility decorator that let's you wrap functions so that a spinner
displays while they run. `spinner` accepts the same arguments as the context manager [`Spinner`](#spinner).

<!--- mdtest -->
```python
import asyncio
from clypi import spinner

@spinner("Doing work", capture=True)
async def do_some_work():
    await asyncio.sleep(2)

asyncio.run(do_some_work())
```

### Boxed

#### `Boxes`

```python
class Boxes(Enum): ...
```

The border style you'd like to use. To see all the box styles in action run `uv run -m examples.boxed`.

The full list can be found in the code [here](https://github.com/danimelchor/clypi/blob/master/clypi/_data/boxes.py).


#### `boxed`

```python
def boxed(
    lines: T,
    width: int | None = None,
    style: Boxes = Boxes.HEAVY,
    alignment: AlignType = "left",
    title: str | None = None,
    color: ColorType = "bright_white",
) -> T:
```
Wraps text neatly in a box with the selected style, padding, and alignment.

Parameters:

- `lines`: the type of lines will determine it's output type. It can be one of `str`, `list[str]` or `Iterable[str]`
- `width`: the desired width of the box
- `style`: the desired style (see [`Boxes`](#boxes))
- `alignment`: the style of alignment (see [`align`](#align))
- `title`: optionally define a title for the box, it's length must be < width
- `color`: a color for the box border and title (see [`colors`](#colors))

Examples:

<!--- mdtest -->
> ```python
> print(clypi.boxed("Some boxed text", color="red", width=30, align="center"))
> ```

<img width="697" alt="image" src="https://github.com/user-attachments/assets/87e325a3-397c-4022-a3eb-a13984bfa855" />


### Stack

```python
def stack(*blocks: list[str], padding: int = 1) -> str:
def stack(*blocks: list[str], padding: int = 1, lines: bool) -> list[str]:
```

Horizontally aligns blocks of text to display a nice layout where each block is displayed
side by side.


<img width="974" alt="image" src="https://github.com/user-attachments/assets/9340d828-f7ce-491c-b0a8-6a666f7b7caf" />

Parameters:

- `blocks`: a series of blocks of lines of strings to display side by side
- `padding`: the space between each block
- `lines`: if the output should be returned as lines or as a string

Examples:
<!--- mdtest -->
> ```python
> names = clypi.boxed(["Daniel", "Pedro", "Paul"], title="Names", width=15)
> colors = clypi.boxed(["Blue", "Red", "Green"], title="Colors", width=15)
> print(clypi.stack(names, colors))
> ```

### Separator

#### `separator`
```python
def separator(
    separator: str = "━",
    width: t.Literal["max"] | int = "max",
    title: str | None = None,
    color: ColorType | None = None,
) -> str:
```
Prints a line made of the given separator character.

Parameters:

- `separator`: the character used to build the separator line
- `width`: if `max` it will use the max size of the terminal. Otherwise you can provide a fixed width.
- `title`: optionally provide a title to display in the middle of the separator
- `color`: the color for the characters

<!--- mdtest -->
> ```python
> print(clypi.separator(title="Some title", color="red", width=30))
> ```

<img width="716" alt="image" src="https://github.com/user-attachments/assets/42be7ee3-7357-44fb-8a22-11b065a23558" />


### Indented

#### `indented`
```python
def indented(lines: list[str], prefix: str = "  ") -> list[str]
```
Indents a set of lines with the given prefix

### Align

#### `align`

```python
def align(s: str, alignment: AlignType, width: int) -> str
```
Aligns text according to `alignment` and `width`. In contrast with the built-in
methods `rjust`, `ljust`, and `center`, `clypi.align(...)` aligns text according
to it's true visible width (the built-in methods count color codes as width chars).

Parameters:

- `s`: the string being aligned
- `alignment`: one of `left`, `right`, or `center`
- `width`: the wished final visible width of the string

Examples:

> ```python
> clypi.align("foo", "left", 10) # -> "foo       "
> clypi.align("foo", "right", 10) # -> "          foo"
> clypi.align("foo", "center", 10) # -> "   foo   "
>```
