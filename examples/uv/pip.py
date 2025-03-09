import clypi
from clypi import Command


class Install(Command):
    """Install packages into an environment"""

    async def run(self) -> None:
        clypi.print("Running `uv pip install` command...", fg="blue")


class Uninstall(Command):
    """Uninstall packages from an environment"""

    async def run(self) -> None:
        clypi.print("Running `uv pip uninstall` command...", fg="blue")


class Freeze(Command):
    """List, in requirements format, packages installed in an environment"""

    async def run(self) -> None:
        clypi.print("Running `uv pip freeze` command...", fg="blue")


class List(Command):
    """List, in tabular format, packages installed in an environment"""

    async def run(self) -> None:
        clypi.print("Running `uv pip list` command...", fg="blue")


class Pip(Command):
    """Manage Python packages with a pip-compatible interface"""

    subcommand: Install | Uninstall | Freeze | List
