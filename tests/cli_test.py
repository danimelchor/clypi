from pathlib import Path

from typing_extensions import override

from clypi import Command, Positional, arg


class ExampleSubCommand(Command):
    """Some sample docs"""

    positional: Positional[tuple[str | Path, ...]]

    async def run(self):
        print("subcommand")


class ExampleCommand(Command):
    """
    Some sample documentation for the main command
    """

    flag: bool = False
    subcommand: ExampleSubCommand | None = None
    option: list[str] = arg(help="A list of strings please", default_factory=list)

    @override
    @classmethod
    def prog(cls):
        return "example"

    @override
    @classmethod
    def epilog(cls):
        return "Some text to display after..."

    async def run(self):
        print("main")


def test_expected_base():
    assert ExampleCommand.help() == "Some sample documentation for the main command"
    assert ExampleCommand.prog() == "example"
    assert ExampleCommand.epilog() == "Some text to display after..."


def test_expected_options():
    opts = ExampleCommand.options()
    assert len(opts) == 2

    assert opts["flag"].name == "flag"
    assert opts["flag"].arg_type is bool
    assert opts["flag"].nargs == 0

    assert opts["option"].name == "option"
    assert opts["option"].arg_type == list[str]
    assert opts["option"].nargs == "*"


def test_expected_positional():
    pos = ExampleSubCommand.positionals()
    assert len(pos) == 1

    assert pos["positional"].name == "positional"
    assert pos["positional"].arg_type == Positional[tuple[str | Path, ...]]
    assert pos["positional"].nargs == "+"


def test_expected_subcommands():
    pos = ExampleCommand.subcommands()
    assert len(pos) == 2

    assert pos[None] is None

    sub = pos["example-sub-command"]
    assert sub is ExampleSubCommand
    assert sub.prog() == "example-sub-command"
    assert sub.help() == "Some sample docs"


def test_expected_cls_introspection():
    assert ExampleCommand.option == []
