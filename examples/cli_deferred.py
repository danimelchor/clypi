import clypi.parsers as cp
from clypi import Command, arg, cprint


class VerboseIntParser(cp.Int):
    """Helper parser to show the user when the parsing is being done"""

    def __call__(self, raw: str | list[str], /) -> int:
        cprint(f"⚠️ The call to to parse {raw} as an int was executed!", fg="yellow")
        return super().__call__(raw)


class Main(Command):
    runner: bool = arg(
        False,
        help="Whether you run",
        prompt="Do you run?",
    )
    often: int = arg(
        help="The frequency you run with in days",
        prompt="How many days a week do you run?",
        defer=True,
        parser=VerboseIntParser(),
    )

    async def run(self):
        print("Command execution started...")

        if not self.runner:
            cprint("You are not a runner!", fg="green", bold=True)
            cprint("Try answering yes on the next try :)", bold=True)
        else:
            cprint(
                # This line will trigger the evaluation of `often` and prompt
                # the user if it was not provided as a CLI arg
                f"You are a runner and run every {self.often} days!",
                fg="green",
                bold=True,
            )
            cprint("Try answering no on the next try :)", bold=True)


if __name__ == "__main__":
    main: Main = Main.parse()
    main.start()
