import typing as t

import pytest

from clypi import Command, arg
from tests.cli_parse_test import parametrize


class Run(Command):
    """
    Runs all files
    """

    verbose: bool = arg(inherited=True)
    env: str = arg(inherited=True)


class Main(Command):
    subcommand: Run | None = None
    verbose: bool = arg(False, short="v", help="Whether to show more output")
    env: t.Literal["qa", "prod"] = arg(help="Whether to show more output")


@parametrize(
    "args,expected,fails",
    [
        ([], {}, True),
        (["-v"], {}, True),
        (
            ["-v", "--env", "qa"],
            {
                "verbose": True,
                "env": "qa",
            },
            False,
        ),
        (
            ["--env", "qa", "-v", "run"],
            {
                "verbose": True,
                "env": "qa",
            },
            False,
        ),
        (
            ["--env", "qa", "run", "-v"],
            {
                "verbose": True,
                "env": "qa",
                "run": {"verbose": True, "env": "qa"},
            },
            False,
        ),
        (
            ["run", "--env", "qa", "-v"],
            {
                "verbose": True,
                "env": "qa",
                "run": {"verbose": True, "env": "qa"},
            },
            False,
        ),
        (["run", "-v"], {}, True),
    ],
)
def test_parse_inherited(args: list[str], expected: dict[str, t.Any], fails: bool):
    if fails:
        with pytest.raises(Exception):
            _ = Main.parse(args)
        return

    # Check command
    main = Main.parse(args)
    assert main is not None
    for k, v in expected.items():
        if k == "run":
            continue
        lc_v = getattr(main, k)
        assert lc_v == v, f"{k} should be {v} but got {lc_v}"

    # Check subcommand
    if "run" in expected:
        assert main.subcommand is not None
        assert isinstance(main.subcommand, Run)
        for k, v in expected["run"].items():
            lc_v = getattr(main, k)
            assert lc_v == v, f"run.{k} should be {v} but got {lc_v}"
