from pathlib import Path

import clypi
from clypi import Command, Positional, config


class Init(Command):
    """Create a new project"""

    path: Positional[Path] = config(help="The path to use for the project/script")
    name: str = config(
        help="The name of the project",
        prompt="What's the name of your project/script?",
    )
    description: str = config(
        help="Set the project description",
        prompt="What's your project/script's description?",
    )

    async def run(self) -> None:
        clypi.print("Running `uv init` command...", fg="blue")
