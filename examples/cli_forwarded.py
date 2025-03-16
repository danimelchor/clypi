import os
import shlex
import sys
import typing as t

from typing_extensions import override

from clypi import ClypiFormatter, Command, Positional, arg, cprint, get_config, style


class Run(Command):
    """
    Runs all files
    """

    files: Positional[list[str]] = arg(help="The files to run")
    verbose: bool = arg(..., group="global")
    env: str = arg(..., group="global")

    async def run(self):
        cprint("Running with:", fg="blue", bold=True)
        cprint(f" - Files: {self.files}", fg="blue")
        cprint(f" - Verbose: {self.verbose}", fg="blue")
        cprint(f" - Env: {self.env}", fg="blue")
        cprint("Done!", fg="green", bold=True)


class Main(Command):
    """
    4ward is an example of how we can reuse args across commands using Clypi.
    """

    subcommand: Run | None = None
    verbose: bool = arg(False, short="v", help="Whether to show more output")
    env: t.Literal["qa", "prod"] = arg(help="Whether to show more output")

    @override
    @classmethod
    def prog(cls):
        return "4ward"

    @override
    @classmethod
    def epilog(cls):
        return "Learn more at http://4ward.org"

    async def run(self):
        cprint("Running with:", fg="blue", bold=True)
        cprint(f" - Verbose: {self.verbose}", fg="blue")
        cprint(f" - Env: {self.env}", fg="blue")
        cprint("Done!", fg="green", bold=True)


if __name__ == "__main__":
    show_forwarded = True
    if os.getenv("SHOW_FORWARDED") != "1":
        cprint(
            "Not showing forwarded args. Try using: "
            + style(
                "SHOW_FORWARDED=1 uv run -m examples.cli_forwarded "
                + shlex.join(sys.argv[1:]),
                bold=True,
            )
            + "\n\n",
            fg="yellow",
        )
        show_forwarded = False

    get_config().help_formatter = ClypiFormatter(show_forwarded_options=show_forwarded)

    main: Main = Main.parse()
    main.start()
