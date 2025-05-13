## `arg`

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
    negative: str | None = None,
    group: str | None = None,
) -> T
```

Utility function to configure how a specific argument should behave when displayed
and parsed.

Parameters:

- `default`: the default value to return if the user doesn't pass in the argument (or hits enter during the prompt, if any)
- `parser`: a function that takes in a string and returns the parsed type (see [`Parser`](./parsers.md))
- `default_factory`: a function that returns a default value. Useful to defer computation or to avoid default mutable values
- `help`: a brief description to show the user when they pass in `-h` or `--help`
- `short`: for options it defines a short way to pass in a value (e.g.: `short="v"` allows users to pass in `-v <value>`)
- `prompt`: if defined, it will ask the user to provide input if not already defined in the command line args
- `hide_input`: whether the input shouldn't be displayed as the user types (for passwords, API keys, etc.)
- `max_attempts`: how many times to ask the user before giving up and raising
- `group`: optionally define the name of a group to display the option in. Adding an option will automatically display the options in a different section of the help page (see the [Argument groups](../learn/getting_started.md#argument-groups) docs).
- `negative`: defines the negative argument to set a flag as False. Useful for flags that have prompts so that they can be programmatically set to False.
- `defer` (advanced): defers the fetching of a value until the value is used. This can be helpful to express complex dependencies between arguments. For example, you may not want to prompt if a different option was passed in (see `examples/cli_deferred.py`).

## `Command`

This is the main class you must extend when defining a command. There are no methods you must override
other than the [`run`](#run) method.

Clypi supports:

- Long options: `--foo 123` or `--foo=123`
- Short options: `-f 123` or `-f=123`
- Flags: `--verbose`
- <!-- md:version 1.2.12 --> Concatenated short options: `-a -b -c` is the same as `-abc`
- <!-- md:version 1.2.13 --> A double dash (`--`) stops parsing: `my-cli foo -- anything after is okay`


### Subcommands

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

### Arguments (positional)

Arguments are mandatory positional words the user must pass in. They're defined as class attributes with no default and type hinted with the `Positional[T]` type.

<!-- mdtest-args 5 foo bar baz -->
```python hl_lines="6 7"
from clypi import Command, Positional

# my-command 5 foo bar baz
#        arg1^ ^^^^^^^^^^^arg2
class MyCommand(Command):
    arg1: Positional[int]
    arg2: Positional[list[str]]

main = MyCommand.parse()
main.start()
```

### Flags

Flags are boolean options that can be either present or not. To define a flag, simply define
a boolean class attribute in your command with a default value. The user will then be able
to pass in `--my-flag` when running the command which will set it to True.

<!-- mdtest -->
```python hl_lines="6"
from clypi import Command

# With the flag ON: my-command --my-flag
# With the flag OFF: my-command
class MyCommand(Command):
    my_flag: bool = False

main = MyCommand.parse()
main.start()
```

#### Negative flags

You can define negative flag names for each flag using our handy `arg` helper and `negative`. This will configure an option users can pass that will set the flag to False. This is useful for flags that prompt so that they can be set to any value from the command line:

<!-- mdtest-args --no-my-flag -->
```python hl_lines="7"
from clypi import Command, arg

# With the flag ON: my-command --my-flag
# With the flag OFF: my-command --no-my-flag
# With no value: will prompt
class MyCommand(Command):
    my_flag: bool = arg(False, prompt="Value for my-flag?", negative="no_my_flag")

main = MyCommand.parse()
main.start()
```

### Options

Options are like flags but, instead of booleans, the user passes in specific values. You can think of options as key/pair items. Options can be set as required by not specifying a default value.

<!-- mdtest -->
```python hl_lines="6"
from clypi import Command

# With value: my-command --my-attr foo
# With default: my-command
class MyCommand(Command):
    my_attr: str | int = "some-default-here"

main = MyCommand.parse()
main.start()
```

### Running the command

You must implement the [`run`](#run) method so that your command can be ran. The function
must be `async` so that we can properly render items in your screen.

<!-- mdtest -->
```python hl_lines="7 8"
from clypi import Command
from typing_extensions import override

class MyCommand(Command):
    verbose: bool = False

    @override
    async def run(self):
        print(f"Running with verbose: {self.verbose}")

main = MyCommand.parse()
main.start()
```

### Help page

You can define custom help messages for each argument using our handy `arg` helper:

<!-- mdtest -->
```python hl_lines="6"
from clypi import Command, arg

class MyCommand(Command):
    verbose: bool = arg(
        True,
        help="Whether to show all of the output"
    )

main = MyCommand.parse()
main.start()
```

You can also define custom help messages for commands by creating a docstring on the class itself:
<!-- mdtest -->
```python hl_lines="5 6"
from clypi import Command

