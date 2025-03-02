from __future__ import annotations

import asyncio
import inspect
import logging
import re
import sys
import typing as t
from dataclasses import dataclass
from types import NoneType, UnionType

from Levenshtein import distance  # type: ignore

from clypi._cli import config as _conf
from clypi._cli import parser, type_util
from clypi._cli.formatter import TermFormatter

logger = logging.getLogger(__name__)

# re-exports
config = _conf.config


def _camel_to_dashed(s: str):
    return re.sub(r"(?<!^)(?=[A-Z])", "-", s).lower()


@dataclass
class Argument:
    name: str
    arg_type: t.Any
    help: str | None
    is_opt: bool = False
    short: str | None = None

    @property
    def nargs(self) -> parser.Nargs:
        if self.arg_type is bool:
            return 0

        if type_util.is_collection(self.arg_type):
            return "*"

        if type_util.is_tuple(self.arg_type):
            sz = type_util.tuple_size(self.arg_type)
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
    klass: type[Command]
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

    async def run(self, root: Command) -> None:
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
    def fields(cls) -> dict[str, _conf.Config[t.Any]]:
        """
        Parses the type hints from the class extending Command and assigns each
        a _Config field with all the necessary info to display and parse them.
        """
        defaults: dict[str, _conf.Config[t.Any]] = {}
        for field, _type in inspect.get_annotations(cls).items():
            default = getattr(cls, field, _conf.MISSING)
            if isinstance(default, _conf.PartialConfig):
                defaults[field] = _conf.Config.from_partial(
                    default,
                    parser=default.parser or parser.from_type(_type),
                    arg_type=_type,
                )
            else:
                defaults[field] = _conf.Config(
                    default=default,
                    parser=parser.from_type(_type),
                    arg_type=_type,
                )
        return defaults

    @t.final
    @classmethod
    def _next_positional(cls, kwargs: dict[str, t.Any]) -> Argument | None:
        """
        Traverse the current collected arguments and find the next positional
        arg we can assign to.
        """
        for pos in cls.positionals().values():
            # List positionals are a catch-all
            if type_util.is_collection(pos.arg_type):
                return pos

            if pos.name not in kwargs:
                return pos

    @t.final
    @classmethod
    def _get_long_name(cls, short: str) -> str | None:
        fields = cls.fields()
        for field, field_conf in fields.items():
            if field_conf.short == short:
                return field
        return None

    @t.final
    @classmethod
    def _find_similar_arg(cls, arg: parser.Arg) -> str | None:
        """
        Utility function to find arguments similar to the one the
        user passed in to correct typos.
        """
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
    def _safe_parse(cls, args: t.Iterator[str], parents: list[str]) -> t.Self:
        """
        Tries parsing args and if an error is shown, it displays the subcommand
        that failed the parsing's help page.
        """
        try:
            return cls._parse(args, parents)
        except (ValueError, TypeError) as e:
            cls.print_help(parents, exception=e)

    @t.final
    @classmethod
    def _parse(cls, args: t.Iterator[str], parents: list[str]) -> t.Self:
        """
        Given an iterator of arguments we recursively parse all options, arguments,
        and subcommands until the iterator is complete.
        """

        # The kwars used to initialize the dataclass
        kwargs: dict[str, t.Any] = {}

        # The current option or positional arg being parsed
        current_attr = parser.CurrentCtx()

        def flush_ctx():
            nonlocal current_attr
            if current_attr and current_attr.needs_more():
                raise ValueError(f"Not enough values for {current_attr.name}")
            elif current_attr:
                kwargs[current_attr.name] = current_attr.collected
                current_attr = None

        def find_similar(parsed: parser.Arg):
            what = "argument" if parsed.is_pos() else "option"
            error = f"Unknown {what} {parsed.orig!r}"
            if similar := cls._find_similar_arg(parsed):
                error += f". Did you mean {similar!r}?"
            raise ValueError(error)

        for a in args:
            if a in ("-h", "--help"):
                cls.print_help(parents=parents)

            # ---- Try to parse as an arg/opt ----
            parsed = parser.parse_as_attr(a)
            if parsed.is_pos() and (subcmd := cls.subcommands().get(parsed.value)):
                kwargs["subcommand"] = subcmd.klass._safe_parse(
                    args, parents=parents + [cls.prog()]
                )
                break

            # ---- Try to set to the current option ----
            is_valid_long = (
                not parsed.is_pos()
                and parsed.is_long_opt()
                and parsed.value in cls.options()
            )
            is_valid_short = (
                not parsed.is_pos()
                and parsed.is_short_opt()
                and cls._get_long_name(parsed.value) is not None
            )
            if (
                parsed.is_short_opt()
                or parsed.is_long_opt()
                and not (is_valid_long or is_valid_short)
            ):
                raise find_similar(parsed)

            if is_valid_long or is_valid_short:
                long_name = cls._get_long_name(parsed.value) or parsed.value
                option = cls.options()[long_name]
                flush_ctx()

                # Boolean flags don't need to parse more args later on
                if option.nargs == 0:
                    kwargs[long_name] = True
                else:
                    current_attr = parser.CurrentCtx(
                        option.name, option.nargs, option.nargs
                    )
                continue

            # ---- Try to assign to the current positional ----
            if not current_attr.name and (pos := cls._next_positional(kwargs)):
                current_attr = parser.CurrentCtx(pos.name, pos.nargs, pos.nargs)

            # ---- Try to assign to the current ctx ----
            if current_attr.name and current_attr.has_more():
                current_attr.collect(parsed.value)
                continue

            raise find_similar(parsed)

        # If we finished the loop but an option needs more args, fail
        if current_attr.name and current_attr.needs_more():
            raise ValueError(f"Not enough values for {current_attr.name}")

        # If we finished the loop and we haven't saved current_attr, save it
        if current_attr.name and not current_attr.needs_more():
            kwargs[current_attr.name] = current_attr.collected
            current_attr = None

        # Parse as the correct values and assign to the instance
        instance = cls()
        for field, field_conf in cls.fields().items():
            if field not in kwargs and not field_conf.has_default():
                raise ValueError(f"Missing required argument {field}")

            # Get the value passed in or the provided default
            value = kwargs[field] if field in kwargs else field_conf.get_default()

            # Subcommands are already parsed properly
            if field == "subcommand":
                setattr(instance, field, value)
                continue

            # Try parsing the string as the right type
            parsed = field_conf.parser(value)
            setattr(instance, field, parsed)

        return instance

    @t.final
    @classmethod
    def subcommands(cls) -> dict[str, SubCommand]:
        if "subcommand" not in cls.fields():
            return {}

        # Get the subcommand type/types
        _type = cls.fields()["subcommand"].arg_type
        subcmds = [_type]
        if isinstance(_type, UnionType):
            subcmds = [s for s in _type.__args__ if s is not NoneType]

        for v in subcmds:
            assert inspect.isclass(v) and issubclass(v, Command)

        return {
            s.name(): SubCommand(name=s.name(), klass=s, help=s.help()) for s in subcmds
        }

    @t.final
    @classmethod
    def options(cls) -> dict[str, Argument]:
        options: dict[str, Argument] = {}
        for field, field_conf in cls.fields().items():
            if field == "subcommand" or not field_conf.has_default():
                continue

            options[field] = Argument(
                field,
                type_util.remove_optionality(field_conf.arg_type),
                help=field_conf.help,
                short=field_conf.short,
                is_opt=True,
            )
        return options

    @t.final
    @classmethod
    def positionals(cls) -> dict[str, Argument]:
        options: dict[str, Argument] = {}
        for field, field_conf in cls.fields().items():
            if field == "subcommand" or field_conf.has_default():
                continue

            options[field] = Argument(
                field,
                field_conf.arg_type,
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
        instance = cls._safe_parse(args_iter, parents=[])
        if list(args_iter):
            raise ValueError(f"Unknown arguments {list(args_iter)}")

        return instance

    @t.final
    @classmethod
    def print_help(cls, parents: list[str] = [], *, exception: Exception | None = None):
        tf = TermFormatter(
            prog=parents + [cls.prog()],
            description=cls.help(),
            epilog=cls.epilog(),
            options=list(cls.options().values()),
            positionals=list(cls.positionals().values()),
            subcommands=list(cls.subcommands().values()),
            exception=exception,
        )
        print(tf.format_help())
        sys.exit(1 if exception else 0)

    def __repr__(self) -> str:
        fields = ", ".join(
            f"{k}={v}"
            for k, v in vars(self).items()
            if v is not None and not k.startswith("_")
        )
        return f"{self.__class__.__name__}({fields})"
