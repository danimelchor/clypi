from __future__ import annotations

import typing as t
from dataclasses import dataclass

import term
from term import boxed, stack
from term._cli import type_util

if t.TYPE_CHECKING:
    from term.cli import Argument, SubCommand


@dataclass
class ProgramConfig:
    prog: str


def _ext(ls: list[str], s: str | list[str] | None) -> list[str] | str | None:
    if s is None:
        return ls
    if isinstance(s, str):
        ls.append(s)
    else:
        ls.extend(s)


@dataclass
class TermFormatter:
    prog: list[str]
    description: str | None
    epilog: str | None
    options: list[Argument]
    positionals: list[Argument]
    subcommands: list[SubCommand]
    error: str | None

    def _format_option(self, option: Argument) -> tuple[str, ...]:
        usage = term.style(option.display_name, fg="blue", bold=True)
        short_usage = (
            term.style(option.short_display_name, fg="green", bold=True)
            if option.short
            else ""
        )
        type_str = term.style(
            type_util.type_to_str(option._type).upper(), fg="yellow", bold=True
        )
        help = option.help or ""
        return usage, short_usage, type_str, help

    def _format_options(self) -> list[str] | None:
        if not self.options:
            return None

        usage, short_usage, type_str, help = [], [], [], []
        for o in self.options:
            u, su, ts, hp = self._format_option(o)
            usage.append(u)
            short_usage.append(su)
            type_str.append(ts)
            help.append(hp)
        return list(boxed(stack(usage, short_usage, type_str, help), title="Options"))

    def _format_positional(self, positional: Argument) -> t.Any:
        name = term.style(positional.name, fg="blue", bold=True)
        help = positional.help or ""
        type_str = term.style(
            type_util.type_to_str(positional._type).upper(), fg="yellow", bold=True
        )
        return name, type_str, help

    def _format_positionals(self) -> list[str] | str | None:
        if not self.positionals:
            return None

        name, type_str, help = [], [], []
        for p in self.positionals:
            n, ts, hp = self._format_positional(p)
            name.append(n)
            type_str.append(ts)
            help.append(hp)
        return list(boxed(stack(name, type_str, help), title="Arguments"))

    def _format_subcommand(self, subcmd: SubCommand) -> t.Any:
        name = term.style(subcmd.name, fg="blue", bold=True)
        help = subcmd.help or ""
        return name, help

    def _format_subcommands(self) -> list[str] | str | None:
        if not self.subcommands:
            return None

        name, help = [], []
        for p in self.subcommands:
            n, hp = self._format_subcommand(p)
            name.append(n)
            help.append(hp)
        return list(boxed(stack(name, help), title="Subcommands"))

    def _format_header(self) -> list[str] | str | None:
        prefix = term.style("Usage:", fg="yellow")
        prog = term.style(" ".join(self.prog), bold=True)

        options = (
            " [" + term.style("OPTIONS", fg="blue", bold=True) + "]"
            if self.options
            else ""
        )
        command = (
            term.style(" COMMAND", fg="blue", bold=True) if self.subcommands else ""
        )
        positional = (
            " "
            + " ".join(
                term.style(p.name.upper(), fg="blue", bold=True)
                for p in self.positionals
            )
            if self.positionals
            else ""
        )

        return [f"{prefix} {prog}{options}{command}{positional}"]

    def _format_description(self) -> list[str] | str | None:
        if not self.description:
            return None
        return [self.description, ""]

    def _format_error(self) -> list[str] | str | None:
        if not self.error:
            return ""
        return list(boxed([self.error], title="Error", color="red"))

    def format_help(self) -> str:
        lines = []

        # Header
        _ext(lines, self._format_header())
        _ext(lines, "")

        # Description
        _ext(lines, self._format_description())

        # Options
        _ext(lines, self._format_options())

        # Positionals
        _ext(lines, self._format_positionals())

        # Subcommands
        _ext(lines, self._format_subcommands())

        # Errors
        _ext(lines, self._format_error())

        return "\n".join(lines)
