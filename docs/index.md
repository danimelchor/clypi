# 🦄 clypi

## Configuration

### Accessing and changing the configuration

```python
from clypi import ClypiConfig, configure, get_config

# Get's the current config (or a default)
conf = get_config()

# Change the configuration
config = ClypiConfig(help_on_fail=False)
configure(config)
```

### Default config

```python
ClypiConfig(
    help_formatter=ClypiFormatter(boxed=True),
    help_on_fail=True,
    nice_errors=(ClypiException,),
    theme=Theme(
        usage=Styler(fg="yellow"),
        prog=Styler(bold=True),
        section_title=Styler(),
        subcommand=Styler(fg="blue", bold=True),
        long_option=Styler(fg="blue", bold=True),
        short_option=Styler(fg="green", bold=True),
        positional=Styler(fg="blue", bold=True),
        type_str=Styler(fg="yellow", bold=True),
        prompts=Styler(fg="blue", bold=True),
    ),
)
```

Parameters:
- `help_formatter`: the formatter class to use to display the help pages (see [Formatter](#formatter))
- `help_on_fail`: weather the help page should be displayed if a user doesn't pass the right params
- `nice_errors`: a list of errors clypi will catch and display neatly
- `theme`: a `Theme` object used to format different styles and colors for help pages, prompts, tracebacks, etc.


## CLI

### `arg`

```python
def arg(
    parser: Parser[T] | None = None,
    default: T | Unset = _UNSET,
    default_factory: t.Callable[[], T] | Unset = _UNSET,
    help: str | None = None,
    short: str | None = None,
    prompt: str | None = None,
    hide_input: bool = False,
    max_attempts: int = MAX_ATTEMPTS,
) -> T
```

Utility function to configure how a specific argument should behave when displayed
and parsed.

Parameters:
- `parser`: a function that takes in a string and returns the parsed type (see [`Parser`](#parser[t]))
- `default`: the default value to return if the user doesn't pass in the argument (or hits enter during the prompt, if any)
- `default_factory`: a function that returns a default value. Useful to defer computation or to avoid default mutable values
- `help`: a brief description to show the user when they pass in `-h` or `--help`
- `short`: for options it defines a short way to pass in a value (e.g.: `short="v"` allows users to pass in `-v <value>`)
- `prompt`: if defined, it will ask the user to provide input if not already defined in the command line args
- `hide_input`: whether the input shouldn't be displayed as the user types (for passwords, API keys, etc.)
- `max_attempts`: how many times to ask the user before giving up and raising

### `Command`

This is the main class you must extend when defining a command. There are no methods you must override
other than the [`run`](#run) method. The type hints you annotate the class will define the arguments that
command will take based on a set of rules:

#### Subcommands

To define a subcommand, you must define a field in a class extending `Command` called `subcommand`. It's type hint must
point to other classes extending `Command` or `None` by using either a single class, or a union of classes.

These are all valid examples:
```python
from clypi import Command

class MySubcommand(Command):
    pass

class MyOtherSubcommand(Command):
    pass

class MyCommand(Command):
    # A mandatory subcommand `my-subcommand`
    subcommand: MySubcommand

    # An optional subcommand `my-subcommand`
    subcommand: MySubcommand | None

    # A mandatory subcommand `my-subcommand` or `my-other-subcommand`
    subcommand: MySubcommand | MyOtherSubcommand

    # An optional subcommand `my-subcommand` or `my-other-subcommand`
    subcommand: MySubcommand | MyOtherSubcommand | None
```

#### Arguments (positional)

Arguments are mandatory positional words the user must pass in. They're defined as class attributes with no default and type hinted with the `Positional[T]` type.

```python
from clypi import Command, Positional

# my-command 5 foo bar baz
#        arg1^ ^^^^^^^^^^^arg2
class MyCommand(Command):
    arg1: Positional[int]
    arg2: Positional[list[str]]
```

#### Flags

Flags are boolean options that can be either present or not. To define a flag, simply define
a boolean class attribute in your command with a default value. The user will then be able
to pass in `--my-flag` when running the command which will set it to True.

```python
from clypi import Command

# With the flag ON: my-command --my-flag
# With the flag OFF: my-command
class MyCommand(Command):
    my_flag: bool = False
```


#### Options

Options are like flags but, instead of booleans, the user passes in specific values. You can think of options as key/pair items. Options can be set as required by not specifying a default value.

```python
from clypi import Command

# With value: my-command --my-attr foo
# With default: my-command
class MyCommand(Command):
    my_attr: str | int = "some-default-here"
```

#### Running the command

You must implement the [`run`](#run) method so that your command can be ran. The function
must be `async` so that we can properly render items in your screen.

```python
from clypi import Command, arg

class MyCommand(Command):
    verbose: bool = False

    async def run(self):
        print(f"Running with verbose: {self.verbose}")
```

#### Help page

You can define custom help messages for each argument using our handy `config` helper:

```python
from clypi import Command, arg

class MyCommand(Command):
    verbose: bool = arg(help="Whether to show all of the output", default=True)
```

You can also define custom help messages for commands by creating a docstring on the class itself:
```python
from clypi import Command, arg

class MyCommand(Command):
    """
    This text will show up when someone does `my-command --help`
    and can contain any info you'd like
    """
```

#### Prompting

If you want to ask the user to provide input if it's not specified, you can pass in a prompt to `config` for each field like so:

```python
from clypi import Command, arg

class MyCommand(Command):
    name: str = arg(prompt="What's your name?")
```

On runtime, if the user didn't provide a value for `--name`, the program will ask the user to provide one until they do. You can also pass in a `default` value to `config` to allow the user to just hit enter to accept the default.

#### Custom parsers

If the type you want to parse from the user is too complex, you can define your own parser
using `config` as well:

```python
import typing as t
from clypi import Command, arg

def parse_slack(value: t.Any) -> str:
    if not value.startswith('#'):
        raise ValueError("Invalid Slack channel. It must start with a '#'.")
    return value

class MyCommand(Command):
    slack: str = arg(parser=parse_slack)
```

Optionally, you can use packages like [v6e](https://github.com/danimelchor/v6e) to parse the input:

```python
import v6e
from clypi import Command, arg

class MyCli(Command):
    files: list[Path] = arg(parser=v6e.path().exists().list())
```

#### Forwarding arguments

If a command defines an argument you want to use in any of it's children, you can re-define the
argument and pass in a literal ellipsis (`...`) to config to indicate the argument comes from the
parent command. You can also use `forwarded=True` if you prefer:

```python
from clypi import Command, arg

class MySubCmd(Command):
    verbose: bool = arg(...)  # or `arg(forwarded=True)`

class MyCli(Command):
    subcommand: MySubCmd | None
```

#### Autocomplete

All CLIs built with clypi come with a builtin `--install-autocomplete` option that will automatically
set up shell completions for your built CLI.

> [!IMPORTANT]
> This feature is brand new and might contain some bugs. Please file a ticket
> if you run into any!

#### `prog`
```python
@t.final
@classmethod
def prog(cls)
```
The name of the command. Can be overriden to provide a custom name
or will default to the class name extending `Command`.

#### `help`
```python
@t.final
@classmethod
def help(cls)
```
The help displayed for the command when the user passes in `-h` or `--help`. Defaults to the
docstring for the class extending `Command`.

#### `run`
```python
async def run(self: Command) -> None:
```
The main function you **must** override. This function is where the business logic of your command
should live.

`self` contains the arguments for this command you can access
as you would do with any other instance property.


#### `astart` and `start`
```python
async def astart(self: Command | None = None) -> None:
```
```python
def start(self) -> None:
```
These commands are the entry point for your program. You can either call `YourCommand.start()` on your class
or, if already in an async loop, `await YourCommand.astart()`.


#### `print_help`
```python
@t.final
@classmethod
def print_help(cls, exception: Exception | None = None)
```
Prints the help page for a particular command.

Parameters:
- `exception`: an exception neatly showed to the user as a traceback. Automatically passed in during runtime.

### `Formatter`

A formatter is any class conforming to the following protocol. It is called on several occasions to render
the help page. The `Formatter` implementation should try to use the provided configuration theme when possible.

```python
class Formatter(t.Protocol):
    def format_help(
        self,
        prog: list[str],
        description: str | None,
        epilog: str | None,
        options: list[_Argument],
        positionals: list[_Argument],
        subcommands: list[type[Command]],
        exception: Exception | None,
    ) -> str: ...
```

### `ClypiFormatter`

Clypi ships with a pre-made formatter that can display help pages with either boxes or with idented sections:

```python
ClypiFormatter(boxed=True)
```

<img width="1701" alt="image" src="https://github.com/user-attachments/assets/20212b97-73b8-4efa-92b0-873405f33c55" />


```python
ClypiFormatter(boxed=False)
```

<img width="1696" alt="image" src="https://github.com/user-attachments/assets/d0224cf4-0c91-4720-8e43-746985531912" />


## Prompts

### `Parser[T]`

```python
Parser: TypeAlias = Callable[[Any], T] | type[T]
```
A function taking in any value and returns a value of type `T`. This parser
can be a user defined function, a built-in type like `str`, `int`, etc., or a parser
from a library.

### `confirm`

```python
def confirm(
    text: str,
    *,
    default: bool | Unset = _UNSET,
    max_attempts: int = MAX_ATTEMPTS,
    abort: bool = False,
) -> bool:
```
Prompts the user for a yes/no value.

Parameters:
- `text`: the text to display to the user when asking for input
- `default`: optionally set a default value that the user can immediately accept
- `max_attempts`: how many times to ask the user before giving up and raising
- `abort`: if a user answers "no", it will raise a `AbortException`


### `prompt`

```python
def prompt(
    text: str,
    default: T | Unset = _UNSET,
    parser: Parser[T] = str,
    hide_input: bool = False,
    max_attempts: int = MAX_ATTEMPTS,
) -> T:
```
Prompts the user for a value and uses the provided parser to validate and parse the input

Parameters:
- `text`: the text to display to the user when asking for input
- `default`: optionally set a default value that the user can immediately accept
- `parser`: a function that parses in the user input as a string and returns the parsed value or raises
- `hide_input`: whether the input shouldn't be displayed as the user types (for passwords, API keys, etc.)
- `max_attempts`: how many times to ask the user before giving up and raising

## Colors

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
)
```
Returns a reusable function to style text.

Examples:
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
) -> str
```
Styles text and returns the styled string.

Examples:
> ```python
> print(clypi.style("This is blue", fg="blue"), "and", clypi.style("this is red", fg="red"))
> ```

### `print`

```python
def print(
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
    end: str | None = "\n",
) -> None
```
Styles and prints text directly.

Examples:
> ```python
> clypi.print("Some colorful text", fg="green", reverse=True, bold=True, italic=True)
> ```

## Spinners

### `Spin`

```python
class Spin(Enum): ...
```

The spinning animation you'd like to use. The spinners are sourced from the NPM [cli-spinners](https://www.npmjs.com/package/cli-spinners) package.

You can see all the spinners in action by running `uv run -m examples.spinner`. The full list can be found in the code [here](https://github.com/danimelchor/clypi/blob/master/clypi/_data/spinners.py).

### `Spinner`

A spinner indicating that something is happening behind the scenes. It can be used as a context manager or [like a decorator](#spinner-decorator). The context manager usage is like so:

```python
import asyncio
from clypi import Spinner

async def main():
    async with Spinner("Doing something", capture=True) as s:
        asyncio.sleep(2)
        s.title = "Slept for a bit"
        print("I slept for a bit, will sleep a bit more")
        asyncio.sleep(2)

asyncio.run(main())
```

#### `Spinner.__init__()`

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

#### `done`

```python
async def done(self, msg: str | None = None)
```
Mark the spinner as done early and optionally display a message.

#### `fail`

```python
async def fail(self, msg: str | None = None)
```
Mark the spinner as failed early and optionally display an error message.

#### `log`

```python
async def log(self, msg: str | None = None)
```
Display extra log messages to the user as the spinner spins and your work progresses.

#### `pipe`

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

### `spinner` (decorator)

This is just a utility decorator that let's you wrap functions so that a spinner
displays while they run. `spinner` accepts the same arguments as the context manager [`Spinner`](#spinner).

```python
import asyncio
from clypi import spinner

@spinner("Doing work", capture=True)
async def do_some_work():
    await asyncio.sleep(5)

asyncio.run(do_some_work())
```

## Boxed

### `Boxes`

```python
class Boxes(Enum): ...
```

The border style you'd like to use. To see all the box styles in action run `uv run -m examples.boxed`.

The full list can be found in the code [here](https://github.com/danimelchor/clypi/blob/master/clypi/_data/boxes.py).


### `boxed`

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
- `style`: the desired style (see [`Boxes`](#Boxes))
- `alignment`: the style of alignment (see [`align`](#align))
- `title`: optionally define a title for the box, it's lenght must be < width
- `color`: a color for the box border and title (see [`colors`](#colors))

Examples:

> ```python
> print(clypi.boxed("Some boxed text", color="red", width=30, align="center"))
> ```


## Stack

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
```python
names = clypi.boxed(["Daniel", "Pedro", "Paul"], title="Names", width=15)
colors = clypi.boxed(["Blue", "Red", "Green"], title="Colors", width=15)
print(clypi.stack(names, colors))
```

## Align

### `align`

```python
def align(s: str, alignment: AlignType, width: int) -> str
```
Aligns text according to `alignment` and `width`. In contrast with the built-in
methods `rjust`, `ljust`, and `center`, `clypi.align(...)` aligns text according
to it's true visible width (the built-in methods count color codes as width chars).

Parameters:
- `s`: the string being aligned
- `alignment`: one of `left`, `right`, or `center`
- `width`: the wished final visible widht of the string

Examples:

> ```python
> clypi.align("foo", "left", 10) -> "foo       "
> clypi.align("foo", "right", 10) -> "          foo"
> clypi.align("foo", "center", 10) -> "   foo   "
>```
