from __future__ import annotations

import argparse
import asyncio
import inspect
import logging
import re
import typing as t
from dataclasses import _MISSING_TYPE, MISSING, Field
from dataclasses import field as dataclass_field
from types import UnionType

logger = logging.getLogger(__name__)


def _type_to_argparse(_type: t.Any):
    if t.get_origin(_type) is t.Literal:
        return {"choices": _type.__args__}
    elif t.get_origin(_type) is list:
        return {"type": _type.__args__[0], "nargs": "+"}
    return {"type": _type}


def _camel_to_dashed(s: str):
    return re.sub(r"(?<!^)(?=[A-Z])", "-", s).lower()


class Command:
    @t.final
    @classmethod
    def name(cls):
        return _camel_to_dashed(cls.__name__)

    @t.final
    @classmethod
    def help(cls):
        doc = inspect.getdoc(cls)
        if not doc or doc.startswith(cls.__name__):
            return None
        return doc

    async def run(self):
        raise NotImplementedError

    async def astart(self) -> None:
        if subcommand := getattr(self, "subcommand", None):
            return await subcommand.astart()
        return await self.run()

    def start(self) -> None:
        asyncio.run(self.astart())

    @classmethod
    def _subparser_name(cls, parent: str | None = None):
        if not parent:
            return "subparser_" + cls.name()
        return f"subparser_{parent}_{cls.name()}"

    @classmethod
    def _annotations(cls):
        return inspect.get_annotations(cls)

    @classmethod
    def _type_of(cls, name: str):
        if name not in cls._annotations():
            raise ValueError(f"{cls.__name__} has no value {name}")

        return cls._annotations()[name]

    @classmethod
    def _is_flag(cls, name: str) -> bool:
        return cls._type_of(name) is bool

    @classmethod
    def _get_default(cls, name: str) -> t.Any | _MISSING_TYPE:
        params: Field = getattr(cls, "__dataclass_fields__")[name]
        if params.default is not MISSING:
            return params.default
        if params.default_factory is not MISSING:
            return params.default_factory()
        return MISSING

    @classmethod
    def _get_help(cls, name: str) -> str | None:
        params: Field = getattr(cls, "__dataclass_fields__")[name]
        return params.metadata.get("help", None)

    @classmethod
    def _parse(cls, args: argparse.Namespace, parent: str | None = None) -> t.Self:
        kwargs = {}
        for name in cls._annotations():
            if name == "subcommand":
                value = getattr(args, cls._subparser_name(parent))
                subcmd = cls._subcommand_with_name(value)
                kwargs["subcommand"] = subcmd._parse(
                    args,
                    parent=cls.name(),
                )
            elif hasattr(args, name):
                kwargs[name] = getattr(args, name)

        return cls(**kwargs)

    @classmethod
    def _get_subcommands(cls) -> list[type[Command]]:
        if "subcommand" not in cls._annotations():
            return []

        _type = cls._type_of("subcommand")
        subcmds = []
        if isinstance(_type, UnionType):
            subcmds = list(_type.__args__)
        else:
            subcmds = [_type]

        for s in subcmds:
            assert inspect.isclass(s) and issubclass(s, Command)

        return t.cast(t.List[type[Command]], subcmds)

    @classmethod
    def _subcommand_with_name(cls, name: str) -> type[Command]:
        for subcmd in cls._get_subcommands():
            if subcmd.name() == name:
                return subcmd

        raise ValueError(f"Subcommand {name} does not exist in {cls.name()}")

    @classmethod
    def _configure_arguments(cls, parser: argparse.ArgumentParser):
        for name, _type in cls._annotations().items():
            if name == "subcommand":
                continue

            help = cls._get_help(name)
            if cls._is_flag(name):
                parser.add_argument(f"--{name}", action="store_true", help=help)
                continue

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

    @classmethod
    def _configure_parser(
        cls, parser: argparse.ArgumentParser, parent: str | None = None
    ):
        cls._configure_arguments(parser)

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
                )
                subcmd._configure_parser(
                    subparser,
                    parent=cls.name(),
                )

    @classmethod
    def parse(cls) -> t.Self:
        parser = argparse.ArgumentParser()
        cls._configure_parser(parser)
        args = parser.parse_args()
        return cls._parse(args)


def field(help: str | None = None, *args, **kwargs):
    return dataclass_field(*args, **kwargs, metadata={"help": help})
