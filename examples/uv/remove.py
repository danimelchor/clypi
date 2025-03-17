import clypi
from clypi import Command, Positional, arg


class Remove(Command):
    """Remove dependencies from the project"""

    packages: Positional[list[str]] = arg(
        help="The names of the dependencies to remove (e.g., `ruff`)"
    )
    dev: bool = arg(
        False, help="Remove the packages from the development dependency group"
    )

    # Inherited opts
    quiet: bool = arg(inherited=True)
    version: bool = arg(inherited=True)
    no_cache: bool = arg(inherited=True)

    async def run(self) -> None:
        clypi.cprint("Running `uv remove` command...", fg="blue")

        # Remove the packages passed as args
        clypi.cprint("\nRemoved packages", fg="blue", bold=True)
        for p in self.packages:
            icon = clypi.style("-", fg="red", bold=True)
            print(f"[{icon}] {p} 0.1.0")
