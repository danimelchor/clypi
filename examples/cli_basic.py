from pathlib import Path

import clypi.parsers as cp
from clypi import Command, Positional, arg


class Lint(Command):
    files: Positional[tuple[Path, ...]]
    verbose: bool = arg(inherited=True)  # Comes from MyCli but I want to use it too

    async def run(self):
        print(f"Linting {self.files=} and {self.verbose=}")


class MyCli(Command):
    """
    my-cli is a very nifty demo CLI tool
    """

    subcommand: Lint | None = None
    threads: int = arg(
        default=4,
        # Built-in parsers for useful validations
        parser=cp.Int(min=1, max=10),
    )
    verbose: bool = arg(
        False,
        help="Whether to show extra logs",
        prompt="Do you want to see extra logs?",
        short="v",  # User can pass in --verbose or -v
    )

    async def run(self):
        print(f"Running the main command with {self.verbose}")


if __name__ == "__main__":
    cli: MyCli = MyCli.parse()
    cli.start()
