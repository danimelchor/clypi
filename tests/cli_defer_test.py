from clypi import Command, arg
from clypi.parsers import Str
from tests.prompt_test import replace_stdin


class DeferredError(Exception):
    pass


class Signal:
    called: bool = False

    def __bool__(self):
        return self.called


class SignalParser(Str):
    """Utility parser that just raises to test when it is evaluated"""

    def __init__(self, signal: Signal) -> None:
        self._signal = signal

    def __call__(self, raw: str | list[str], /) -> str:
        self._signal.called = True
        return super().__call__(raw)


def test_never_evaluates():
    called = Signal()

    class Main(Command):
        verbose: bool = False
        some_arg: str = arg(
            prompt="What's the value?",
            defer=True,
            parser=SignalParser(called),
        )

    cmd = Main.parse([])
    assert cmd.verbose is False
    assert not called


def test_defer_with_cli_args():
    called = Signal()

    class Main(Command):
        verbose: bool = False
        some_arg: str = arg(
            prompt="What's the value?",
            defer=True,
            parser=SignalParser(called),
        )

    # Happens during CLI arg parse
    assert not called
    Main.parse(["--some-arg", "foo"])
    assert called


def test_defer_not_provided():
    called = Signal()

    class Main(Command):
        verbose: bool = False
        some_arg: str = arg(
            prompt="What's the value?",
            defer=True,
            parser=SignalParser(called),
        )

    cmd = Main.parse([])

    # Happens during attribute access
    assert not called
    with replace_stdin("foo"):
        assert cmd.some_arg == "foo"
    assert called
