import asyncio
import re
from pathlib import Path

import clypi
from clypi import ClypiException, Command, Positional, Spinner, arg


async def from_requirements(file: Path):
    """
    Given a file, it will load it, try to parse the packages and versions
    with regex, and "install" them.
    """

    packages_with_versions: dict[str, str] = {}
    for line in file.read_text().split():
        package = re.search(r"(\w+)[>=<]+([0-9\.]+)", line)
        if not package:
            continue
        packages_with_versions[package.group(1)] = package.group(2)

    await _install_packages(packages_with_versions)


async def from_packages(packages: list[str]):
    """
    Given a list of packages, it will try to parse the packages and versions
    with regex, and "install" them.
    """

    packages_with_versions: dict[str, str] = {}

    clypi.cprint("\nAdded new packages", fg="blue", bold=True)
    for p in packages:
        package = re.search(r"(\w+)[>=<]+([0-9\.]+)", p)
        if not package:
            continue
        packages_with_versions[package.group(1)] = package.group(2)

    await _install_packages(packages_with_versions)


async def _install_packages(packages: dict[str, str]):
    """
    Mock install the packages with a nice colored spinner.
    """

    async with Spinner("Installing packages", capture=True):
        for name, version in packages.items():
            print("Installed", name)
            await asyncio.sleep(0.3)

    clypi.cprint("\nAdded new packages", fg="blue", bold=True)
    for name, version in packages.items():
        icon = clypi.style("+", fg="green", bold=True)
        print(f"[{icon}] {name} {version}")


class Add(Command):
    """Add dependencies to the project"""

    packages: Positional[list[str]] = arg(
        default_factory=list,
        help="The packages to add, as PEP 508 requirements (e.g., `ruff==0.5.0`)",
    )
    requirements: Path | None = arg(
        None,
        short="r",
        help="Add all packages listed in the given `requirements.txt` files",
    )
    dev: bool = arg(
        False, help="Add the requirements to the development dependency group"
    )

    # Inherited opts
    quiet: bool = arg(inherited=True)
    version: bool = arg(inherited=True)
    no_cache: bool = arg(inherited=True)

    async def run(self) -> None:
        clypi.cprint("Running `uv add` command...\n", fg="blue", bold=True)

        # Download from requirements.txt file
        if self.requirements:
            await from_requirements(self.requirements)

        # Download positional args
        elif self.packages:
            await from_packages(self.packages)

        else:
            raise ClypiException("One of requirements or packages is required!")
