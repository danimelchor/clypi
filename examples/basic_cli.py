from clypi import Command, config


class Lint(Command):
    files: tuple[str, ...]

    async def run(self):
        print(f"Linting {', '.join(self.files)}")


class MyCli(Command):
    """
    my-cli is a very nifty demo CLI tool
    """

    subcommand: Lint | None = None
    verbose: bool = config(
        help="Wether to show extra logs",
        prompt="Do you want to see extra logs?",
        default=False,
        short="v",
    )

    async def run(self):
        print(f"Running the main command with {self.verbose}")


if __name__ == "__main__":
    cli: MyCli = MyCli.parse()
    cli.start()
