import sys

import clypi
from clypi import ClypiConfig, ClypiFormatter, Command, Styler, Theme, arg, configure
from examples.uv.add import Add
from examples.uv.init import Init
from examples.uv.pip import Pip
from examples.uv.remove import Remove


class Uv(Command):
    """
    A clone of an extremely fast Python package manager.
    """

    subcommand: Add | Init | Pip | Remove | None
    quiet: bool = arg(False, short="q", help="Do not print any output", group="global")
    version: bool = arg(False, short="V", help="Display the uv version", group="global")
    no_cache: bool = arg(
        False,
        help="Avoid reading from or writing to the cache, instead using a temporary directory for the duration of the operation",
        hidden=True,
        group="global",
    )

    async def run(self) -> None:
        # If the version was requested, print it
        if self.version:
            clypi.cprint("clypi's UV 0.0.1", fg="green")
            sys.exit(0)

        if not self.quiet:
            self.print_help()


if __name__ == "__main__":
    # Configure the CLI to look like uv's
    configure(
        ClypiConfig(
            theme=Theme(
                usage=Styler(fg="green", bold=True),
                usage_command=Styler(fg="cyan", bold=True),
                usage_args=Styler(fg="cyan"),
                section_title=Styler(fg="green", bold=True),
                subcommand=Styler(fg="cyan", bold=True),
                long_option=Styler(fg="cyan", bold=True),
                short_option=Styler(fg="cyan", bold=True),
                positional=Styler(fg="cyan"),
                placeholder=Styler(fg="cyan"),
                prompts=Styler(fg="green", bold=True),
            ),
            help_formatter=ClypiFormatter(
                boxed=False,
                show_option_types=False,
            ),
        )
    )

    # Parse and run the commands
    uv = Uv.parse()
    uv.start()
