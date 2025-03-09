import re
from pathlib import Path

import clypi
from clypi import Command, Positional, config


class Add(Command):
    """Add dependencies to the project"""

    packages: Positional[list[str]] = config(
        default_factory=list,
        help="The packages to add, as PEP 508 requirements (e.g., `ruff==0.5.0`)",
    )
    requirements: Path | None = config(
        default=None,
        short="r",
        help="Add all packages listed in the given `requirements.txt` files",
    )
    dev: bool = config(
        default=False, help="Add the requirements to the development dependency group"
    )

    async def run(self) -> None:
        clypi.print("Running `uv add` command...", fg="blue", bold=True)

        # Download from requirements.txt file
        if self.requirements:
            clypi.print(
                f"\nAdded new packages from {self.requirements}", fg="blue", bold=True
            )
            for line in self.requirements.read_text().split():
                package = re.search(r"(\w+)[>=<]+([0-9\.]+)", line)
                if package:
                    icon = clypi.style("+", fg="green", bold=True)
                    print(f"[{icon}] {package.group(1)} {package.group(2)}")

        # Download positional args
        elif self.packages:
            clypi.print("\nAdded new packages", fg="blue", bold=True)
            for p in self.packages:
                icon = clypi.style("+", fg="green", bold=True)
                print(f"[{icon}] {p} 1.0.0")

            clypi.print("\nRemoved old packages", fg="blue", bold=True)
            for p in self.packages:
                icon = clypi.style("-", fg="red", bold=True)
                print(f"[{icon}] {p} 0.9.0")

        else:
            raise ValueError("One of requirements or packages is required!")
