## Your first CLI

An extremely simple clypi CLI can be built in a couple of lines:

<!-- mdtest -->
```python title="cli.py"
from clypi import Command
from typing_extensions import override

class Cli(Command):
    @override
    async def run(self):
        print(f"Hello, world!")

if __name__ == '__main__':
    cmd = Cli.parse()
    cmd.start()
```

<!-- termynal -->
```
$ python cli.py --help
Usage: cli
```

## Adding positional arguments

Positional arguments are unnamed arguments provided by the user in a specific order. We only
care about the position they are in (hence the name positional).

In this example, whatever the first argument to our program is will be passed in as `name`,
and the second argument will be passed as `age` since they're defined in that order.

<!-- mdtest-args foo 1 -->
```python title="cli.py" hl_lines="5-6"
from clypi import Command, Positional
from typing_extensions import override

class Cli(Command):
    name: Positional[str]
    age: Positional[int]

    @override
    async def run(self):
        print(f"Hello, {self.name}. You are {self.age}!")

if __name__ == '__main__':
    cmd = Cli.parse()
    cmd.start()
```

<!-- termynal -->
```
$ python cli.py --help
Usage: cli [NAME] [AGE]

┏━ Arguments ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ [NAME]                                                                       ┃
┃ [AGE]                                                                        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

If we run it:

<!-- termynal -->
```
$ python cli.py Daniel 22
Hello, Daniel. You are 22!
```

## Adding options

Options are named arguments, and they are usually optional. A user of your CLI must provide the name of the argument and the value(s) to assign to it.

<!-- mdtest-args foo -->
```python title="cli.py" hl_lines="6"
from clypi import Command, Positional
from typing_extensions import override

class Cli(Command):
    name: Positional[str]
    age: int | None = None

    @override
    async def run(self):
        print(f"Hello, {self.name}.")
        if self.age is not None:
            print(f"You are {self.age}!")

if __name__ == '__main__':
    cmd = Cli.parse()
    cmd.start()
```


<!-- termynal -->
```
$ python cli.py --help
Usage: cli [NAME] [OPTIONS]

┏━ Arguments ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ [NAME]                                                                       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━ Options ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ --age <AGE>                                                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

If we run it with and without the `--age` flag, we get:

<!-- termynal -->
```
$ python cli.py Daniel
Hello, Daniel.


$ python cli.py Daniel --age 22
Hello, Daniel.
You are 22!
```

## Adding documentation

As it stands right now, our CLI is a bit difficult to use. We can add documentation
to help our users understand what our CLI is and how to use it.

To document the overall command we can use Python docstrings. To document each argument
and option we can make user of clypi's `arg` helper.

<!-- mdtest-args foo --age 10 -->
```python title="cli.py" hl_lines="5 7 8"
from clypi import Command, Positional, arg
from typing_extensions import override

class Cli(Command):
    """A very simple CLI"""

    name: Positional[str] = arg(help="Your name")
    age: int | None = arg(None, help="Your age in years")

    @override
    async def run(self):
        print(f"Hello, {self.name}.")
        if self.age is not None:
            print(f"You are {self.age}!")

if __name__ == '__main__':
    cmd = Cli.parse()
    cmd.start()
```


<!-- termynal -->
```
$ python cli.py --help
A very simple CLI

Usage: cli [NAME] [OPTIONS]

┏━ Arguments ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ [NAME]  Your name                                                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━ Options ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ --age <AGE>  Your age in years                                               ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

## Adding subcommands

Our applications sometimes have multiple usecases. To better group each usecase and avoid
having too many options and arguments, we can create subcommands. Subcommands allow the user
to select which tool to use inside your CLI.

Creating subcommands is very easy. Just create more commands and then define a class-level attribute
in your main CLI with the name `subcommand`:

<!-- mdtest-args wave daniel -->
```python title="cli.py" hl_lines="22"
from clypi import Command, Positional, arg
from typing_extensions import override

