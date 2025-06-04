import typing as t
from dataclasses import dataclass

import pytest

from clypi import Command, Positional, arg
from tests.cli_parse_test import parametrize
from tests.prompt_test import replace_stdin


@dataclass
class CustomType:
    foo: str = "bar"


def parse_custom(raw: str | list[str]) -> CustomType:
    return CustomType(foo=str(raw))


class Run(Command):
    """
    Runs all files
    """

    pos: Positional[str] = arg(inherited=True)
    verbose: bool = arg(inherited=True)
    env: str = arg(inherited=True)
    env_prompt: str = arg(inherited=True)
    custom: CustomType = arg(inherited=True)


class Main(Command):
    subcommand: Run | None = None
    pos: Positional[int] = arg(help="Some positional arg")
    verbose: bool = arg(False, short="v", help="Whether to show more output")
    env: t.Literal["qa", "prod"] = arg(help="The environment to use")
    env_prompt: t.Literal["qa", "prod"] = arg(
        help="The environment to use",
        prompt="What environment should we use?",
    )
    custom: CustomType = arg(default=CustomType(), parser=parse_custom)


@parametrize(
    "args,expected,fails,stdin",
    [
        ([], {}, True, ""),
        (["-v"], {}, True, ""),
        (["-v", "--env", "qa"], {}, True, ""),
        (["-v", "--env", "qa", "--env-prompt", "qa"], {}, True, ""),
        (
            ["1", "-v", "--env", "qa"],
            {
                "pos": 1,
                "verbose": True,
                "env": "qa",
                "env_prompt": "qa",
            },
            False,
            "qa\n",
        ),
        (
            ["1", "-v", "--env", "qa", "--env-prompt", "qa"],
            {
                "pos": 1,
                "verbose": True,
                "env": "qa",
                "env_prompt": "qa",
            },
            False,
            "",
        ),
        (
            ["1", "--env", "qa", "-v", "run"],
            {
                "pos": 1,
                "verbose": True,
                "env": "qa",
                "env_prompt": "qa",
                "run": {
                    "pos": 1,
                    "verbose": True,
                    "env": "qa",
                    "env_prompt": "qa",
                },
            },
            False,
            "qa\n",
        ),
        (
            ["1", "--custom", "baz", "run", "--env", "qa", "-v"],
            {
                "pos": 1,
                "verbose": True,
                "env": "qa",
                "env_prompt": "qa",
                "run": {
                    "pos": 1,
                    "verbose": True,
                    "env": "qa",
                    "env_prompt": "qa",
                    "custom": CustomType("baz"),
                },
                "custom": CustomType("baz"),
            },
            False,
            "qa\n",
        ),
        (
            ["--env", "qa", "run", "1", "-v", "--env-prompt", "qa"],
            {
                "pos": 1,
                "verbose": True,
                "env": "qa",
                "env_prompt": "qa",
                "run": {
                    "pos": 1,
                    "verbose": True,
                    "env": "qa",
                    "env_prompt": "qa",
                },
            },
            False,
            "",
        ),
        (
            ["--env", "qa", "--env-prompt", "qa", "run", "1", "-v"],
            {
                "pos": 1,
                "verbose": True,
                "env": "qa",
                "env_prompt": "qa",
                "run": {
                    "pos": 1,
                    "verbose": True,
                    "env": "qa",
                    "env_prompt": "qa",
                },
            },
            False,
            "",
        ),
        (
            ["--env", "qa", "run", "1", "-v"],
            {
                "pos": 1,
                "verbose": True,
                "env": "qa",
                "env_prompt": "qa",
                "run": {
                    "pos": 1,
                    "verbose": True,
                    "env": "qa",
                    "env_prompt": "qa",
                },
            },
            False,
            "qa\n",
        ),
        (
            ["run", "--env", "qa", "-v", "1"],
            {
                "pos": 1,
                "verbose": True,
                "env": "qa",
                "env_prompt": "qa",
                "run": {
                    "pos": 1,
                    "verbose": True,
                    "env": "qa",
                    "env_prompt": "qa",
                },
            },
            False,
            "qa\n",
        ),
        (["run", "-v"], {}, True, ""),
        (
            ["run", "--env", "qa", "-v", "1", "--custom", "baz"],
            {
                "pos": 1,
                "verbose": True,
                "env": "qa",
                "env_prompt": "qa",
                "run": {
                    "pos": 1,
                    "verbose": True,
                    "env": "qa",
                    "env_prompt": "qa",
                    "custom": CustomType("baz"),
                },
                "custom": CustomType("baz"),
            },
            False,
            "qa\n",
        ),
    ],
)
def test_parse_inherited(
    args: list[str],
    expected: dict[str, t.Any],
    fails: bool,
    stdin: str | list[str],
):
    if fails:
        with pytest.raises(BaseException):
            _ = Main.parse(args)
        return

    # Check command
    with replace_stdin(stdin):
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


def test_inherited_fails_on_load():
    class Subcmd(Command):
        pos: Positional[str] = arg(inherited=True)
        verbose: bool = arg(inherited=True)

    with pytest.raises(TypeError) as exc_info:

        class Main(Command):
            subcommand: Subcmd | None = None

    assert (
        str(exc_info.value)
        == "Fields ['verbose', 'pos'] in Subcmd cannot be inherited from Main since they don't exist!"
    )
