import os
import typing as t

from clypi import Command, arg

SOME_ENV_VAR = "SOME_ENV_VAR"
SOME_ENV_VAR2 = "SOME_ENV_VAR2"


class Main(Command):
    foo: float | None = arg(None, env=SOME_ENV_VAR)
    bar: list[int] = arg(env=SOME_ENV_VAR2)


def test_env_var_works(monkeypatch: t.Any):
    monkeypatch.setenv(SOME_ENV_VAR, "-0.1")
    monkeypatch.setenv(SOME_ENV_VAR2, "1,2,3")

    # Just to make sure
    assert os.getenv(SOME_ENV_VAR) == "-0.1"
    assert os.getenv(SOME_ENV_VAR2) == "1,2,3"

    cmd = Main.parse([])
    assert cmd.foo == -0.1
    assert cmd.bar == [1, 2, 3]
