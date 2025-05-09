from typing_extensions import override

from clypi import Command, arg, cprint, get_config, style


class Main(Command):
    """An example of how enabling negative flags looks like"""

    verbose: bool = arg(
        False,
        short="v",
        help="Whether to show more output",
        prompt="Should we show more output?",
    )

    @override
    async def run(self):
        cprint(f"Verbose: {self.verbose}", fg="blue")
        print(
            style("Try using ", fg="cyan")
            + style("--no-verbose", fg="yellow", bold=True)
            + style(" or ", fg="cyan")
            + style("--help", fg="yellow", bold=True)
        )


if __name__ == "__main__":
    get_config().negative_flags = True
    main: Main = Main.parse()
    main.start()
