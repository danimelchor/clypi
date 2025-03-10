import asyncio
from enum import Enum
from pathlib import Path
from typing import Literal

import v6e as v
from typing_extensions import override

import clypi
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
    exceptions_with_reasons: Path | None = arg(
        default=None,
        parser=v.path().exists(),
    )
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

    files: Positional[list[Path]] = arg(parser=v.list(v.path().exists()))
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
    quiet: bool = False
    env: Env = Env.PROD
    format: Literal["json", "pretty"] = "pretty"


class Lint(Command):
    """
    Lints all of the files in a given directory using the latest
    termuff rules.
    """

    files: Positional[list[str]] = arg(help="The list of files to lint")
    quiet: bool = arg(
        short="q",
        help="If the linter should omit all stdout messages",
        default=False,
    )
    timeout: int = arg(help="Disable the termuff cache")
    index: str = arg(
        default="http://pypi.org",
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
    Termuff is a powerful command line interfact to lint and
    run arbitrary files.
    """

    subcommand: Run | Lint | None = None
    verbose: bool = arg(short="v", default=False)

    @override
    @classmethod
    def prog(cls):
        return "termuff"

    @override
    @classmethod
    def epilog(cls):
        return "Learn more at http://termuff.org"

    @debug
    async def run(self):
        self.print_help()


if __name__ == "__main__":
    main: Main = Main.parse()
    main.start()
