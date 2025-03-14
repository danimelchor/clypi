from __future__ import annotations

import typing as t
from dataclasses import dataclass
from functools import cached_property

from clypi import _type_util
from clypi._arg_parser import dash_to_snake
from clypi._boxed import boxed
from clypi._colors import ColorType, style
from clypi._exceptions import format_traceback
from clypi._indented import indented
from clypi._stack import stack

if t.TYPE_CHECKING:
    from clypi import Command
    from clypi._arg_config import Config


def _ext(ls: list[str], s: str | list[str] | None) -> None:
    if isinstance(s, str):
        ls.append(s)
    elif isinstance(s, list):
        ls.extend(s)
    return None


class Formatter(t.Protocol):
    def format_help(
        self,
        full_command: list[str],
        description: str | None,
        epilog: str | None,
        options: list[Config[t.Any]],
        positionals: list[Config[t.Any]],
        subcommands: list[type[Command]],
        exception: Exception | None,
    ) -> str: ...


@dataclass
class ClypiFormatter:
    boxed: bool = True
    show_option_types: bool = False
    normalize_dots: t.Literal[".", ""] | None = ""

    @cached_property
    def theme(self):
        from clypi._configuration import get_config

        return get_config().theme

    def _maybe_norm_help(self, message: str) -> str:
        """
        Utility function to add or remove dots from the end of all option/arg
        descriptions to have a more consistent formatting experience.
        """
        if message and self.normalize_dots == "." and message[-1].isalnum():
            return message + "."
        if message and self.normalize_dots == "" and message[-1] == ".":
            return message[:-1]
        return message

    def _maybe_boxed(
        self, *columns: list[str], title: str, color: ColorType | None = None
    ) -> list[str]:
        first_col, *rest = columns

        # Filter out empty columns
        rest = list(filter(any, rest))

        if not self.boxed:
            section_title = self.theme.section_title(title)

            # For non-boxed design, we just indent the first col a bit so that it looks
            # like it's inside the section
            stacked = stack(indented(first_col), *rest, lines=True)
            return [section_title] + stacked + [""]

        stacked = stack(first_col, *rest, lines=True)
        return list(boxed(stacked, width="max", title=title, color=color))

    def _format_option_value(self, option: Config[t.Any]):
        if option.nargs == 0:
            return ""
        placeholder = dash_to_snake(option.name).upper()
        return self.theme.placeholder(f"<{placeholder}>")

    def _format_option(self, option: Config[t.Any]) -> tuple[str, ...]:
        help = self._maybe_norm_help(option.help or "")

        # E.g.: -r, --requirements <REQUIREMENTS>
        name = self.theme.long_option(option.display_name)
        short_usage = (
            self.theme.short_option(option.short_display_name) if option.short else ""
        )
        usage = name
        if short_usage:
            usage = short_usage + ", " + usage
        if not self.show_option_types:
            usage += " " + self._format_option_value(option)

        # E.g.: TEXT
        type_str = ""
        type_upper = str(option.parser).upper()
        if self.show_option_types:
            type_str = self.theme.type_str(type_upper)
        elif _type_util.has_metavar(option.arg_type):
            help = help + " " + type_upper if help else type_upper

        return usage, type_str, help

    def _format_options(self, options: list[Config[t.Any]]) -> list[str] | None:
        if not options:
            return None

        usage: list[str] = []
        type_str: list[str] = []
        help: list[str] = []
        for o in options:
            # Hidden options do not get displayed for the user
            if o.hidden:
                continue

            u, ts, hp = self._format_option(o)
            usage.append(u)
            type_str.append(ts)
            help.append(hp)

        return self._maybe_boxed(usage, type_str, help, title="Options")

    def _format_positional_with_mod(self, positional: Config[t.Any]) -> str:
        # E.g.: [FILES]...
        pos_name = positional.name.upper()
        name = f"[{pos_name}]{positional.modifier}"
        return name

    def _format_positional(self, positional: Config[t.Any]) -> tuple[str, ...]:
        # E.g.: [FILES]... or FILES
        name = (
            self.theme.positional(self._format_positional_with_mod(positional))
            if not self.show_option_types
            else self.theme.positional(positional.name.upper())
        )

        help = positional.help or ""
        type_str = (
            self.theme.type_str(str(positional.parser).upper())
            if self.show_option_types
            else ""
        )
        return name, type_str, self._maybe_norm_help(help)

    def _format_positionals(
        self, positionals: list[Config[t.Any]]
    ) -> list[str] | str | None:
        if not positionals:
            return None

        name: list[str] = []
        type_str: list[str] = []
        help: list[str] = []
        for p in positionals:
            n, ts, hp = self._format_positional(p)
            name.append(n)
            type_str.append(ts)
            help.append(hp)

        return self._maybe_boxed(name, type_str, help, title="Arguments")

    def _format_subcommand(self, subcmd: type[Command]) -> tuple[str, str]:
        name = self.theme.subcommand(subcmd._name())
        help = subcmd.help() or ""
        return name, self._maybe_norm_help(help)

    def _format_subcommands(
        self, subcommands: list[type[Command]]
    ) -> list[str] | str | None:
        if not subcommands:
            return None

        name: list[str] = []
        help: list[str] = []
        for p in subcommands:
            n, hp = self._format_subcommand(p)
            name.append(n)
            help.append(hp)

        return self._maybe_boxed(name, help, title="Subcommands")

    def _format_header(
        self,
        full_command: list[str],
        options: list[Config[t.Any]],
        positionals: list[Config[t.Any]],
        subcommands: list[type[Command]],
    ) -> list[str] | str | None:
        prefix = self.theme.usage("Usage:")
        command_str = self.theme.usage_command(" ".join(full_command))

        option = self.theme.usage_args(" [OPTIONS]") if options else ""
        command = self.theme.usage_args(" COMMAND") if subcommands else ""

        positionals_str: list[str] = []
        for pos in positionals:
            name = self._format_positional_with_mod(pos)
            positionals_str.append(self.theme.usage_args(name))
        positional = " " + " ".join(positionals_str) if positionals else ""

        return [f"{prefix} {command_str}{option}{command}{positional}", ""]

    def _format_description(self, description: str | None) -> list[str] | str | None:
        if not description:
            return None
        return [self._maybe_norm_help(description), ""]

    def _format_epilog(self, epilog: str | None) -> list[str] | str | None:
        if not epilog:
            return None
        return ["", self._maybe_norm_help(epilog)]

    def _format_exception(self, exception: Exception | None) -> list[str] | str | None:
        if not exception:
            return None

        if self.boxed:
            return self._maybe_boxed(
                format_traceback(exception), title="Error", color="red"
            )

        # Special section title since it's an error
        section_title = style("Error:", fg="red", bold=True)
        stacked = indented(format_traceback(exception, color=None))
        return [section_title] + stacked + [""]

    def format_help(
        self,
        full_command: list[str],
        description: str | None,
        epilog: str | None,
        options: list[Config[t.Any]],
        positionals: list[Config[t.Any]],
        subcommands: list[type[Command]],
        exception: Exception | None,
    ) -> str:
        lines: list[str] = []

        # Header
        _ext(
            lines, self._format_header(full_command, options, positionals, subcommands)
        )

        # Description
        _ext(lines, self._format_description(description))

        # Subcommands
        _ext(lines, self._format_subcommands(subcommands))

        # Positionals
        _ext(lines, self._format_positionals(positionals))

        # Options
        _ext(lines, self._format_options(options))

        # Epilog
        _ext(lines, self._format_epilog(epilog))

        # Exceptions
        _ext(lines, self._format_exception(exception))

        return "\n".join(lines)
