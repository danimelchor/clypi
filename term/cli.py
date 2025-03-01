import logging
from dataclasses import dataclass, field
from typing import Literal

from term._cli.main import Command


@dataclass
class Run(Command):
    files: list[str]
    quiet: bool
    format: Literal["json", "pretty"] = "pretty"


@dataclass
class Lint(Command):
    quiet: bool
    no_cache: bool
    index: str
    files: list[str] = field(default_factory=list)


@dataclass
class Main(Command):
    subcommand: Run | Lint
    verbose: bool


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main = Main.parse()
    print(main)
