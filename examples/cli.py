import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from typing_extensions import override

import term
from term.cli import Command, field


@dataclass
class RunParallel(Command):
    files: list[str]
    exceptions_file: str | Path | None = None

    async def run(self):
        async with term.Spinner(f"Running {', '.join(self.files)} in parallel"):
            await asyncio.sleep(2)
        term.print("Done!", fg="green", bold=True)


@dataclass
class RunSerial(Command):
    files: list[str]

    async def run(self):
        async with term.Spinner(f"Running {', '.join(self.files)} sequentially"):
            await asyncio.sleep(2)
        term.print("Done!", fg="green", bold=True)


@dataclass
class Run(Command):
    subcommand: RunParallel | RunSerial
    quiet: bool = False
    format: Literal["json", "pretty"] = "pretty"


@dataclass
class Lint(Command):
    """
    Lints all of the files in a given directory using the latest termuff
    rules.
    """

    files: list[str] = field(help="The list of files to lint")
    quiet: bool = field(
        help="If the linter should omit all stdout messages", default=False
    )
    no_cache: bool = field(help="Disable the termuff cache", default=False)
    index: str = field(
        default="http://pypi.org",
        help="The index to download termuff from",
    )

    async def run(self):
        async with term.Spinner(f"Linting {', '.join(self.files)}"):
            await asyncio.sleep(2)
        term.print("Done!", fg="green", bold=True)


@dataclass
class Main(Command):
    """
    Termuff is a powerful command line interfact to lint and
    run arbitrary files.
    """

    subcommand: Run | Lint
    verbose: bool

    @override
    @classmethod
    def prog(cls):
        return "termuff"

    @override
    @classmethod
    def epilog(cls):
        return "Learn more at http://termuff.org"


if __name__ == "__main__":
    main = Main.parse()
    print(main)
    main.start()
