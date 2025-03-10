from clypi import Command, Positional, arg


class Lint(Command):
    files: Positional[tuple[str, ...]]
    verbose: bool = arg(...)  # Comes from MyCli but I want to use it too

    async def run(self):
        print(f"Linting {', '.join(self.files)} and {self.verbose=}")


class MyCli(Command):
    """
    my-cli is a very nifty demo CLI tool
    """

    subcommand: Lint | None = None
    verbose: bool = arg(
        help="Weather to show extra logs",
        prompt="Do you want to see extra logs?",
        default=False,
        short="v",  # User can pass in --verbose or -v
    )

    async def run(self):
        print(f"Running the main command with {self.verbose}")


if __name__ == "__main__":
    cli: MyCli = MyCli.parse()
    cli.start()
