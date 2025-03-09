import asyncio
import re
from pathlib import Path

import clypi
from clypi import Command, Positional, Spinner, config


async def from_requirements(file: Path):
    packages_with_versions: dict[str, str] = {}
    for line in file.read_text().split():
        package = re.search(r"(\w+)[>=<]+([0-9\.]+)", line)
        if not package:
            continue
        packages_with_versions[package.group(1)] = package.group(2)

    await _install_packages(packages_with_versions)


async def from_packages(packages: list[str]):
    packages_with_versions: dict[str, str] = {}

    clypi.print("\nAdded new packages", fg="blue", bold=True)
    for p in packages:
        package = re.search(r"(\w+)[>=<]+([0-9\.]+)", p)
        if not package:
            continue
        packages_with_versions[package.group(1)] = package.group(2)

    await _install_packages(packages_with_versions)


async def _install_packages(packages: dict[str, str]):
    async with Spinner("Installing packages", capture=True):
        for name, version in packages.items():
            print("Installed", name)
            await asyncio.sleep(0.3)

    clypi.print("\nAdded new packages", fg="blue", bold=True)
    for name, version in packages.items():
        icon = clypi.style("+", fg="green", bold=True)
        print(f"[{icon}] {name} {version}")


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
        clypi.print("Running `uv add` command...\n", fg="blue", bold=True)

        # Download from requirements.txt file
        if self.requirements:
            await from_requirements(self.requirements)

        # Download positional args
        elif self.packages:
            await from_packages(self.packages)

        else:
            raise ValueError("One of requirements or packages is required!")
