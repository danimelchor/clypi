import pytest
from typing_extensions import override

from clypi import Command

# A counter to check the order of events and their results
_counter: list[Exception | int] = []

# An exception we will raise and catch
_EXC: Exception = Exception("foo")


class ExampleSubCommand(Command):
    """Some sample docs"""

    should_raise: bool = False

    @override
    async def pre_run_hook(self) -> None:
        _counter.append(1)

    @override
    async def post_run_hook(self, exception: Exception | None) -> None:
        _counter.append(exception or 3)

    @override
    async def run(self):
        _counter.append(2)

        if self.should_raise:
            raise _EXC


def test_cli_hooks_run_in_order():
    global _counter
    _counter = []

    ExampleSubCommand().parse([]).start()

    # Pre-run, run, post-run no exception
    assert _counter == [1, 2, 3]


def test_cli_hooks_catch_exception():
    global _counter
    _counter = []

    with pytest.raises(Exception):
        ExampleSubCommand().parse(["--should-raise"]).start()

    # Pre-run, run, post-run with catch
    assert _counter == [1, 2, _EXC]
