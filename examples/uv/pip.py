import clypi
from clypi import Command, arg


class Install(Command):
    """Install packages into an environment"""

    # Inherited opts
    quiet: bool = arg(inherited=True)
    version: bool = arg(inherited=True)
    no_cache: bool = arg(inherited=True)

    async def run(self) -> None:
        clypi.cprint("Running `uv pip install` command...", fg="blue")


class Uninstall(Command):
    """Uninstall packages from an environment"""

    # Inherited opts
    quiet: bool = arg(inherited=True)
    version: bool = arg(inherited=True)
    no_cache: bool = arg(inherited=True)

    async def run(self) -> None:
        clypi.cprint("Running `uv pip uninstall` command...", fg="blue")


class Freeze(Command):
    """List, in requirements format, packages installed in an environment"""

    # Inherited opts
    quiet: bool = arg(inherited=True)
    version: bool = arg(inherited=True)
    no_cache: bool = arg(inherited=True)

    async def run(self) -> None:
        clypi.cprint("Running `uv pip freeze` command...", fg="blue")


class List(Command):
    """List, in tabular format, packages installed in an environment"""

    # Inherited opts
    quiet: bool = arg(inherited=True)
    version: bool = arg(inherited=True)
    no_cache: bool = arg(inherited=True)

    async def run(self) -> None:
        clypi.cprint("Running `uv pip list` command...", fg="blue")


class Pip(Command):
    """Manage Python packages with a pip-compatible interface"""

    subcommand: Install | Uninstall | Freeze | List

    # Inherited opts
    quiet: bool = arg(inherited=True)
    version: bool = arg(inherited=True)
    no_cache: bool = arg(inherited=True)
