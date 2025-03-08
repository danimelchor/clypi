from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from clypi import Command, config


class ExampleSub(Command):
    pos2: tuple[str | Path, ...]
    flag2: bool = False
    option2: list[str] = config(default_factory=list)

    async def run(self):
        print("subcommand")


class Example(Command):
    pos: Path
    flag: bool = config(default=False, short="f")
    subcommand: ExampleSub | None = None
    option: list[str] = config(default_factory=list, short="o")

    async def run(self):
        print("main")


@pytest.mark.parametrize(
    "args,expected",
    [
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
    ],
)
@patch("os.get_terminal_size")
def test_expected_parsing_no_subcommand(gts, args, expected):
    gts.return_value = MagicMock()
    gts.return_value.columns = 80

    ec = Example.parse(args)
    for k, v in expected.items():
        assert getattr(ec, k) == v
