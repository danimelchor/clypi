import typing as t

import pytest

from clypi import Command, arg
from tests.cli_parse_test import parametrize
from tests.prompt_test import replace_stdin


class Run(Command):
    """
    Runs all files
    """

    verbose: bool = arg(inherited=True)
    env: str = arg(inherited=True)
    env_prompt: str = arg(inherited=True)


class Main(Command):
    subcommand: Run | None = None
    verbose: bool = arg(False, short="v", help="Whether to show more output")
    env: t.Literal["qa", "prod"] = arg(help="The environment to use")
    env_prompt: t.Literal["qa", "prod"] = arg(
        help="The environment to use",
        prompt="What environment should we use?",
    )


@parametrize(
    "args,expected,fails,stdin",
    [
        ([], {}, True, ""),
        (["-v"], {}, True, ""),
        (["-v", "--env", "qa"], {}, True, ""),
        (
            ["-v", "--env", "qa"],
            {
                "verbose": True,
                "env": "qa",
                "env_prompt": "qa",
            },
            False,
            "qa\n",
        ),
        (
            ["-v", "--env", "qa", "--env-prompt", "qa"],
            {
                "verbose": True,
                "env": "qa",
                "env_prompt": "qa",
            },
            False,
            "",
        ),
        (
            ["--env", "qa", "-v", "run"],
            {
                "verbose": True,
                "env": "qa",
                "env_prompt": "qa",
                "run": {
                    "verbose": True,
                    "env": "qa",
                    "env_prompt": "qa",
                },
            },
            False,
            "qa\n",
        ),
        (
            ["--env", "qa", "run", "-v", "--env-prompt", "qa"],
            {
                "verbose": True,
                "env": "qa",
                "env_prompt": "qa",
                "run": {
                    "verbose": True,
                    "env": "qa",
                    "env_prompt": "qa",
                },
            },
            False,
            "",
        ),
        (
            ["--env", "qa", "--env-prompt", "qa", "run", "-v"],
            {
                "verbose": True,
                "env": "qa",
                "env_prompt": "qa",
                "run": {
                    "verbose": True,
                    "env": "qa",
                    "env_prompt": "qa",
                },
            },
            False,
            "",
        ),
        (
            ["--env", "qa", "run", "-v"],
            {
                "verbose": True,
                "env": "qa",
                "env_prompt": "qa",
                "run": {
                    "verbose": True,
                    "env": "qa",
                    "env_prompt": "qa",
                },
            },
            False,
            "qa\n",
        ),
        (
            ["run", "--env", "qa", "-v"],
            {
                "verbose": True,
                "env": "qa",
                "env_prompt": "qa",
                "run": {
                    "verbose": True,
                    "env": "qa",
                    "env_prompt": "qa",
                },
            },
            False,
            "qa\n",
        ),
        (["run", "-v"], {}, True, ""),
    ],
)
def test_parse_inherited(
    args: list[str],
    expected: dict[str, t.Any],
    fails: bool,
    stdin: str | list[str],
):
    if fails:
        with pytest.raises(Exception):
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
