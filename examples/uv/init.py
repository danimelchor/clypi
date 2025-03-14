from pathlib import Path

import clypi
from clypi import Command, Positional, arg


class Init(Command):
    """Create a new project"""

    path: Positional[Path] = arg(help="The path to use for the project/script")
    name: str = arg(
        help="The name of the project",
        prompt="What's the name of your project/script?",
    )
    description: str = arg(
        help="Set the project description",
        prompt="What's your project/script's description?",
    )

    async def run(self) -> None:
        clypi.cprint("Running `uv init` command...", fg="blue")
