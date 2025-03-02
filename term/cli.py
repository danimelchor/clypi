from __future__ import annotations

import asyncio
import inspect
import logging
import re
import sys
import typing as t
from dataclasses import dataclass
from types import NoneType, UnionType

from Levenshtein import distance

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
    is_opt: bool = False
    short: str | None = None

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

    @property
    def display_name(self):
        name = parser.snake_to_dash(self.name)
        if self.is_opt:
            return f"--{name}"
        return name

    @property
    def short_display_name(self):
        assert self.short
        name = parser.snake_to_dash(self.short)
        return f"-{name}"


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

        return doc.replace("\n", " ")

    async def run(self, root: Command):
        """
        This function is where the business logic of your command
        should live.

        `self` contains the arguments for this command you can access
        as any other instance property.

        `root` is a pointer to the base command of your CLI so that you
        can access arguments passed to parent commands.
        """
        raise NotImplementedError

    @t.final
    async def astart(self, root: Command | None = None) -> None:
        if subcommand := getattr(self, "subcommand", None):
            return await subcommand.astart(root=root or self)
        return await self.run(root or self)

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
                defaults[field] = _Config.from_partial(
                    default,
                    parser=default.parser or parser.from_type(_type),
                    _type=_type,
                )
            else:
                defaults[field] = _Config(
                    default=default,
                    parser=parser.from_type(_type),
                    _type=_type,
                )
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
    def _fully_qualify(cls, name: str):
        fields = cls.fields()
        if name in fields:
            return name

        for field, field_conf in fields.items():
            if field_conf.short == name:
                return field

        return name

    @t.final
    @classmethod
    def _find_similar_arg(cls, arg: parser.Arg) -> str | None:
        if arg.is_pos():
            for pos in cls.subcommands().values():
                if distance(pos.name, arg.value) < 3:
                    return pos.name

            for pos in cls.positionals().values():
                if distance(pos.name, arg.value) < 3:
                    return pos.display_name
        else:
            for opt in cls.options().values():
                if distance(opt.name, arg.value) <= 2:
                    return opt.display_name
                if opt.short and distance(opt.short, arg.value) <= 1:
                    return opt.short_display_name

        return None

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
            parsed = parser.parse_as_attr(a)
            if parsed.is_pos() and (subcmd := cls.subcommands().get(parsed.value)):
                kwargs["subcommand"] = subcmd._type._parse(
                    args, parents=parents + [cls.prog()]
                )
                break

            # ---- Try to set to the current option ----
            full_name = (
                cls._fully_qualify(parsed.value)
                if parsed.is_short_opt
                else parsed.value
            )
            if not parsed.is_pos() and full_name in cls.options():
                option = cls.options()[full_name]
                if current_attr and current_attr.needs_more():
                    cls.print_help(
                        parents=parents,
                        error=f"Not enough values for {current_attr.name}",
                    )

                # Boolean flags don't need to parse more args later on
                if option.nargs == 0:
                    kwargs[full_name] = True
                else:
                    current_attr = parser.CurrentCtx(option.name, option.nargs)
                continue

            # ---- Try to assign to the current positional ----
            if not current_attr.name and (pos := cls._next_positional(kwargs)):
                current_attr = parser.CurrentCtx(pos.name, pos.nargs)

            # ---- Try to assign to the current ctx ----
            if current_attr.name and current_attr.has_more():
                if current_attr.name not in kwargs:
                    kwargs[current_attr.name] = []
                kwargs[current_attr.name].append(full_name)
                current_attr.use()
                continue
            elif current_attr.name and not current_attr.needs_more():
                if current_attr.name not in kwargs:
                    kwargs[current_attr.name] = []
                current_attr = None

            what = "argument" if parsed.is_pos else "option"
            error = f"Unknown {what} {parsed.orig!r}"
            if similar := cls._find_similar_arg(parsed):
                error += f". Did you mean {similar!r}?"
            cls.print_help(parents=parents, error=error)

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

            # Get the value passed in or the provided default
            value = kwargs[field] if field in kwargs else field_conf.get_default()

            # Subcommands are already parsed properly
            if field == "subcommand":
                setattr(instance, field, value)
                continue

            # Try parsing the string as the right type
            try:
                parsed = field_conf.parser(value)
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
                help=field_conf.help,
                short=field_conf.short,
                is_opt=True,
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
                help=field_conf.help,
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
    def print_help(cls, parents: list[str] = [], error: str | None = None):
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

    def __repr__(self) -> str:
        fields = ", ".join(
            f"{k}={v}"
            for k, v in vars(self).items()
            if v is not None and not k.startswith("_")
        )
        return f"{self.__class__.__name__}({fields})"
