from typing_extensions import override

from clypi import Command, arg, cprint, style


class Main(Command):
    """An example of how enabling negative flags looks like"""

    verbose: bool = arg(
        True,
        short="v",
        negative="quiet",
        help="Whether to show more output",
    )

    @override
    async def run(self):
        cprint(f"Verbose: {self.verbose}", fg="blue")
        print(
            style("Try using ", fg="cyan")
            + style("--quiet", fg="yellow", bold=True)
            + style(" or ", fg="cyan")
            + style("--help", fg="yellow", bold=True)
        )


if __name__ == "__main__":
    main: Main = Main.parse()
    main.start()
