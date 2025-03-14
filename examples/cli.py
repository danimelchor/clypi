import asyncio
import typing as t
from enum import Enum
from pathlib import Path
from types import CoroutineType

from typing_extensions import override

import clypi.parsers as cp
from clypi import Command, Positional, Spinner, arg, boxed, cprint, style

# ---- START DEMO UTILS ----
P = t.ParamSpec("P")
R = t.TypeVar("R")
CommandT = t.TypeVar("CommandT", bound=Command)
AsyncFunc = t.Callable[t.Concatenate[CommandT, P], CoroutineType[t.Any, t.Any, None]]


def debug(fun: AsyncFunc[CommandT, P]) -> AsyncFunc[CommandT, P]:
    """
    Just a utility decorator to display the commands being passed in a somewhat
    nice way
    """

    def inner(self: CommandT, *args: P.args, **kwargs: P.kwargs):
        box = boxed(style(self, bold=True), title="Debug", color="magenta")
        print(box, end="\n\n")
        return fun(self, *args, **kwargs)

    return inner


# ---- END DEMO UTILS ----


class Env(Enum):
    QA = 1
    PROD = 2


class RunParallel(Command):
    """
    Runs all of the files in parallel
    """

    files: Positional[list[str]]
    exceptions_with_reasons: Path | None = arg(None, parser=cp.Path(exists=True))
    env: Env = arg(...)

    @debug
    async def run(self):
        cprint(f"{self.env.name} - Running all files", fg="blue", bold=True)

        async with Spinner(f"Running {', '.join(self.files)} in parallel"):
            await asyncio.sleep(2)

        async with Spinner(f"Linting {', '.join(self.files)} in parallel"):
            await asyncio.sleep(2)

        cprint("\nDone!", fg="green", bold=True)


class RunSerial(Command):
    """
    Runs all of the files one by one
    """

    files: Positional[list[Path]] = arg(parser=cp.List(cp.Path(exists=True)))
    env: Env = arg(...)

    @debug
    async def run(self):
        cprint(f"{self.env.name} - Running all files", fg="blue", bold=True)
        for f in self.files:
            async with Spinner(f"Running {f.as_posix()} in parallel"):
                await asyncio.sleep(2)
        cprint("\nDone!", fg="green", bold=True)


class Run(Command):
    """
    Allows running files with different options
    """

    subcommand: RunParallel | RunSerial
    quiet: bool = arg(
        False,
        short="q",
        help="If the runner should omit all stdout messages",
    )
    env: Env = arg(Env.PROD, help="The environment to run in")
    format: t.Literal["json", "pretty"] = arg(
        "pretty", help="The format with which to display results"
    )


class Lint(Command):
    """
    Lints all of the files in a given directory using the latest
    termuff rules.
    """

    files: Positional[list[str]] = arg(help="The list of files to lint")
    quiet: bool = arg(
        False,
        short="q",
        help="If the linter should omit all stdout messages",
    )
    timeout: int = arg(help="Disable the termuff cache")
    index: str = arg(
        "http://pypi.org",
        help="The index to download termuff from",
        prompt="What index do you want to download termuff from?",
    )

    @debug
    async def run(self) -> None:
        async with Spinner(f"Linting {', '.join(self.files)}"):
            await asyncio.sleep(self.timeout)
        cprint("\nDone!", fg="green", bold=True)


class Main(Command):
    """
    Termuff is a powerful command line interface to lint and
    run arbitrary files.
    """

    subcommand: Run | Lint | None = None
    verbose: bool = arg(False, short="v", help="Weather to show more output")

    @override
    @classmethod
    def prog(cls):
        return "termuff"

    @override
    @classmethod
    def epilog(cls):
        return "Learn more at http://termuff.org"


if __name__ == "__main__":
    main: Main = Main.parse()
    main.start()
