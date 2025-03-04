import typing as t
from pathlib import Path

from clypi import Command, config


class MySub(Command):
    foo: int = 1


class MyCommand(Command):
    subcommand: MySub
    foo: bool
    bar: str = config(help="help!")
    baz: Path = config(default=Path.cwd())
    qux: list[str] = config(default_factory=list)


cli = MyCommand.parse()

t.assert_type(cli, MyCommand)
t.assert_type(cli.foo, bool)
t.assert_type(cli.bar, str)
t.assert_type(cli.baz, Path)
t.assert_type(cli.qux, list[str])

t.assert_type(cli.subcommand, MySub)
t.assert_type(cli.subcommand.foo, int)

t.assert_type(config(default=None), None)
t.assert_type(config(default=5), int)
t.assert_type(config(default_factory=int), int)


def parser(x: t.Any) -> int | list[str]:
    if x == 1:
        return x
    return ["a"]


t.assert_type(config(parser=parser), int | list[str])
