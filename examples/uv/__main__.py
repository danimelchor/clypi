import sys

import clypi
from clypi import Command, config
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
    uv = Uv.parse()
    uv.start()
