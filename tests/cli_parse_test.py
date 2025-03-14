import shlex
import typing as t
from enum import Enum
from pathlib import Path

import pytest
from typing_extensions import override

from clypi import Command, Positional, arg
from clypi._configuration import get_config


def parametrize(args: str, cases: list[tuple[t.Any, ...]]):
    def wrapper(fn: t.Callable[..., t.Any]):
        return pytest.mark.parametrize(args, cases, ids=ids(cases))(fn)

    return wrapper


get_config().help_on_fail = False


class ExampleSub(Command):
    pos2: Positional[tuple[str | Path, ...]]
    flag2: bool = False
    option2: int = 5

    @override
    async def run(self):
        print("subcommand")


class Example(Command):
    pos: Positional[Path]
    flag: bool = arg(False, short="f")
    subcommand: ExampleSub | None = None
    option: list[str] = arg(default_factory=list, short="o")

    @override
    async def run(self):
        print("main")


def ids(cases: list[tuple[t.Any]]):
    return list(map(lambda x: shlex.join(x[0]), cases))


COMMAND: list[tuple[t.Any, ...]] = [
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


@parametrize("args,expected", COMMAND)
def test_expected_parsing_no_subcommand(args: list[str], expected: dict[str, t.Any]):
    ec = Example.parse(args)
    for k, v in expected.items():
        assert getattr(ec, k) == v


SUBCMD: list[tuple[t.Any, ...]] = [
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


@parametrize("args,cmd_expected,subcmd_expected", MERGED)
def test_expected_parsing_subcommand(
    args: list[str], cmd_expected: dict[str, t.Any], subcmd_expected: dict[str, t.Any]
):
    ec = Example.parse(args)
    for k, v in cmd_expected.items():
        assert getattr(ec, k) == v

    sc = ec.subcommand
    assert sc is not None
    assert sc.parents() == ["example"]
    assert sc.full_command() == ["example", "example-sub"]
    for k, v in subcmd_expected.items():
        assert getattr(sc, k) == v


@parametrize(
    "args,expected,fails",
    [
        ([], {}, True),
        (["foo"], {}, True),
        (
            ["foo", "--opt", "bar"],
            {"pos": ["foo"], "opt": ["bar"], "opt2": []},
            False,
        ),
        (
            ["foo", "--opt", "bar", "--opt2", "baz"],
            {"pos": ["foo"], "opt": ["bar"], "opt2": ["baz"]},
            False,
        ),
        (
            [
                *(["foo"] * 10),
                "--opt",
                *(["bar"] * 10),
                "--opt2",
                *(["baz"] * 10),
            ],
            {"pos": ["foo"] * 10, "opt": ["bar"] * 10, "opt2": ["baz"] * 10},
            False,
        ),
    ],
)
def test_parse_lists(args: list[str], expected: dict[str, t.Any], fails: bool):
    class ListCommand(Command):
        pos: Positional[list[str]]
        opt: list[str]
        opt2: list[str] = arg(default_factory=list)

    if fails:
        with pytest.raises(Exception):
            _ = ListCommand.parse(args)
        return

    lc = ListCommand.parse(args)
    assert lc is not None
    for k, v in expected.items():
        lc_v = getattr(lc, k)
        assert lc_v == v
        assert isinstance(lc_v, list)


@parametrize(
    "args,expected,fails",
    [
        ([], {}, True),
        (["foo"], {}, True),
        (["foo", "--opt", "bar"], {}, True),
        (
            ["foo", "--opt", "bar", "baz"],
            {"pos": ("foo",), "opt": ("bar", "baz"), "opt2": tuple()},
            False,
        ),
        (
            ["foo", "--opt", "bar", "baz", "--opt2", "qux"],
            {"pos": ("foo",), "opt": ("bar", "baz"), "opt2": ("qux",)},
            False,
        ),
        ([*(["foo"] * 2), "--opt", "bar", "--opt2", "qux"], {}, True),
        (["foo", "--opt", *(["bar"] * 3), "--opt2", "qux"], {}, True),
        (["foo", "--opt", *(["bar"] * 2), "--opt2", *(["qux"] * 10)], {}, False),
    ],
)
def test_parse_tuples(args: list[str], expected: dict[str, t.Any], fails: bool):
    class TupleCommand(Command):
        pos: Positional[tuple[str]]
        opt: tuple[str, str]
        opt2: tuple[str, ...] = arg(default_factory=tuple)

    if fails:
        with pytest.raises(Exception):
            _ = TupleCommand.parse(args)
        return

    lc = TupleCommand.parse(args)
    assert lc is not None
    for k, v in expected.items():
        lc_v = getattr(lc, k)
        assert lc_v == v
        assert isinstance(lc_v, tuple)


class Env(Enum):
    QA = 1
    PROD = 2


@parametrize(
    "args,expected,fails",
    [
        ([], {}, True),
        (["foo"], {}, True),
        (["qa"], {}, True),
        (["qa", "--env2", "bar"], {}, True),
        (["qa", "--env2", "prod", "--env3", "foo"], {}, True),
        (
            ["qa", "--env2", "prod"],
            {"env": Env.QA, "env2": Env.PROD, "env3": Env.PROD},
            False,
        ),
        (
            ["prod", "--env2", "qa", "--env3", "prod"],
            {"env": Env.PROD, "env2": Env.QA, "env3": Env.PROD},
            False,
        ),
    ],
)
def test_parse_enums(args: list[str], expected: dict[str, t.Any], fails: bool):
    class EnumCommand(Command):
        env: Positional[Env]
        env2: Env
        env3: Env = Env.PROD

    if fails:
        with pytest.raises(Exception):
            _ = EnumCommand.parse(args)
        return

    ec = EnumCommand.parse(args)
    assert ec is not None
    for k, v in expected.items():
        lc_v = getattr(ec, k)
        assert lc_v == v
        assert isinstance(lc_v, Env)
