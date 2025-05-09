from typing_extensions import override

from clypi import Command, arg, cprint, get_config


class Main(Command):
    verbose: bool = arg(
        False,
        short="v",
        help="Whether to show more output",
        prompt="Should we show more output?",
    )

    @override
    async def run(self):
        cprint(f"Verbose: {self.verbose}", fg="blue")
        cprint("Try using --no-verbose or --help", fg="cyan")


if __name__ == "__main__":
    get_config().negative_flags = True
    main: Main = Main.parse()
    main.start()
