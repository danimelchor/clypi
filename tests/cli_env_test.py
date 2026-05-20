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


def test_flag_overrides_env_var(monkeypatch: t.Any):
    monkeypatch.setenv(SOME_ENV_VAR, "-0.1")
    monkeypatch.setenv(SOME_ENV_VAR2, "1,2,3")

    cmd = Main.parse(["--foo=0.5", "--bar", "4", "5"])
    assert cmd.foo == 0.5
    assert cmd.bar == [4, 5]


class InheritedRun(Command):
    foo: float | None = arg(inherited=True)


class InheritedMain(Command):
    subcommand: InheritedRun
    foo: float | None = arg(None, env=SOME_ENV_VAR)


def test_flag_overrides_env_var_through_inherited_subcommand(monkeypatch: t.Any):
    monkeypatch.setenv(SOME_ENV_VAR, "-0.1")

    cmd = InheritedMain.parse(["--foo=0.5", "inherited-run"])
    assert cmd.foo == 0.5
    assert cmd.subcommand.foo == 0.5


def test_env_var_used_when_flag_omitted_through_inherited_subcommand(
    monkeypatch: t.Any,
):
    monkeypatch.setenv(SOME_ENV_VAR, "-0.1")

    cmd = InheritedMain.parse(["inherited-run"])
    assert cmd.foo == -0.1
    assert cmd.subcommand.foo == -0.1
