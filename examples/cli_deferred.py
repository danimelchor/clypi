from clypi import Command, arg, cprint


class Main(Command):
    """
    4ward is an example of how we can reuse args across commands using Clypi.
    """

    runner: bool = arg(
        False,
        help="Whether you run",
        prompt="Do you run?",
    )
    often: int = arg(
        help="The frequency you run with in days",
        prompt="How many days a week do you run?",
        defer=True,
    )

    async def run(self):
        if not self.runner:
            cprint("You are not a runner!", fg="green", bold=True)
            cprint("Try answering yes on the next try :)", bold=True)
        else:
            cprint(
                f"You are a runner and run every {self.often} days!",
                fg="green",
                bold=True,
            )
            cprint("Try answering no on the next try :)", bold=True)


if __name__ == "__main__":
    main: Main = Main.parse()
    main.start()
