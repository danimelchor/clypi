from __future__ import annotations

import argparse
import typing as t

from typing_extensions import override

import term


def debug(**msg):
    msg = {f"  {k}={v}" for k, v in msg.items()}
    s = ", ".join(msg)
    term.print("DEBUG:", s, "\n", fg="blue")


class TermArgparseFormatter(argparse.ArgumentDefaultsHelpFormatter):
    def format_help(self) -> str:
        return "Foo"

    def _format_text(self, text):
        """
        Format raw text like descriptions, epilog, etc.
        """
        return super()._format_text(text)

    def _format_usage(
        self,
        usage: str | None,
        actions: t.Iterable[argparse.Action],
        groups: t.Iterable[argparse._MutuallyExclusiveGroup],
        prefix: str | None,
    ) -> str:
        prefix = term.style("Usage: ", fg="yellow", bold=True)
        prog = term.style(self._prog, bold=True)
        # return prefix + prog
        return super()._format_usage(usage, actions, groups, prefix)

    @override
    def _metavar_formatter(self, action, default_metavar):
        """
        Renders special qualities about arguments like choices
        """
        if action.metavar is not None:
            result = action.metavar
        elif action.choices is not None:
            choice_strs = [str(choice) for choice in action.choices]
            result = "".join(
                [
                    term.style("{", fg="blue"),
                    term.style(",".join(choice_strs), reset=True, fg="cyan"),
                    term.style("}", fg="blue"),
                ]
            )
        else:
            result = default_metavar

        def format(tuple_size):
            if isinstance(result, tuple):
                return result
            return (result,) * tuple_size

        return format

    def _format_actions_usage(self, actions, groups):
        """
        Renders options and positionals like --foo
        """
        r = super()._format_actions_usage(actions, groups)
        debug(r=r)
        return term.style(r, fg="blue", bold=True)

    def _format_action_invocation(self, action):
        """
        Renders options and positionals like --foo
        """
        r = super()._format_action_invocation(action)
        return term.style(r, fg="blue", bold=True)
