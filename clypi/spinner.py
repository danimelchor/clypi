import asyncio
import io
import sys
import typing as t
from contextlib import AbstractAsyncContextManager, AbstractContextManager, suppress

from typing_extensions import override

import clypi
from clypi._data.spinners import Spin as _Spin
from clypi.colors import ColorType
from clypi.const import ESC

MOVE_START = f"{ESC}1G"
DEL_LINE = f"{ESC}0K"

Spin = _Spin


class _PerLineIO(io.TextIOBase):
    def __init__(self, *args, new_line_cb: t.Callable[[str], None], **kwargs) -> None:
        """
        A string buffer that captures text and calls the callback `new_line_cb`
        on every line written to the buffer. Useful to redirect stdout and stderr
        but only print them nicely on every new line.
        """
        super().__init__(*args, **kwargs)
        self._new_line_cb = new_line_cb
        self.buffer: list[str] = []

    @override
    def write(self, s: str, /) -> int:
        """
        When we get a string, split it by new lines, submit every line we've
        collected and keep the remainder for future writes
        """
        self.buffer.extend(s.split("\n"))
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


class RedirectStdPipe(AbstractContextManager):
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
    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()

    def stop(self) -> None:
        setattr(sys, self._pipe, self._original)

    def write(self, s: str):
        self._original.write(s)

    def flush(self):
        self._original.flush()


@t.final
class Spinner(AbstractAsyncContextManager):
    def __init__(
        self,
        title: str,
        animation: Spin | list[str] = Spin.DOTS,
        prefix: str = " ",
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
    async def __aexit__(self, _type, value, traceback):
        # If a user already called `.done()`, leaving the closure
        # should not re-trigger a re-render
        if self._manual_exit:
            return

        if any([_type, value, traceback]):
            await self.fail()
        else:
            await self.done()

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
        icon = "✔️" if success else "×"
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
        end="\n",
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
