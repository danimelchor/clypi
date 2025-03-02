from __future__ import annotations

import asyncio
import inspect
import logging
import re
import sys
import typing as t
from dataclasses import _MISSING_TYPE, MISSING, Field, dataclass
from dataclasses import field as dataclass_field
from types import NoneType, UnionType

from term._cli import parser, type_util
from term._cli.formatter import TermFormatter

logger = logging.getLogger(__name__)


def _camel_to_dashed(s: str):
    return re.sub(r"(?<!^)(?=[A-Z])", "-", s).lower()


@dataclass
class Argument:
    name: str
    _type: t.Any
    help: str | None

    @property
    def nargs(self) -> parser.Nargs:
        if self._type is bool:
            return 0

        if type_util.is_collection(self._type):
            return "*"

        if type_util.is_tuple(self._type):
            sz = type_util.tuple_size(self._type)
            return "+" if sz == float("inf") else sz

        return 1


@dataclass
class SubCommand:
    name: str
    _type: type[Command]
    help: str


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
        if not doc or doc.startswith(cls.__name__ + "("):
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
        return cls._annotations()[name]

    @t.final
    @classmethod
    def _has_attr(cls, name: str) -> bool:
        return name in cls._annotations()

    @t.final
    @classmethod
    def _next_positional(cls, kwargs: dict[str, t.Any]) -> Argument | None:
        for pos in cls.positionals().values():
            # List positionals are a catch-all
            if type_util.is_collection(pos._type):
                return pos

            if field not in kwargs:
                return pos

    @t.final
    @classmethod
    def _has_default(cls, name: str) -> bool:
        params: Field = getattr(cls, "__dataclass_fields__")[name]
        if params.default is not MISSING or params.default_factory is not MISSING:
            return True
        return False

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
    def _parse(cls, args: t.Iterator[str], parents: list[str]) -> t.Self:
        """
        Given an iterator of arguments we recursively parse all options, arguments,
        and subcommands until the iterator is complete.
        """

        # The kwars used to initialize the dataclass
        kwargs = {}

        current_attr = parser.CurrentCtx()

        for a in args:
            # ---- Try to parse as an arg/opt ----
            is_opt, attr, orig = parser.parse_as_attr(a)
            if not is_opt and (subcmd := cls.subcommands().get(attr)):
                kwargs["subcommand"] = subcmd._type._parse(
                    args, parents=parents + [cls.prog()]
                )
                break

            if is_opt and attr in ("h", "help"):
                cls.print_help(parents=parents)

            # ---- Try to set to the current option ----
            if is_opt and attr in cls.options():
                option = cls.options()[attr]
                if current_attr and not current_attr.needs_more():
                    if current_attr.name not in kwargs:
                        kwargs[current_attr.name] = []
                elif current_attr:
                    cls.print_help(
                        parents=parents,
                        error=f"Not enough values for {current_attr.name}",
                    )

                current_attr = parser.CurrentCtx(option.name, option.nargs)
                continue

            # ---- Try to assign to the current positional ----
            if not current_attr.name and (pos := cls._next_positional(kwargs)):
                current_attr = parser.CurrentCtx(pos.name, pos.nargs)

            # ---- Try to assign to the current ctx ----
            if current_attr.name and current_attr.has_more():
                if current_attr.name not in kwargs:
                    kwargs[current_attr.name] = []
                kwargs[current_attr.name].append(attr)
                current_attr.use()
                continue
            elif current_attr.name and not current_attr.needs_more():
                if current_attr.name not in kwargs:
                    kwargs[current_attr.name] = []
                current_attr = None

            what = "option" if is_opt else "argument"
            cls.print_help(parents=parents, error=f"Unknown {what} {orig!r}")

        if current_attr.name and current_attr.needs_more():
            cls.print_help(
                parents=parents, error=f"Not enough values for {current_attr.name}"
            )

        # Parse as the correct values
        parsed_kwargs = {}
        for k, v in kwargs.items():
            if k == "subcommand":
                parsed_kwargs[k] = v
                continue
            try:
                parsed_kwargs[k] = parser.parse_value_as_type(v, cls._type_of(k))
            except Exception as e:
                cls.print_help(parents, f"Error parsing {k}: {e}")

        try:
            return cls(**parsed_kwargs)
        except TypeError as e:
            parts = str(e).split(" ")[1:]
            cls.print_help(parents, " ".join(parts))

    @t.final
    @classmethod
    def subcommands(cls) -> dict[str, SubCommand]:
        if "subcommand" not in cls._annotations():
            return {}

        # Get the subcommand type/types
        _type = cls._type_of("subcommand")
        subcmds = [_type]
        if isinstance(_type, UnionType):
            subcmds = [s for s in _type.__args__ if s is not NoneType]

        for v in subcmds:
            assert inspect.isclass(v) and issubclass(v, Command)

        return {
            s.name(): SubCommand(name=s.name(), _type=s, help=s.help()) for s in subcmds
        }

    @t.final
    @classmethod
    def options(cls) -> dict[str, Argument]:
        options = {}
        for field, _type in cls._annotations().items():
            if field == "subcommand" or not cls._has_default(field):
                continue

            options[field] = Argument(
                field,
                type_util.remove_optionality(_type),
                help=cls._get_help(field),
            )
        return options

    @t.final
    @classmethod
    def positionals(cls) -> dict[str, Argument]:
        options = {}
        for field, _type in cls._annotations().items():
            if field == "subcommand" or cls._has_default(field):
                continue

            options[field] = Argument(field, _type, help=cls._get_help(field))
        return options

    @t.final
    @classmethod
    def parse(cls, args: t.Sequence[str] | None = None) -> t.Self:
        """
        This is the entry point to start parsing arguments
        """
        norm_args = parser.normalize_args(args or sys.argv[1:])
        args_iter = iter(norm_args)
        instance = cls._parse(args_iter, parents=[])
        if list(args_iter):
            raise ValueError(f"Unknown arguments {list(args_iter)}")

        return instance

    @t.final
    @classmethod
    def print_help(cls, parents: list[str], error: str | None = None):
        tf = TermFormatter(
            prog=parents + [cls.prog()],
            description=cls.help(),
            epilog=cls.epilog(),
            options=list(cls.options().values()),
            positionals=list(cls.positionals().values()),
            subcommands=list(cls.subcommands().values()),
            error=error,
        )
        print(tf.format_help())
        sys.exit(1 if error else 0)


def field(help: str | None = None, *args, **kwargs):
    return dataclass_field(*args, **kwargs, metadata={"help": help})
