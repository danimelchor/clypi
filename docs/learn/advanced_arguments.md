## Argument inheritance

Say you have arguments that you want every command to be able to use but you want to avoid
having to copy paste their definition over and over on every command. Clypi provides an intuitive
solution for this issue: argument inheritance.

The idea is easy: define the arguments in a parent command and all children will be able to use them
without having to redefine them.

<!-- mdtest -->
```python title="cli.py" hl_lines="7 18-20"
from clypi import Command, Positional, arg
from typing_extensions import override

class Wave(Command):
    """Wave at someone"""
    name: Positional[str]
    verbose: bool = arg(inherited=True)

    @override
    async def run(self) -> None:
        print(f"👋 Hey {self.name}")
        if self.verbose:
            print(f"👋👋👋 HEYYY {self.name}")

class Cli(Command):
    """A very simple CLI"""
    subcommand: Wave | None
    verbose: bool = arg(
        False, short="v", help="Whether to show verbose output", group="global"
    )

if __name__ == "__main__":
    cmd = Cli.parse()
    cmd.start()
```

You will see even though the help message for `verbose` is defined in the parent command,
the subcommand `Wave` gets the entire argument definition for free:

<!-- termynal -->
```
$ python cli.py wave --help
Wave at someone

Usage: cli wave [NAME] [OPTIONS]

┏━ Arguments ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ [NAME]                                                                       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━ Global options ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ -v, --verbose   Whether to show verbose output                               ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛


$ python cli.py Daniel
👋 Hey Daniel


$ python cli.py Daniel -v
👋 Hey Daniel
👋👋👋 HEYYY Daniel
```


## Deferring arguments

CLIs can get very complex. Sometimes we want to build a complex graph of dependencies between the arguments and it is hard to do that. For example, we can have an application that does not use `--num-cores` if `--single-threaded` was provided already. For that, clypi offers `arg(defer=True)`.

The internals are complex but the user experience is quite simple: clypi will not prompt or require this value being passed up until when it's executed.

<!-- mdtest-stdin 5 -->
```python hl_lines="7 19"
from clypi import Command, arg
from typing_extensions import override

class Cli(Command):
    single_threaded: bool = arg(False)
    num_cores: int = arg(
        defer=True,
        prompt="How many CPU cores do you want to use?"
    )

    @override
    async def run(self):
        print(f"Running single theaded:", self.single_threaded)  # << will not prompt yet...
        if self.single_threaded:
            # if we never access num_cores in this if condition, we will
            # never prompt!
            print("Running single threaded...")
        else:
            threads = self.num_cores // 4  # << we prompt here!
            print("Running with threads:", threads)

if __name__ == "__main__":
    cmd = Cli.parse()  # << will not prompt yet...
    cmd.start()  # << will not prompt yet...
```

As you can see, we are prompted only if we do not specify `--single-threaded` and only
after we've printed the `"Running single threaded: False"` message:

<!-- termynal -->
```
$ python cli.py --single-threaded
Running single theaded: True
Running single threaded...


$ python cli.py
Running single theaded: False
How many CPU cores do you want to use?: 16
Running with threads: 4
```

## Custom parsers

If the type you want to parse from the user is too complex, you can define your own parser
using `config` as well:

<!-- mdtest -->
```python hl_lines="4-7 10"
import typing as t
from clypi import Command, arg

def parse_slack(value: t.Any) -> str:
    if not value.startswith('#'):
        raise ValueError("Invalid Slack channel. It must start with a '#'.")
    return value

class MyCommand(Command):
    slack: str = arg(parser=parse_slack)
```
