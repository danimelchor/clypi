import asyncio
from dataclasses import dataclass
from pathlib import Path

from typing_extensions import override

from term import Command, field


@dataclass
class ExampleSubCommand(Command):
    """Some sample docs"""

    positional: tuple[str | Path, ...]

    async def run(self):
        return "subcommand"


@dataclass
class ExampleCommand(Command):
    """
    Some sample documentation for the main command
    """

    flag: bool = False
    subcommand: ExampleSubCommand | None = None
    option: list[str] = field(help="A list of strings please", default_factory=list)

    @override
    @classmethod
    def prog(cls):
        return "example"

    @override
    @classmethod
    def epilog(cls):
        return "Some text to display after..."

    async def run(self):
        return "main"


def test_expected_base():
    assert ExampleCommand.help() == "Some sample documentation for the main command"
    assert ExampleCommand.prog() == "example"
    assert ExampleCommand.epilog() == "Some text to display after..."


def test_expected_options():
    opts = ExampleCommand.options()
    assert len(opts) == 2

    assert opts["flag"].name == "flag"
    assert opts["flag"]._type is bool
    assert opts["flag"].nargs == 0

    assert opts["option"].name == "option"
    assert opts["option"]._type == list[str]
    assert opts["option"].nargs == "*"


def test_expected_positional():
    pos = ExampleSubCommand.positionals()
    assert len(pos) == 1

    assert pos["positional"].name == "positional"
    assert pos["positional"]._type == tuple[str | Path, ...]
    assert pos["positional"].nargs == "+"


def test_expected_subcommands():
    pos = ExampleCommand.subcommands()
    assert len(pos) == 1

    assert pos["example-sub-command"].name == "example-sub-command"
    assert pos["example-sub-command"]._type == ExampleSubCommand
    assert pos["example-sub-command"].help == "Some sample docs"


def test_expected_parsing():
    ec = ExampleCommand.parse(["--flag", "--option", "a", "b"])
    assert ec.flag is True
    assert ec.option == ["a", "b"]

    assert ec.subcommand is None
    assert asyncio.run(ec.astart()) == "main"


def test_expected_parsing_subcmd():
    ec = ExampleCommand.parse(
        ["--flag", "--option", "a", "b", "example-sub-command", "some_file.json"]
    )
    assert ec.flag is True
    assert ec.option == ["a", "b"]

    sc = ec.subcommand
    assert isinstance(sc, ExampleSubCommand)
    assert sc.positional == ("some_file.json",)

    assert asyncio.run(ec.astart()) == "subcommand"
