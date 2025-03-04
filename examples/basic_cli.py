from clypi import Command, config


class Lint(Command):
    """
    A basic example of clypi's subcommands
    """

    files: tuple[str, ...]

    async def run(self, root):
        print(f"Linting {', '.join(self.files)}")


class MyCli(Command):
    """
    A basic example of clypi
    """

    subcommand: Lint | None = None
    verbose: bool = config(short="v", default=False)
    name: str = config(prompt="What's your name?", help="The name of the user")

    async def run(self, root):
        print(f"Running the main command with {self.verbose} and {self.name}")


if __name__ == "__main__":
    cli: MyCli = MyCli.parse()
    cli.start()
