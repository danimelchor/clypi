from __future__ import annotations

import asyncio
import inspect
import logging
import re
import sys
import typing as t
from dataclasses import dataclass
from types import NoneType, UnionType

from term._cli import parser, type_util
from term._cli.config import MISSING, _Config, _PartialConfig
from term._cli.config import config as _config
from term._cli.formatter import TermFormatter

logger = logging.getLogger(__name__)

# re-exports
config = _config


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
    def fields(cls) -> dict[str, _Config]:
        defaults = {}
        for field, _type in inspect.get_annotations(cls).items():
            default = getattr(cls, field, MISSING)
            if isinstance(default, _PartialConfig):
                defaults[field] = _Config.from_partial(default, _type)
            else:
                defaults[field] = _Config(default=default, _type=_type)
        return defaults

    @t.final
    @classmethod
    def _next_positional(cls, kwargs: dict[str, t.Any]) -> Argument | None:
        for pos in cls.positionals().values():
            # List positionals are a catch-all
            if type_util.is_collection(pos._type):
                return pos

            if pos.name not in kwargs:
                return pos

    @t.final
    @classmethod
    def _parse(cls, args: t.Iterator[str], parents: list[str]) -> t.Self:
        """
        Given an iterator of arguments we recursively parse all options, arguments,
        and subcommands until the iterator is complete.
        """

        # The kwars used to initialize the dataclass
        kwargs = {}

        # The current option or positional arg being parsed
        current_attr = parser.CurrentCtx()

        for a in args:
            if a in ("-h", "--help"):
                cls.print_help(parents=parents)

            # ---- Try to parse as an arg/opt ----
            is_opt, attr, orig = parser.parse_as_attr(a)
            if not is_opt and (subcmd := cls.subcommands().get(attr)):
                kwargs["subcommand"] = subcmd._type._parse(
                    args, parents=parents + [cls.prog()]
                )
                break

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

        # If we finished the loop and we haven't saved current_attr, save it
        if current_attr.name and current_attr.needs_more():
            cls.print_help(
                parents=parents, error=f"Not enough values for {current_attr.name}"
            )
        elif current_attr.name and not current_attr.needs_more():
            if current_attr.name not in kwargs:
                kwargs[current_attr.name] = []
            current_attr = None

        # Parse as the correct values and assign to the instance
        instance = cls()
        for field, field_conf in cls.fields().items():
            if field not in kwargs and not field_conf.has_default():
                cls.print_help(parents, f"Missing required argument {field}")

            value = kwargs[field] if field in kwargs else field_conf.get_default()
            if field == "subcommand":
                setattr(instance, field, value)
                continue

            try:
                parsed = parser.parse_value_as_type(value, field_conf._type)
                setattr(instance, field, parsed)
            except Exception as e:
                cls.print_help(parents, f"Error parsing {field}: {e}")

        return instance

    @t.final
    @classmethod
    def subcommands(cls) -> dict[str, SubCommand]:
        if "subcommand" not in cls.fields():
            return {}

        # Get the subcommand type/types
        _type = cls.fields()["subcommand"]._type
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
        for field, field_conf in cls.fields().items():
            if field == "subcommand" or not field_conf.has_default():
                continue

            options[field] = Argument(
                field,
                type_util.remove_optionality(field_conf._type),
                help=cls.fields()[field].help,
            )
        return options

    @t.final
    @classmethod
    def positionals(cls) -> dict[str, Argument]:
        options = {}
        for field, field_conf in cls.fields().items():
            if field == "subcommand" or field_conf.has_default():
                continue

            options[field] = Argument(
                field,
                field_conf._type,
                help=cls.fields()[field].help,
            )
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
