import asyncio
from enum import Enum
from pathlib import Path
from typing import Literal

from typing_extensions import override

import clypi
import clypi.parsers as cp
from clypi import Command, Positional, arg


def debug(fun):
    """
    Just a utility decorator to display the commands being passed in a somewhat
    nice way
    """

    async def inner(self):
        boxed = clypi.boxed(
            clypi.style(self, bold=True), title="Debug", color="magenta"
        )
        print(boxed, end="\n\n")
        await fun(self)

    return inner


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
        clypi.print(f"{self.env.name} - Running all files", fg="blue", bold=True)

        async with clypi.Spinner(f"Running {', '.join(self.files)} in parallel"):
            await asyncio.sleep(2)

        async with clypi.Spinner(f"Linting {', '.join(self.files)} in parallel"):
            await asyncio.sleep(2)

        clypi.print("\nDone!", fg="green", bold=True)


class RunSerial(Command):
    """
    Runs all of the files one by one
    """

    files: Positional[list[Path]] = arg(parser=cp.List(cp.Path(exists=True)))
    env: Env = arg(...)

    @debug
    async def run(self):
        clypi.print(f"{self.env.name} - Running all files", fg="blue", bold=True)
        for f in self.files:
            async with clypi.Spinner(f"Running {f.as_posix()} in parallel"):
                await asyncio.sleep(2)
        clypi.print("\nDone!", fg="green", bold=True)


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
    format: Literal["json", "pretty"] = arg(
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
    async def run(self):
        async with clypi.Spinner(f"Linting {', '.join(self.files)}"):
            await asyncio.sleep(self.timeout)
        clypi.print("\nDone!", fg="green", bold=True)


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
