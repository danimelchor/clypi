import asyncio
from pathlib import Path
from typing import Literal

import v6e as v
from typing_extensions import override

import term
from term import Command, config


def debug(fun):
    """
    Just a utility decorator to display the root commands being passed in a somewhat
    nice way
    """

    async def inner(self, root):
        boxed = term.boxed(term.style(root, bold=True), title="Debug", color="magenta")
        print(boxed, end="\n\n")
        await fun(self, root)

    return inner


class RunParallel(Command):
    """
    Runs all of the files in parallel
    """

    files: list[str]
    exceptions_with_reasons: Path | None = config(
        default=None,
        parser=v.path().exists(),
    )

    @debug
    async def run(self, root):
        async with term.Spinner(f"Running {', '.join(self.files)} in parallel"):
            await asyncio.sleep(2)
        term.print("Done!", fg="green", bold=True)


class RunSerial(Command):
    """
    Runs all of the files one by one
    """

    files: list[Path] = config(parser=v.list(v.path().exists()))

    @debug
    async def run(self, root):
        files_str = ", ".join(p.as_posix() for p in self.files)
        async with term.Spinner(f"Running {files_str} sequentially"):
            await asyncio.sleep(2)
        term.print("Done!", fg="green", bold=True)


class Run(Command):
    """
    Allows running files with different options
    """

    subcommand: RunParallel | RunSerial
    quiet: bool = False
    format: Literal["json", "pretty"] = "pretty"


class Lint(Command):
    """
    Lints all of the files in a given directory using the latest
    termuff rules.
    """

    files: list[str] = config(help="The list of files to lint")
    quiet: bool = config(
        short="q",
        help="If the linter should omit all stdout messages",
        default=False,
    )
    no_cache: bool = config(help="Disable the termuff cache", default=False)
    index: str = config(
        default="http://pypi.org",
        help="The index to download termuff from",
    )

    @debug
    async def run(self, root):
        async with term.Spinner(f"Linting {', '.join(self.files)}"):
            await asyncio.sleep(2)
        term.print("Done!", fg="green", bold=True)


class Main(Command):
    """
    Termuff is a powerful command line interfact to lint and
    run arbitrary files.
    """

    subcommand: Run | Lint | None = None
    verbose: bool = config(short="v", default=False)

    @override
    @classmethod
    def prog(cls):
        return "termuff"

    @override
    @classmethod
    def epilog(cls):
        return "Learn more at http://termuff.org"

    @debug
    async def run(self, root):
        self.print_help()


if __name__ == "__main__":
    main: Main = Main.parse()
    main.start()
