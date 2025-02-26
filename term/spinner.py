import asyncio
import itertools
import sys
from contextlib import AbstractAsyncContextManager
from typing import final

import term
from term.colors import ColorType
from term.const import ESC

DEFAULT_CHARSET_1 = "⣾⣽⣻⢿⡿⣟⣯⣷"
DEFAULT_CHARSET_2 = "⠁⠂⠄⡀⢀⠠⠐⠈"

MOVE_START = f"{ESC}1G"
DEL_LINE = f"{ESC}0K"


@final
class Spinner(AbstractAsyncContextManager):
    def __init__(
        self,
        title: str,
        charset=DEFAULT_CHARSET_1,
        prefix: str = " ",
        suffix: str = "…",
    ) -> None:
        self.charset = charset
        self.prefix = prefix
        self.suffix = suffix
        self.title = title

        self._task: asyncio.Task | None = None
        self._manual_exit: bool = False
        self._frame: str = ""

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
        icon = term.style(icon + " ", fg=color) if icon else ""
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
            icon=self._frame,
            color="blue",
        )

    async def _spin(self) -> None:
        for frame in itertools.cycle(self.charset):
            self._frame = frame
            self._render_frame()
            await asyncio.sleep(0.05)

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

        color = "green" if success else "red"
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


if __name__ == "__main__":
    from term.examples.spinner import main as example

    asyncio.run(example())
