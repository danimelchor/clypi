import asyncio
import io
import sys
import typing as t
from contextlib import AbstractAsyncContextManager

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
        super().__init__(*args, **kwargs)
        self._new_line_cb = new_line_cb
        self.buffer: list[str] = []

    def write(self, s: str, /) -> int:
        self.buffer.extend(s.split("\n"))
        if len(self.buffer) > 1:
            for i in range(0, len(self.buffer) - 1):
                if line := self.buffer[i]:
                    self._new_line_cb(line)
            self.buffer = self.buffer[-1:]
        return 0


class _RedirectStdPipe:
    def __init__(
        self,
        pipe: t.Literal["stdout", "stderr"],
        target: t.Callable[[str], t.Any],
    ) -> None:
        self._pipe = pipe
        self._original = getattr(sys, pipe)
        self._new = _PerLineIO(new_line_cb=target)

    def start(self) -> None:
        setattr(sys, self._pipe, self._new)

    def stop(self) -> None:
        setattr(sys, self._pipe, self._original)

    def write(self, s: str):
        self._original.write(s)


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
        self._stdout = _RedirectStdPipe("stdout", self.log)
        self._stderr = _RedirectStdPipe("stderr", self.log)

    async def __aenter__(self):
        if self._capture:
            self._stdout.start()
            # self._stderr.start()

        self._task = asyncio.create_task(self._spin())
        return self

    @override
    async def __aexit__(self, _type, value, traceback):
        # If a user already called `.done()`, leaving the closure
        # should not re-trigger a re-render
        if self._manual_exit:
            return

        if any([_type, value, traceback]):
            self.fail()
        else:
            self.done()

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
        sys.stdout.flush()

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

    def _exit(self, msg: str | None = None, success: bool = True):
        if t := self._task:
            t.cancel()

        color: ColorType = "green" if success else "red"
        icon = "✔️" if success else "×"
        self._print(msg or self.title, icon=icon, color=color, end="\n")

        # Stop capturing stdout/stderrr
        if self._capture:
            self._stdout.stop()
            self._stderr.stop()

    def done(self, msg: str | None = None):
        self._manual_exit = True
        self._exit(msg)

    def fail(self, msg: str | None = None):
        self._manual_exit = True
        self._exit(msg, success=False)

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
