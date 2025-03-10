import sys

import clypi
from clypi import ClypiConfig, ClypiFormatter, Command, Styler, Theme, config, configure
from examples.uv.add import Add
from examples.uv.init import Init
from examples.uv.pip import Pip
from examples.uv.remove import Remove


class Uv(Command):
    """
    A clone of an extremely fast Python package manager.
    """

    subcommand: Add | Init | Pip | Remove | None
    quiet: bool = config(default=False, short="q", help="Do not print any output")
    version: bool = config(default=False, short="V", help="Display the uv version")

    async def run(self) -> None:
        if self.version:
            clypi.print("clypi's UV 0.0.1", fg="green")
            sys.exit(0)

        if not self.quiet:
            self.print_help()


if __name__ == "__main__":
    configure(
        ClypiConfig(
            theme=Theme(
                usage=Styler(fg="green", bold=True),
                prog=Styler(fg="cyan", bold=True),
                section_title=Styler(fg="green", bold=True),
                subcommand=Styler(fg="cyan"),
                long_option=Styler(fg="cyan"),
                short_option=Styler(fg="cyan"),
                positional=Styler(fg="cyan"),
                type_str=Styler(fg="cyan"),
                prompts=Styler(fg="green", bold=True),
            ),
            help_formatter=ClypiFormatter(boxed=False),
        )
    )

    uv = Uv.parse()
    uv.start()
