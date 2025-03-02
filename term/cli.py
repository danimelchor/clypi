from __future__ import annotations

import argparse
import asyncio
import inspect
import logging
import re
import sys
import typing as t
from dataclasses import _MISSING_TYPE, MISSING, Field
from dataclasses import field as dataclass_field
from types import UnionType

from typing_extensions import override

import term
from term._cli.formatter import TermArgparseFormatter

logger = logging.getLogger(__name__)

_FORMATTER_CLASS = TermArgparseFormatter


def _type_to_argparse(_type: t.Any):
    if t.get_origin(_type) is t.Literal:
        return {"choices": _type.__args__}
    elif t.get_origin(_type) is list:
        return {"type": _type.__args__[0], "nargs": "+"}
    return {"type": _type}


def _camel_to_dashed(s: str):
    return re.sub(r"(?<!^)(?=[A-Z])", "-", s).lower()


class TermParser(argparse.ArgumentParser):
    @override
    def error(self, message):
        sys.stderr.write(term.style("Error: ", fg="red", bold=True) + "%s\n" % message)
        self.print_help()
        sys.exit(2)


class Command:
    @t.final
    @classmethod
    def name(cls):
        return _camel_to_dashed(cls.__name__)

    @classmethod
    def prog(cls) -> str | None:
        return cls.name()

    @classmethod
    def epilog(cls) -> str | None:
        return None

    @t.final
    @classmethod
    def help(cls):
        doc = inspect.getdoc(cls)

        # Dataclass sets a default docstring so ignore that
        if not doc or doc.startswith(cls.__name__):
            return None

        return doc

    async def run(self):
        raise NotImplementedError

    @t.final
    async def astart(self) -> None:
        if subcommand := getattr(self, "subcommand", None):
            return await subcommand.astart()
        return await self.run()

    @t.final
    def start(self) -> None:
        asyncio.run(self.astart())

    @t.final
    @classmethod
    def _subparser_name(cls, parent: str | None = None):
        if not parent:
            return "subparser_" + cls.name()
        return f"subparser_{parent}_{cls.name()}"

    @t.final
    @classmethod
    def _annotations(cls):
        return inspect.get_annotations(cls)

    @t.final
    @classmethod
    def _type_of(cls, name: str):
        if name not in cls._annotations():
            raise ValueError(f"{cls.__name__} has no value {name}")

        return cls._annotations()[name]

    @t.final
    @classmethod
    def _is_flag(cls, name: str) -> bool:
        return cls._type_of(name) is bool

    @t.final
    @classmethod
    def _get_default(cls, name: str) -> t.Any | _MISSING_TYPE:
        params: Field = getattr(cls, "__dataclass_fields__")[name]
        if params.default is not MISSING:
            return params.default
        if params.default_factory is not MISSING:
            return params.default_factory()
        return MISSING

    @t.final
    @classmethod
    def _get_help(cls, name: str) -> str | None:
        params: Field = getattr(cls, "__dataclass_fields__")[name]
        return params.metadata.get("help", None)

    @t.final
    @classmethod
    def _parse(cls, args: argparse.Namespace, parent: str | None = None) -> t.Self:
        """
        Given an argparse namespace we create the dataclass for this command and all
        subcommands
        """
        kwargs = {}
        for name in cls._annotations():
            # Subcommands are stored in a particular subparser
            if name == "subcommand":
                value = getattr(args, cls._subparser_name(parent))
                subcmd = cls._subcommand_with_name(value)

                # Recursively parse subcommand
                kwargs["subcommand"] = subcmd._parse(
                    args,
                    parent=cls.name(),
                )
            elif hasattr(args, name):
                kwargs[name] = getattr(args, name)

        return cls(**kwargs)

    @t.final
    @classmethod
    def _get_subcommands(cls) -> list[type[Command]]:
        if "subcommand" not in cls._annotations():
            return []

        # Get the subcommand type/types
        _type = cls._type_of("subcommand")
        subcmds = list(_type.__args__) if isinstance(_type, UnionType) else [_type]
        for s in subcmds:
            assert inspect.isclass(s) and issubclass(s, Command)

        return t.cast(t.List[type[Command]], subcmds)

    @t.final
    @classmethod
    def _subcommand_with_name(cls, name: str) -> type[Command]:
        for subcmd in cls._get_subcommands():
            if subcmd.name() == name:
                return subcmd
        raise ValueError(f"Subcommand {name} does not exist in {cls.name()}")

    @t.final
    @classmethod
    def _configure_arguments(cls, parser: argparse.ArgumentParser):
        """
        Configures this command's arguments based on the dataclass fields
        """
        for name, _type in cls._annotations().items():
            # Subcommand is not an actual argument
            if name == "subcommand":
                continue

            # Get the help message for this field to display
            help = cls._get_help(name)

            # Flags are boolean values
            if cls._is_flag(name):
                parser.add_argument(f"--{name}", action="store_true", help=help)
                continue

            # If the attr has a default, it's an option. Otherwise its a positional argument
            default = cls._get_default(name)
            if default is not MISSING:
                parser.add_argument(
                    f"--{name}",
                    default=default,
                    help=help,
                    **_type_to_argparse(_type),
                )
            else:
                parser.add_argument(
                    name,
                    help=help,
                    **_type_to_argparse(_type),
                )

    @t.final
    @classmethod
    def _configure_parser(
        cls,
        parser: argparse.ArgumentParser,
        parent: str | None = None,
    ):
        """
        Configures the arguments for this particular command/subcommand
        and traverses through subcommands
        """

        # Configure the arguments for this command
        cls._configure_arguments(parser)

        # Configure each subcommand's args
        if subcmds := cls._get_subcommands():
            subparsers = parser.add_subparsers(
                required=True,
                dest=cls._subparser_name(parent),
            )
            for subcmd in subcmds:
                subparser = subparsers.add_parser(
                    subcmd.name(),
                    help=subcmd.help(),
                    description=subcmd.help(),
                    formatter_class=_FORMATTER_CLASS,
                )

                # Configure the subparser
                subcmd._configure_parser(
                    subparser,
                    parent=cls.name(),
                )

    @t.final
    @classmethod
    def parse(cls) -> t.Self:
        """
        This is the entry point to start parsing arguments
        """
        parser = TermParser(
            prog=cls.prog(),
            description=cls.help(),
            epilog=cls.epilog(),
            formatter_class=_FORMATTER_CLASS,
        )
        cls._configure_parser(parser)
        args = parser.parse_args()
        return cls._parse(args)


def field(help: str | None = None, *args, **kwargs):
    return dataclass_field(*args, **kwargs, metadata={"help": help})
