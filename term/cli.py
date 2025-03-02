from __future__ import annotations

import asyncio
import inspect
import logging
import re
import sys
import typing as t
from dataclasses import _MISSING_TYPE, MISSING, Field
from dataclasses import field as dataclass_field
from types import UnionType

from term._cli import parser, type_util

logger = logging.getLogger(__name__)


def _camel_to_dashed(s: str):
    return re.sub(r"(?<!^)(?=[A-Z])", "-", s).lower()


class Command:
    @t.final
    @classmethod
    def name(cls):
        return _camel_to_dashed(cls.__name__)

    @classmethod
    def prog(cls) -> str:
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
    def _nargs_for(cls, name: str) -> float:
        _type = cls._annotations()[name]

        # List positionals are a catch-all
        if type_util.is_collection(_type):
            return float("inf")

        return 1

    @t.final
    @classmethod
    def _next_positional(cls, kwargs: dict[str, t.Any]) -> str | None:
        for field, _type in cls._annotations().items():
            if cls._get_default(field) is not MISSING:
                continue

            # List positionals are a catch-all
            if type_util.is_collection(_type):
                return field

            if field not in kwargs:
                return field

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
    def _parse(cls, args: t.Iterator[str]) -> t.Self:
        """
        Given an iterator of arguments we recursively parse all options, arguments,
        and subcommands until the iterator is complete.
        """

        # The kwars used to initialize the dataclass
        kwargs = {}

        current_attr_name: str | None = None
        current_attr_nargs: float = 1

        for a in args:
            # ---- Try to parse as an arg/opt ----
            is_opt, attr = parser.parse_as_attr(a)
            if not is_opt and (subcmd := cls._get_subcommands().get(attr)):
                kwargs["subcommand"] = subcmd._parse(args)
                break

            # Assign to current object
            if is_opt:
                if cls._is_flag(attr):
                    kwargs[attr] = True
                else:
                    current_attr_name = attr
                    current_attr_nargs = cls._nargs_for(attr)
                continue

            # ---- Try to assign to the current option ----
            if current_attr_name and current_attr_nargs > 0:
                if current_attr_name not in kwargs:
                    kwargs[current_attr_name] = []
                kwargs[current_attr_name].append(attr)
                current_attr_nargs -= 1
                continue
            elif current_attr_name:
                current_attr_name = None

            # ---- Try to assign to the current positional ----
            if not current_attr_name and (pos_name := cls._next_positional(kwargs)):
                if pos_name not in kwargs:
                    kwargs[pos_name] = []
                if len(kwargs[pos_name]) < cls._nargs_for(pos_name):
                    kwargs[pos_name].append(attr)
                continue

            raise ValueError(f"Unknown argument {attr} for {cls.name()}")

        # Parse as the correct values
        parsed_kwargs = {}
        for k, v in kwargs.items():
            if k == "subcommand":
                parsed_kwargs[k] = v
                continue
            parsed_kwargs[k] = parser.parse_value_as_type(v, cls._type_of(k))

        return cls(**parsed_kwargs)

    @t.final
    @classmethod
    def _get_subcommands(cls) -> dict[str, type[Command]]:
        if "subcommand" not in cls._annotations():
            return {}

        # Get the subcommand type/types
        _type = cls._type_of("subcommand")
        subcmds = (
            {a.name(): a for a in _type.__args__}
            if isinstance(_type, UnionType)
            else {_type.name(): _type}
        )
        for v in subcmds.values():
            assert inspect.isclass(v) and issubclass(v, Command)

        return t.cast(dict[str, type[Command]], subcmds)

    @t.final
    @classmethod
    def parse(cls, args: t.Sequence[str] | None = None) -> t.Self:
        """
        This is the entry point to start parsing arguments
        """
        args_iter = iter(args or sys.argv[1:])
        instance = cls._parse(args_iter)
        if args_iter:
            raise ValueError(f"Unknown arguments {list(args_iter)}")

        return instance

    @t.final
    @classmethod
    def print_help(cls):
        print("Help...")


def field(help: str | None = None, *args, **kwargs):
    return dataclass_field(*args, **kwargs, metadata={"help": help})
