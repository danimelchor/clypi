from term import Command


class Lint(Command):
    files: tuple[str, ...]

    async def run(self):
        print(f"Linting {', '.join(self.files)}")


class MyCli(Command):
    subcommand: Lint | None = None
    verbose: bool = False

    async def run(self):
        print(f"Running the main command with {self.verbose}")


if __name__ == "__main__":
    cli = MyCli.parse()
    cli.start()
