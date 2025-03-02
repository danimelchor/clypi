from __future__ import annotations

import argparse
import typing as t
from dataclasses import dataclass

import term


@dataclass
class ProgramConfig:
    prog: str


def _get_long_short(ls: t.Sequence[str]) -> tuple[str, str | None]:
    if len(ls) == 1:
        return ls[0], None
    return ls[1], ls[0]


@dataclass
class TermFormatter:
    prog: str
    description: str
    epilog: str
    options: list[argparse.Action]
    positionals: list[argparse.Action]
    subcommands: argparse.Action | None

    def _format_option(self, option: argparse.Action) -> list[str]:
        long, short = _get_long_short(option.option_strings)
        usage = term.style(long, fg="blue", bold=True)
        short_usage = term.style(short, fg="green", bold=True) if short else ""
        help = option.help or ""
        return [usage + " " + short_usage + " " + help]

    def _format_options(self) -> list[str]:
        lines = []
        for o in self.options:
            lines.extend(self._format_option(o))
        return lines

    def _format_positional(self, positional: argparse.Action) -> list[str]:
        name = term.style(positional.dest, fg="blue", bold=True)
        help = positional.help or ""
        return [name + " " + help]

    def _format_positionals(self) -> list[str]:
        lines = []
        for p in self.positionals:
            lines.extend(self._format_positional(p))
        return lines

    def _format_header(self) -> list[str]:
        prefix = term.style("Usage:", fg="yellow", bold=True)
        prog = term.style(self.prog, bold=True)

        options = "[" + term.style("OPTIONS", fg="blue", bold=True) + "]"
        command = term.style("COMMAND", fg="blue", bold=True)
        positional = "[" + term.style("ARGS", fg="blue", bold=True) + "]"

        return [f"{prefix} {prog} {options} {command} {positional}"]

    def _format_description(self) -> list[str]:
        return [self.description]

    def format_help(self) -> str:
        lines = []

        # Header
        lines.extend(self._format_header())

        # Description
        lines.extend(self._format_description())

        # Options
        lines.extend(self._format_options())

        # Positionals
        lines.extend(self._format_positionals())

        return "\n".join(lines)
