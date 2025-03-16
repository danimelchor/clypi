import asyncio
import io
import sys
import typing as t
from contextlib import AbstractAsyncContextManager, AbstractContextManager, suppress
from types import TracebackType

from typing_extensions import override

import clypi
from clypi._colors import ESC, ColorType
from clypi._data.spinners import Spin as _Spin

MOVE_START = f"{ESC}1G"
DEL_LINE = f"{ESC}0K"

Spin = _Spin


class _PerLineIO(io.TextIOBase):
    def __init__(self, new_line_cb: t.Callable[[str], None]) -> None:
        """
        A string buffer that captures text and calls the callback `new_line_cb`
        on every line written to the buffer. Useful to redirect stdout and stderr
        but only print them nicely on every new line.
        """
        super().__init__()
        self._new_line_cb = new_line_cb
        self.buffer: list[str] = []

    @override
    def write(self, s: str, /) -> int:
        """
        When we get a string, split it by new lines, submit every line we've
        collected and keep the remainder for future writes
        """
        parts = s.split("\n")

        # If there's a buffer, there's a half-way sentence there, so we merge it
        if self.buffer:
            self.buffer[0] += parts[0]
            self.buffer.extend(parts[1:])
        else:
            self.buffer = parts

        if len(self.buffer) > 1:
            for i in range(0, len(self.buffer) - 1):
                if line := self.buffer[i]:
                    self._new_line_cb(line)
            self.buffer = self.buffer[-1:]
        return 0

    @override
    def flush(self) -> None:
        """
        If flush is called, print whatever we have even if there's no new line
        """
        if self.buffer[0]:
            self._new_line_cb(self.buffer[0])
        self.buffer = []


class RedirectStdPipe(AbstractContextManager[None]):
    def __init__(
        self,
        pipe: t.Literal["stdout", "stderr"],
        target: t.Callable[[str], t.Any],
    ) -> None:
        """
        Given a pipe (stdout or stderr) and a callback function, it redirects
        each line from the pipe into the callback. Useful to redirect users'
        outputs to a custom function without them needing to directly call it.
        """
        self._pipe = pipe
        self._original = getattr(sys, pipe)
        self._new = _PerLineIO(new_line_cb=target)

    @override
    def __enter__(self) -> None:
        self.start()

    def start(self) -> None:
        setattr(sys, self._pipe, self._new)

    @override
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
        /,
    ) -> bool | None:
        self.stop()
        return None

    def stop(self) -> None:
        setattr(sys, self._pipe, self._original)

    def write(self, s: str):
        self._original.write(s)

    def flush(self):
        self._original.flush()


@t.final
class Spinner(AbstractAsyncContextManager["Spinner"]):
    def __init__(
        self,
        title: str,
        animation: Spin | list[str] = Spin.DOTS,
        prefix: str = "",
        suffix: str = "…",
        speed: float = 1,
        capture: bool = False,
    ) -> None:
        """
        A context manager that lets you run async code while nicely
        displaying a spinning animation. Using `capture=True` will
        capture all the stdout and stderr written during the spinner
        and display it nicely.
        """

        self.animation = animation
        self.prefix = prefix
        self.suffix = suffix
        self.title = title

        self._task: asyncio.Task[None] | None = None
        self._manual_exit: bool = False
        self._frame_idx: int = 0
        self._refresh_rate = 0.7 / speed / len(self._frames)

        # For capturing stdout, stderr
        self._capture = capture
        self._stdout = RedirectStdPipe("stdout", self.log)
        self._stderr = RedirectStdPipe("stderr", self.log)

    async def __aenter__(self):
        if self._capture:
            self._stdout.start()
            self._stderr.start()

        self._task = asyncio.create_task(self._spin())
        return self

    @override
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
        /,
    ) -> bool | None:
        # If a user already called `.done()`, leaving the closure
        # should not re-trigger a re-render
        if self._manual_exit:
            return None

        if any([exc_type, exc_value, traceback]):
            await self.fail()
        else:
            await self.done()

        return None

    def _print(
        self,
        msg: str,
        icon: str | None = None,
        color: ColorType | None = None,
        end: str = "",
    ):
        # Build the line being printed
        icon = clypi.style(icon + " ", fg=color) if icon else ""
        msg = f"{self.prefix}{icon}{msg}{end}"

        # Wipe the line for next render
        self._stdout.write(MOVE_START)
        self._stdout.write(DEL_LINE)

        # Write msg and flush
        self._stdout.write(msg)
        self._stdout.flush()

    def _render_frame(self):
        self._print(
            self.title + self.suffix,
            icon=self._frames[self._frame_idx],
            color="blue",
        )

    @property
    def _frames(self) -> list[str]:
        return (
            self.animation.value if isinstance(self.animation, Spin) else self.animation
        )

    async def _spin(self) -> None:
        while True:
            self._frame_idx = (self._frame_idx + 1) % len(self._frames)
            self._render_frame()
            await asyncio.sleep(self._refresh_rate)

    async def _exit(self, msg: str | None = None, success: bool = True):
        if t := self._task:
            t.cancel()
            with suppress(asyncio.CancelledError):
                await t

        # Stop capturing stdout/stderrr
        if self._capture:
            self._stdout.stop()
            self._stderr.stop()

        color: ColorType = "green" if success else "red"
        icon = "✔" if success else "×"
        self._print(msg or self.title, icon=icon, color=color, end="\n")

    async def done(self, msg: str | None = None):
        self._manual_exit = True
        await self._exit(msg)

    async def fail(self, msg: str | None = None):
        self._manual_exit = True
        await self._exit(msg, success=False)

    def log(
        self,
        msg: str,
        icon: str = "   ┃",
        color: ColorType | None = None,
        end: str = "\n",
    ):
        """
        Log a message nicely from inside a spinner. If `capture=True`, you can
        simply use `print("foo")`.
        """
        self._print(msg.rstrip(), icon=icon, color=color, end=end)
        self._render_frame()

    async def pipe(
        self,
        pipe: asyncio.StreamReader | None,
        color: ColorType = "blue",
        prefix: str = "",
    ) -> None:
        """
        Pass in an async pipe for the spinner to display
        """
        if not pipe:
            return

        while True:
            line = await pipe.readline()
            if not line:
                break

            msg = f"{prefix} {line.decode()}" if prefix else line.decode()
            self.log(msg, color=color)


P = t.ParamSpec("P")
R = t.TypeVar("R")
Func = t.Callable[P, t.Coroutine[t.Any, t.Any, R]]


def spinner(
    title: str,
    animation: Spin | list[str] = Spin.DOTS,
    prefix: str = " ",
    suffix: str = "…",
    speed: float = 1,
    capture: bool = False,
) -> t.Callable[[Func[P, R]], Func[P, R]]:
    """
    Utility decorator to wrap a function and display a Spinner while it's running.
    """

    def wrapper(fn: Func[P, R]) -> Func[P, R]:
        async def inner(*args: P.args, **kwargs: P.kwargs) -> R:
            async with Spinner(
                title=title,
                animation=animation,
                prefix=prefix,
                suffix=suffix,
                speed=speed,
                capture=capture,
            ):
                return await fn(*args, **kwargs)

        return inner

    return wrapper
