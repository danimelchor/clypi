import asyncio
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


@t.final
class Spinner(AbstractAsyncContextManager):
    def __init__(
        self,
        title: str,
        animation: Spin | list[str] = Spin.DOTS,
        prefix: str = " ",
        suffix: str = "…",
        speed: float = 1,
    ) -> None:
        self.animation = animation
        self.prefix = prefix
        self.suffix = suffix
        self.title = title

        self._task: asyncio.Task[None] | None = None
        self._manual_exit: bool = False
        self._frame_idx: int = 0
        self._refresh_rate = 0.7 / speed / len(self._frames)

    async def __aenter__(self):
        self._task = asyncio.create_task(self._spin())
        return self

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
        sys.stdout.write(MOVE_START)
        sys.stdout.write(DEL_LINE)

        # Write msg and flush
        sys.stdout.write(msg)
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

    def _exit(self, msg: str | None = None, success: bool = True):
        if t := self._task:
            t.cancel()

        color: ColorType = "green" if success else "red"
        icon = "✔️" if success else "×"
        self._print(msg or self.title, icon=icon, color=color, end="\n")

    def done(self, msg: str | None = None):
        self._manual_exit = True
        self._exit(msg)

    def fail(self, msg: str | None = None):
        self._manual_exit = True
        self._exit(msg, success=False)

    def log(self, msg: str):
        self._print(msg.rstrip(), end="\n")
        self._render_frame()

    async def pipe(
        self,
        pipe: asyncio.StreamReader | None,
        color: ColorType = "blue",
        prefix: str = "",
    ) -> None:
        if not pipe:
            return

        while True:
            line = await pipe.readline()
            if not line:
                break

            icon = f"   ┃ {prefix}" if prefix else "   ┃"
            self._print(
                line.decode(),
                icon=icon,
                color=color,
            )
            self._render_frame()