class MyCommand(Command):
    """
    This text will show up when someone does `my-command --help`
    and can contain any info you'd like
    """

main = MyCommand.parse()
main.start()
```

### Prompting

If you want to ask the user to provide input if it's not specified, you can pass in a prompt to `arg` for each field like so:

<!-- mdtest-stdin foo -->
```python hl_lines="4"
from clypi import Command, arg

class MyCommand(Command):
    name: str = arg(prompt="What's your name?")

main = MyCommand.parse()
main.start()
```

On runtime, if the user didn't provide a value for `--name`, the program will ask the user to provide one until they do. You can also pass in a `default` value to `arg` to allow the user to just hit enter to accept the default.

### Autocomplete

All CLIs built with clypi come with a builtin `--install-autocomplete` option that will automatically
set up shell completions for your built CLI.

> [!WARNING]
> This feature is brand new and might contain some bugs. Please file a ticket
> if you run into any!

### `name`
```python
@t.final
@classmethod
def prog(cls)
```
The name of the command. Can be overridden to provide a custom name
or will default to the class name extending `Command`.

### `epilog`
```python
@t.final
@classmethod
def epilog(cls)
```
Optionally define text to display after the help message

### `full_command`
```python
@t.final
@classmethod
def full_command(cls)
```
The full path of commands to the current command being ran.

### `parents`
```python
@t.final
@classmethod
def parents(cls)
```
A list of parent commands for this command.

### `get_unparsed`

<!-- md:version 1.2.13 -->

```python
@t.final
@classmethod
def get_unparsed(cls)
```
The list of unparsed arguments for this command. If a user passes in `--`, anything after
the double dash will be left unparsed for the command to process as they wish.

### `help`
```python
@t.final
@classmethod
def help(cls)
```
The help displayed for the command when the user passes in `-h` or `--help`. Defaults to the
docstring for the class extending `Command`.

### `run`
```python
async def run(self: Command) -> None:
```
The main function you **must** override. This function is where the business logic of your command
should live.

`self` contains the arguments for this command you can access
as you would do with any other instance property.


### `astart` and `start`
```python
async def astart(self: Command | None = None) -> None:
```
```python
def start(self) -> None:
```
These commands are the entry point for your program. You can either call `YourCommand.start()` on your class
or, if already in an async loop, `await YourCommand.astart()`.


### `print_help`
```python
@classmethod
def print_help(cls, exception: Exception | None = None)
```
Prints the help page for a particular command.

Parameters:

- `exception`: an exception neatly showed to the user as a traceback. Automatically passed in during runtime.

### `pre_run_hook`


<!-- md:version 1.2.7 -->

```python
async def pre_run_hook(self: Command) -> None:
```
A function that will run on every parent command and subcommand right before it's execution. Useful
to print before commands, emit metrics, and more!

Examples:

<!-- mdtest -->
```python hl_lines="5-7"
import logging
from typing_extensions import override
from clypi import Command

class MyCommand(Command):
    @override
    async def pre_run_hook(self):
        cmd_str = " ".join(self.full_command())
        logging.debug("Running %s", cmd_str)

    @override
    async def run(self):
        print("Hey")

main = MyCommand.parse()
main.start()
```

### `post_run_hook`

<!-- md:version 1.2.7 -->

```python
async def post_run_hook(self: Command, exception: Exception | None) -> None:
```
A function that will run on every parent command and subcommand right after it's execution. Useful
to print after commands, process exceptions, emit metrics, and more!

## `Formatter`

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

## `ClypiFormatter`

```python
class ClypiFormatter(
    boxed=True,
    show_option_types=False,
    show_inherited_options=True,
    normalize_dots="",
)
```
Parameters:

- `boxed`: whether to wrap each section in a box made with ASCII characters
- `show_option_types`: whether to display the expected type for each argument or just a placeholder. E.g.: `--foo TEXT` vs `--foo <FOO>`
- `show_inherited_options`: whether to show inherited arguments in child commands or only in parent commands
- `normalize_dots`: either `"."`, `""`, or `None`. If a dot, or empty, it will add or remove trailing dots from all help messages to keep a more consistent formatting across the application.


Clypi ships with a pre-made formatter that can display help pages with either boxes or with indented sections, and hideor show the option types. You can disable both the boxes and type of each option and display just a placeholder.

With everything enabled:

<!-- mdtest -->
```python
ClypiFormatter(boxed=True, show_option_types=True)
```

<img width="1696" alt="image" src="https://github.com/user-attachments/assets/3170874d-d120-4b1a-968a-f121e9b8ee53" />


With everything disabled:

<!-- mdtest -->
```python
ClypiFormatter(boxed=False, show_option_types=False)
```

<img width="1691" alt="image" src="https://github.com/user-attachments/assets/8838227b-d77d-4e1a-9670-32c7f430db40" />
