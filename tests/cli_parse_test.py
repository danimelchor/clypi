import shlex
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from clypi import Command, config


class ExampleSub(Command):
    pos2: tuple[str | Path, ...]
    flag2: bool = False
    option2: int = 5

    async def run(self):
        print("subcommand")


class Example(Command):
    pos: Path
    flag: bool = config(default=False, short="f")
    subcommand: ExampleSub | None = None
    option: list[str] = config(default_factory=list, short="o")

    async def run(self):
        print("main")


def ids(cases: list[tuple]):
    return list(map(lambda x: shlex.join(x[0]), cases))


COMMAND = [
    (["./some-path"], {"flag": False, "pos": Path("./some-path"), "option": []}),
    (
        ["--flag", "./some-path"],
        {"flag": True, "pos": Path("./some-path"), "option": []},
    ),
    (
        ["./some-path", "--flag"],
        {"flag": True, "pos": Path("./some-path"), "option": []},
    ),
    (
        ["-f", "./some-path"],
        {"flag": True, "pos": Path("./some-path"), "option": []},
    ),
    (
        ["./some-path", "--option", "a"],
        {"flag": False, "pos": Path("./some-path"), "option": ["a"]},
    ),
    (
        ["./some-path", "-o", "a"],
        {"flag": False, "pos": Path("./some-path"), "option": ["a"]},
    ),
    (
        ["./some-path", "--flag", "--option", "a"],
        {"flag": True, "pos": Path("./some-path"), "option": ["a"]},
    ),
    (
        ["./some-path", "--option", "a", "--flag"],
        {"flag": True, "pos": Path("./some-path"), "option": ["a"]},
    ),
    (
        ["./some-path", "--flag", "--option", "a", "b"],
        {"flag": True, "pos": Path("./some-path"), "option": ["a", "b"]},
    ),
    (
        ["./some-path", "--option", "a", "b", "--flag"],
        {"flag": True, "pos": Path("./some-path"), "option": ["a", "b"]},
    ),
    (
        ["./some-path", "-o", "a", "b", "-f"],
        {"flag": True, "pos": Path("./some-path"), "option": ["a", "b"]},
    ),
]


@pytest.mark.parametrize("args,expected", COMMAND, ids=ids(COMMAND))
@patch("os.get_terminal_size")
def test_expected_parsing_no_subcommand(gts, args, expected):
    gts.return_value = MagicMock()
    gts.return_value.columns = 80

    ec = Example.parse(args)
    for k, v in expected.items():
        assert getattr(ec, k) == v


SUBCMD = [
    (
        ["example-sub", "foo"],
        {
            "pos2": ("foo",),
            "flag2": False,
            "option2": 5,
        },
    ),
    (
        ["example-sub", "foo", "bar"],
        {
            "pos2": ("foo", "bar"),
            "flag2": False,
            "option2": 5,
        },
    ),
    (
        ["example-sub", "foo", "bar", "--flag2"],
        {
            "pos2": ("foo", "bar"),
            "flag2": True,
            "option2": 5,
        },
    ),
    (
        ["example-sub", "--flag2", "foo", "bar"],
        {
            "pos2": ("foo", "bar"),
            "flag2": True,
            "option2": 5,
        },
    ),
    (
        ["example-sub", "foo", "bar", "--option2", "6"],
        {
            "pos2": ("foo", "bar"),
            "flag2": False,
            "option2": 6,
        },
    ),
    (
        ["example-sub", "--option2", "6", "foo", "bar"],
        {
            "pos2": ("foo", "bar"),
            "flag2": False,
            "option2": 6,
        },
    ),
    (
        ["example-sub", "--option2", "6", "foo", "bar", "--flag2"],
        {
            "pos2": ("foo", "bar"),
            "flag2": True,
            "option2": 6,
        },
    ),
    (
        ["example-sub", "--flag2", "--option2", "6", "foo", "bar"],
        {
            "pos2": ("foo", "bar"),
            "flag2": True,
            "option2": 6,
        },
    ),
    (
        ["example-sub", "--flag2", "foo", "bar", "--option2", "6"],
        {
            "pos2": ("foo", "bar"),
            "flag2": True,
            "option2": 6,
        },
    ),
]

# Test every COMMAND scenario with every SUBCMD scenario
MERGED = [
    (
        [*cmd_args, *subcmd_args],
        cmd_expected,
        subcmd_expected,
    )
    for subcmd_args, subcmd_expected in SUBCMD
    for cmd_args, cmd_expected in COMMAND
]


@pytest.mark.parametrize("args,cmd_expected,subcmd_expected", MERGED, ids=ids(MERGED))
@patch("os.get_terminal_size")
def test_expected_parsing_subcommand(gts, args, cmd_expected, subcmd_expected):
    gts.return_value = MagicMock()
    gts.return_value.columns = 80

    ec = Example.parse(args)
    for k, v in cmd_expected.items():
        assert getattr(ec, k) == v

    sc = ec.subcommand
    assert sc is not None
    for k, v in subcmd_expected.items():
        assert getattr(sc, k) == v
