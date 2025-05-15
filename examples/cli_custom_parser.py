import re

from typing_extensions import override

import clypi.parsers as cp
from clypi import Command, arg, cprint


class SlackChannel(cp.Str):
    @override
    def __call__(self, raw: str | list[str], /) -> str:
        parsed = super().__call__(raw)
        if not re.match(r"#[a-z0-9-]+", parsed):
            raise ValueError("Invalid slack channel")
        return parsed


class SlackChannelId(cp.Int):
    @override
    def __call__(self, raw: str | list[str], /) -> int:
        parsed = super().__call__(raw)
        if parsed < 1_000_000 or parsed > 9_999_999:
            raise ValueError(f"Invalid Slack channel {parsed}, it must be 8 digits")
        return parsed


class Main(Command):
    """An example of how useful custom parsers can be"""

    slack: str | int | None = arg(
        help="The Slack channel to send notifications to",
        prompt="What Slack channel should we send notifications to?",
        parser=SlackChannel() | SlackChannelId() | cp.NoneParser(),
    )

    @override
    async def run(self):
        cprint(f"Slack: {self.slack} ({type(self.slack)})", fg="blue")
        cprint("Try using a valid or invalid slack channel", fg="cyan")


if __name__ == "__main__":
    main: Main = Main.parse()
    main.start()
