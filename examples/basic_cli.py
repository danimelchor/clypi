from clypi import Command, config


class Lint(Command):
    files: tuple[str, ...]

    async def run(self, root):
        print(f"Linting {', '.join(self.files)}")


class MyCli(Command):
    subcommand: Lint | None = None
    verbose: bool = config(short="v", default=False)

    async def run(self, root):
        print(f"Running the main command with {self.verbose}")


if __name__ == "__main__":
    cli: MyCli = MyCli.parse()
    cli.start()
