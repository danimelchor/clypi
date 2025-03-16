# 🦄 clypi

## Configuration

### Accessing and changing the configuration

```python
from clypi import ClypiConfig, configure, get_config

# Gets the current config (or a default)
conf = get_config()

# Change the configuration
config = ClypiConfig(help_on_fail=False)
configure(config)
```

### Default config

<!--- mdtest -->
```python
ClypiConfig(
    help_formatter=ClypiFormatter(
        boxed=True,
        show_option_types=True,
    ),
    help_on_fail=True,
    nice_errors=(ClypiException,),
    theme=Theme(
        usage=Styler(fg="yellow"),
        usage_command=Styler(bold=True),
        usage_args=Styler(),
        section_title=Styler(),
        subcommand=Styler(fg="blue", bold=True),
        long_option=Styler(fg="blue", bold=True),
        short_option=Styler(fg="green", bold=True),
        positional=Styler(fg="blue", bold=True),
        placeholder=Styler(fg="blue"),
        type_str=Styler(fg="yellow", bold=True),
        prompts=Styler(fg="blue", bold=True),
    ),
    overflow_style="wrap",
)
```

Parameters:
- `help_formatter`: the formatter class to use to display the help pages (see [Formatter](#formatter))
- `help_on_fail`: whether the help page should be displayed if a user doesn't pass the right params
- `nice_errors`: a list of errors clypi will catch and display neatly
- `theme`: a `Theme` object used to format different styles and colors for help pages, prompts, tracebacks, etc.
- `overflow_style`: either `wrap` or `ellipsis`. If wrap, text that is too long will get wrapped into the next line. If ellipsis, the text will be truncated with an `…` at the end.


## CLI

### `arg`

```python
def arg(
    default: T | Unset | EllipsisType = UNSET,
    parser: Parser[T] | None = None,
    default_factory: t.Callable[[], T] | Unset = UNSET,
    help: str | None = None,
    short: str | None = None,
    prompt: str | None = None,
    hide_input: bool = False,
    max_attempts: int = MAX_ATTEMPTS,
    group: str | None = None,
) -> T
```

Utility function to configure how a specific argument should behave when displayed
and parsed.

Parameters:
- `default`: the default value to return if the user doesn't pass in the argument (or hits enter during the prompt, if any)
- `parser`: a function that takes in a string and returns the parsed type (see [`Parser`](#parser[t]))
- `default_factory`: a function that returns a default value. Useful to defer computation or to avoid default mutable values
- `help`: a brief description to show the user when they pass in `-h` or `--help`
- `short`: for options it defines a short way to pass in a value (e.g.: `short="v"` allows users to pass in `-v <value>`)
- `prompt`: if defined, it will ask the user to provide input if not already defined in the command line args
- `hide_input`: whether the input shouldn't be displayed as the user types (for passwords, API keys, etc.)
- `max_attempts`: how many times to ask the user before giving up and raising
- `group`: optionally define the name of a group to display the option in. Adding an option will automatically display the options in a different section of the help page (for an example, see the pictures in [formatter](#formatter)).
- `defer` (advanced): defers the fetching of a value until the value is used. This can be helpful to express complex dependencies between arguments. For example, you may not want to prompt if a different option was passed in (see `examples/cli_deferred.py`).

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

<!--- mdtest -->
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

<!--- mdtest -->
```python
from clypi import Command

# With the flag ON: my-command --my-flag
# With the flag OFF: my-command
class MyCommand(Command):
    my_flag: bool = False
```


#### Options

Options are like flags but, instead of booleans, the user passes in specific values. You can think of options as key/pair items. Options can be set as required by not specifying a default value.

<!--- mdtest -->
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

<!--- mdtest -->
```python
from clypi import Command, arg

class MyCommand(Command):
    verbose: bool = False

    async def run(self):
        print(f"Running with verbose: {self.verbose}")
```

#### Help page

You can define custom help messages for each argument using our handy `config` helper:

<!--- mdtest -->
```python
from clypi import Command, arg

class MyCommand(Command):
    verbose: bool = arg(True, help="Whether to show all of the output")
```

You can also define custom help messages for commands by creating a docstring on the class itself:
<!--- mdtest -->
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

<!--- mdtest -->
```python
from clypi import Command, arg

class MyCommand(Command):
    name: str = arg(prompt="What's your name?")
```

On runtime, if the user didn't provide a value for `--name`, the program will ask the user to provide one until they do. You can also pass in a `default` value to `config` to allow the user to just hit enter to accept the default.

#### Built-in parsers

CLypi comes with built-in parsers for all common Python types. See the [`Parsers`](#parsers) section below to find all supported types and validations. Most often, using a normal Python type will automatically load the right parser, but if you want more control or extra features you can use these directly:

<!--- mdtest -->
```python
import typing as t
from clypi import Command, arg
import clypi.parsers as cp

class MyCommand(Command):
    file: Path = arg(parser=cp.Path(exists=True))
```

#### Custom parsers

If the type you want to parse from the user is too complex, you can define your own parser
using `config` as well:

<!--- mdtest -->
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

#### Forwarding arguments

If a command defines an argument you want to use in any of it's children, you can re-define the
argument and pass in a literal ellipsis (`...`) to config to indicate the argument comes from the
parent command. You can also use `forwarded=True` if you prefer:

<!--- mdtest -->
```python
from clypi import Command, arg

class MySubCmd(Command):
    verbose: bool = arg(...)  # or `arg(forwarded=True)`

class MyCli(Command):
    subcommand: MySubCmd
    verbose: bool = arg(False, help="Use verbose output")

cmd = MyCli.parse(["my-sub-cmd", "--verbose"])
assert cmd.subcommand.verbose is True
```

#### Autocomplete

All CLIs built with clypi come with a builtin `--install-autocomplete` option that will automatically
set up shell completions for your built CLI.

> [!IMPORTANT]
> This feature is brand new and might contain some bugs. Please file a ticket
> if you run into any!

#### `name`
```python
@t.final
@classmethod
def prog(cls)
```
The name of the command. Can be overridden to provide a custom name
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
        full_command: list[str],
        description: str | None,
        epilog: str | None,
        options: list[Argument],
        positionals: list[Argument],
        subcommands: list[type[Command]],
        exception: Exception | None,
    ) -> str: ...
```

### `ClypiFormatter`

```python
class ClypiFormatter(
    boxed=True,
    show_option_types=False,
    show_forwarded_options=True,
    normalize_dots="",
)
```
Parameters:
- `boxed`: whether to wrap each section in a box made with ASCII characters
- `show_option_types`: whether to display the expected type for each argument or just a placeholder. E.g.: `--foo TEXT` vs `--foo <FOO>`
- `show_forwarded_options`: whether to show forwarded arguments in child commands or only in parent commands
- `normalize_dots`: either `"."`, `""`, or `None`. If a dot, or empty, it will add or remove trailing dots from all help messages to keep a more consistent formatting across the application.


Clypi ships with a pre-made formatter that can display help pages with either boxes or with indented sections, and hideor show the option types. You can disable both the boxes and type of each option and display just a placeholder.

With everything enabled:

<!--- mdtest -->
```python
ClypiFormatter(boxed=True, show_option_types=True)
```

<img width="1696" alt="image" src="https://github.com/user-attachments/assets/3170874d-d120-4b1a-968a-f121e9b8ee53" />


With everything disabled:

<!--- mdtest -->
```python
ClypiFormatter(boxed=False, show_option_types=False)
```

<img width="1691" alt="image" src="https://github.com/user-attachments/assets/8838227b-d77d-4e1a-9670-32c7f430db40" />






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
    default: bool | Unset = UNSET,
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
    default: T | Unset = UNSET,
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

## UI

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
- `style`: the desired style (see [`Boxes`](#Boxes))
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

## Parsers

For this section, parsers will be imported as such:
```python
import clypi.parsers as cp
```

### `Int`

The `Int` parser converts string input into an integer.

```python
Int(
    gt: int | None = None,
    gte: int | None = None,
    lt: int | None = None,
    lte: int | None = None,
    max: int | None = None,
    min: int | None = None,
    positive: bool = False,
    nonpositive: bool = False,
    negative: bool = False,
    nonnegative: bool = False,

```

Parameters:
- `gt`: A value the integer must be greater than
- `gte`: A value the integer must be greater than or equal to
- `lt`: A value the integer must be less than
- `lte`: A value the integer must be less than or equal to
- `max`: The maximum value the integer can be (same as lte)
- `min`: The maximum value the integer can be (same as gte)
- `positive`: The integer must be greater than 0
- `nonpostive`: The integer must be less than or equal to 0
- `negative`: The integer must be less than 0
- `nonnegative`: The integer must be greater than or equal to 0

Examples:
<!--- mdtest -->
> ```python
> # 3 (OK), 10 (OK), 2 (not OK), 11 (not OK)
> cp.Int(lte=10, gt=2)
> ```

### `Float`

The `Float` parser converts string input into a floating-point number.

```python
Float(
    gt: float | None = None,
    gte: float | None = None,
    lt: float | None = None,
    lte: float | None = None,
    max: float | None = None,
    min: float | None = None,
    positive: bool = False,
    nonpositive: bool = False,
    negative: bool = False,
    nonnegative: bool = False,
)
```
Parameters:
- `gt`: A value the float must be greater than
- `gte`: A value the float must be greater than or equal to
- `lt`: A value the float must be less than
- `lte`: A value the float must be less than or equal to
- `max`: The maximum value the float can be (same as lte)
- `min`: The maximum value the float can be (same as gte)
- `positive`: The float must be greater than 0
- `nonpostive`: The float must be less than or equal to 0
- `negative`: The float must be less than 0
- `nonnegative`: The float must be greater than or equal to 0

Examples:
<!--- mdtest -->
> ```python
> # 3 (OK), 10 (OK), 2 (not OK), 11 (not OK)
> cp.Float(lte=10, gt=2)
> ```

### `Bool`

The `Bool` parser converts string input into a boolean.

```python
Bool()
```

Accepted values:
- `true`, `yes`, `y` → `True`
- `false`, `no`, `n` → `False`

### `Str`

The `Str` parser returns the string input as-is.

```python
Str(
    length: int | None = None,
    max: int | None = None,
    min: int | None = None,
    startswith: str | None = None,
    endswith: str | None = None,
    regex: str | None = None,
    regex_group: int | None = None,
)
```
Parameters:
- `length`: The string must be of this length
- `max`: The string's length must be at most than this number
- `min`: The string's length must be at least than this number
- `startswith`: The string must start with that substring
- `endsswith`: The string must end with that substring
- `regex`: The string must match this regular expression
- `regex_group`: (required `regex`) extracts the group from the regular expression

Examples:

<!--- mdtest -->
> ```python
> cp.Str(regex=r"[a-z]([0-9])", regex_group=1) # f1 -> 1
> ```

### `DateTime`

The `DateTime` parser converts string input into a `datetime` object.

```python
DateTime(
    tz: timezone | None = None,
)
```
Parameters:
- `tz`: the timezone to convert the date to

### `TimeDelta`

The `TimeDelta` parser converts string input into a `timedelta` object.

```python
TimeDelta(
    gt: timedelta | None = None,
    gte: timedelta | None = None,
    lt: timedelta | None = None,
    lte: timedelta | None = None,
    max: timedelta | None = None,
    min: timedelta | None = None,
)
```
- `gt`: A value the timedelta must be greater than
- `gte`: A value the timedelta must be greater than or equal to
- `lt`: A value the timedelta must be less than
- `lte`: A value the timedelta must be less than or equal to
- `max`: The maximum value the timedelta can be (same as lte)
- `min`: The maximum value the timedelta can be (same as gte)

Examples:
<!--- mdtest -->
> ```python
> # 1 day (OK), 2 weeks (OK), 1 second (not OK)
> cp.TimeDelta(gte=timedelta(days=1))
> ```

Supported time units:
- `weeks (w)`, `days (d)`, `hours (h)`, `minutes (m)`, `seconds (s)`, `milliseconds (ms)`, `microseconds (us)`

### `Path`

The `Path` parser is useful to parse file or directory-like arguments from the CLI.

```python
Path(exists: bool = False)
```
Parameters:
- `exists`: If `True`, it checks whether the provided path exists.

Examples:
<!--- mdtest -->
> ```python
> cp.Path(exists=True)
> ```

### `List`

The `List` parser parses comma-separated values into a list of parsed elements.

```python
List(inner: Parser[T])
```

Examples:
<!--- mdtest -->
> ```python
> cp.List(cp.Int())
> ```

Parameters:
- `inner`: The parser used to convert each list element.

### `Tuple`

The `Tuple` parser parses a string input into a tuple of values.

```python
Tuple(*inner: Parser, num: int | None = None)
```

Examples:
<!--- mdtest -->
> ```python
> # tuple[str, ...]
> cp.Tuple(cp.Str())
>
> # tuple[str, int]
> cp.Tuple(cp.Str(), cp.Int(), num=2)
> ```

Parameters:
- `inner`: List of parsers for each tuple element.
- `num`: Expected tuple length (optional).

### `Union`

The `Union` parser attempts to parse input using multiple parsers.

```python
Union(left: Parser[X], right: Parser[Y])
```

You can also use the short hand `|` syntax for two parsers, e.g.:
<!--- mdtest -->
> ```python
> cp.Union(cp.Path(exists=True), cp.Str())
> cp.Path(exists=True) | cp.Str()
> ```

### `Literal`

The `Literal` parser ensures that input matches one of the predefined values.

```python
Literal(*values: t.Any)
```

Examples:
<!--- mdtest -->
> ```python
> cp.Literal(1, "foo")
> ```

### `Enum`

The `Enum` parser maps string input to a valid enum value.

```python
Enum(enum: type[enum.Enum])
```

Examples:
<!--- mdtest -->
> ```python
> class Color(Enum):
>     RED = 1
>     BLUE = 2
>
> cp.Enum(Color)
> ```

### `from_type`

The `from_type` function returns the appropriate parser for a given type.

```python
@tu.ignore_annotated
def from_type(_type: type) -> Parser: ...
```

Examples:
<!--- mdtest -->
> ```python
> assert cp.from_type(bool) == cp.Bool()
> ```