class Greet(Command):
    """Say hi to someone"""
    name: Positional[str] = arg(help="Your name")

    @override
    async def run(self):
        print(f"Hello, {self.name}")

class Wave(Command):
    """Wave at someone"""
    name: Positional[str] = arg(help="Your name")

    @override
    async def run(self):
        print(f"👋 {self.name}")

class Cli(Command):
    """A very simple CLI"""
    subcommand: Greet | Wave

if __name__ == '__main__':
    cmd = Cli.parse()
    cmd.start()
```

<!-- termynal -->
```
$ python cli.py --help
A very simple CLI

Usage: cli COMMAND

┏━ Subcommands ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ greet  Say hi to someone                                                     ┃
┃ wave   Wave at someone                                                       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛


$ python cli.py greet --help
Say hi to someone

Usage: cli greet [NAME]

┏━ Arguments ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ [NAME]  Your name                                                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛


$ python cli.py wave Daniel
👋 Daniel
```

## Prompting for values

Sometimes we want to make arguments required (by not providing a default) but we don't want to
force our users to pass in an argument directly. We might want to ask them in a more user-friendly
way. For that, we can set up a prompt in case the user does not manually pass in a value:

<!-- mdtest-stdin Daniel -->
```python title="cli.py" hl_lines="6"
from clypi import Command, Positional, arg
from typing_extensions import override

class Cli(Command):
    """A very simple CLI"""
    name: Positional[str] = arg(prompt="What's your name?")

    @override
    async def run(self):
        print(f"Hello, {self.name}!")

if __name__ == '__main__':
    cmd = Cli.parse()
    cmd.start()
```


<!-- termynal -->
```
$ python cli.py
What's your name?: Daniel
Hello, Daniel!


$ python cli.py Daniel
Hello, Daniel!
```

## Built-in parsers

Clypi comes with built-in parsers for all common Python types. See the [built-in types](../api/parsers.md#supported-built-in-types) section in the API docs to find all supported types and validations. Most often, using a normal Python type will automatically load the right parser, but if you want more control or extra features you can use these directly:

<!-- mdtest-args . -->
```python hl_lines="2 6"
from clypi import Command, arg
import clypi.parsers as cp

class MyCommand(Command):
    file: Path = arg(
        parser=cp.Path(exists=True),
    )
```

You can also create your own parser if there's a complex data type we do not support. Refer to the [Custom parsers](./advanced_arguments.md/#custom-parsers) docs.


## Argument groups

Sometimes you want to separate your options based on behaviors. For example, you might want to split up environment options from output options. For that, just define a `group` parameter in the `arg`s you want to group together:

<!-- mdtest-stdin Daniel -->
```python title="cli.py" hl_lines="15 20"
from typing import Literal
from clypi import Command, arg

class Cli(Command):
    """A very simple CLI"""

    # Output configs here
    format: Literal["json", "raw"] = arg("raw", help="The output format to use")
    verbose: bool = arg(False, help="Whether to show verbose output")

    # Cluster configs here...
    env: Literal["qa", "prod"] = arg(
        "qa",
        help="The environment to run in",
        group="environment",
    )
    cluster: Literal["default", "secondary"] = arg(
        "default",
        help="The cluster to run in",
        group="environment",
    )

if __name__ == '__main__':
    cmd = Cli.parse()
    cmd.start()
```

You can see they now get displayed in different groups:

<!-- termynal -->
```
$ python cli.py --help
A very simple CLI

Usage: cli [OPTIONS]

┏━ Options ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ --format <FORMAT>  The output format to use {JSON|RAW}                       ┃
┃ --verbose          Whether to show verbose output                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━ Environment options ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ --env <ENV>          The environment to run in {QA|PROD}                     ┃
┃ --cluster <CLUSTER>  The cluster to run in {DEFAULT|SECONDARY}               ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```
