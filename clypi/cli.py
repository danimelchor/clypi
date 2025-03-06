from __future__ import annotations

import asyncio
import inspect
import logging
import re
import sys
import typing as t
from dataclasses import dataclass
from types import NoneType, UnionType

from clypi._cli import autocomplete as _auto
from clypi._cli import config as _conf
from clypi._cli import parser, type_util
from clypi._cli.formatter import TermFormatter
from clypi._levenshtein import distance
from clypi._util import _UNSET
from clypi.prompts import prompt

logger = logging.getLogger(__name__)

# re-exports
config = _conf.config

HELP_ARGS: tuple[str, ...] = ("help", "-h", "--help")


def _camel_to_dashed(s: str):
    return re.sub(r"(?<!^)(?=[A-Z])", "-", s).lower()


@dataclass
class _Argument:
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
        assert self.short, f"Expected short to be set in {self}"
        name = parser.snake_to_dash(self.short)
        return f"-{name}"


class _CommandMeta(type):
    def __init__(cls, name, bases, dct) -> None:
        cls._configure_fields()
        cls._configure_subcommands()

    @t.final
    def _configure_fields(cls) -> None:
        """
        Parses the type hints from the class extending Command and assigns each
        a _Config field with all the necessary info to display and parse them.
        """
        annotations: dict[str, t.Any] = inspect.get_annotations(cls, eval_str=True)

        # Ensure each field is annotated
        for name, value in cls.__dict__.items():
            if (
                not name.startswith("_")
                and not isinstance(value, classmethod)
                and not callable(value)
                and name not in annotations
            ):
                raise TypeError(f"{name!r} has no type annotation")

        # Get the field config for each field
        fields: dict[str, _conf.Config[t.Any]] = {}
        for field, _type in annotations.items():
            if field == "subcommand":
                continue

            default = getattr(cls, field, _UNSET)
            if isinstance(default, _conf.PartialConfig):
                value = _conf.Config.from_partial(
                    default,
                    parser=default.parser or parser.from_type(_type),
                    arg_type=_type,
                )
            else:
                value = _conf.Config(
                    default=default,
                    parser=parser.from_type(_type),
                    arg_type=_type,
                )

            fields[field] = value

            # Set the values in the class properly instead of keeping the
            # _Config classes around
            if not value.has_default() and hasattr(cls, field):
                delattr(cls, field)
            elif value.has_default():
                setattr(cls, field, value.get_default())

        setattr(cls, "__clypi_fields__", fields)

    @t.final
    def _configure_subcommands(cls) -> None:
        """
        Parses the type hints from the class extending Command and stores the
        subcommand class if any
        """
        annotations: dict[str, t.Any] = inspect.get_annotations(cls, eval_str=True)
        if "subcommand" not in annotations:
            return

        _type = annotations["subcommand"]
        subcmds_tmp = [_type]
        if isinstance(_type, UnionType):
            subcmds_tmp = [s for s in _type.__args__ if s]

        subcmds: list[type[Command] | type[None]] = []
        for v in subcmds_tmp:
            if inspect.isclass(v) and issubclass(v, Command):
                subcmds.append(v)
            elif v is NoneType:
                subcmds.append(v)
            else:
                raise TypeError(
                    f"Did not expect to see a subcommand {v} of type {type(v)}"
                )

        setattr(cls, "__clypi_subcommands__", subcmds)


class Command(metaclass=_CommandMeta):
    @classmethod
    def prog(cls) -> str:
        return _camel_to_dashed(cls.__name__)

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

    async def run(self) -> None:
        """
        This function is where the business logic of your command
        should live.

        `self` contains the arguments for this command you can access
        as you would do with any other instance property.
        """
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
    def fields(cls) -> dict[str, _conf.Config[t.Any]]:
        """
        Parses the type hints from the class extending Command and assigns each
        a _Config field with all the necessary info to display and parse them.
        """
        return getattr(cls, "__clypi_fields__")

    @t.final
    @classmethod
    def _next_positional(cls, kwargs: dict[str, t.Any]) -> _Argument | None:
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

        return None

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
    def _find_similar_exc(cls, arg: parser.Arg) -> ValueError:
        """
        Utility function to find arguments similar to the one the
        user passed in to correct typos.
        """
        similar = None

        if arg.is_pos():
            all_pos: list[str] = [
                *[s for s in cls.subcommands() if s],
                *[p.name for p in cls.positionals().values()],
            ]
            for pos in all_pos:
                if distance(pos, arg.value) < 3:
                    similar = pos
                    break
        else:
            for opt in cls.options().values():
                if distance(opt.name, arg.value) <= 2:
                    similar = opt.display_name
                    break
                if opt.short and distance(opt.short, arg.value) <= 1:
                    similar = opt.short_display_name
                    break

        what = "argument" if arg.is_pos() else "option"
        error = f"Unknown {what} {arg.orig!r}"
        if similar is not None:
            error += f". Did you mean {similar!r}?"

        return ValueError(error)

    @t.final
    @classmethod
    def _safe_parse(
        cls,
        args: t.Iterator[str],
        parents: list[str],
        parent_attrs: dict[str, str | list[str]] | None = None,
    ) -> t.Self:
        """
        Tries parsing args and if an error is shown, it displays the subcommand
        that failed the parsing's help page.
        """
        try:
            return cls._parse(args, parents, parent_attrs)
        except (ValueError, TypeError) as e:
            # The user might have started typing a subcommand but not
            # finished it so we cannot fully parse it, but we can recommend
            # the current command's args to autocomplete it
            if _auto.get_autocomplete_args() is not None:
                _auto.list_arguments(cls)

            # Otherwise, help page
            cls.print_help(parents, exception=e)

        assert False, "Should never happen"

    @t.final
    @classmethod
    def _parse(
        cls,
        args: t.Iterator[str],
        parents: list[str],
        parent_attrs: dict[str, str | list[str]] | None = None,
    ) -> t.Self:
        """
        Given an iterator of arguments we recursively parse all options, arguments,
        and subcommands until the iterator is complete.

        When we encounter a subcommand, we parse all the types, then try to keep parsing the
        subcommand whilst we assign all forwarded types.
        """
        parent_attrs = parent_attrs or {}

        # An accumulator to store unparsed arguments for this class
        unparsed = {}

        # The current option or positional arg being parsed
        current_attr: parser.CurrentCtx = parser.CurrentCtx()

        def flush_ctx():
            nonlocal current_attr
            if current_attr and current_attr.needs_more():
                raise ValueError(f"Not enough values for {current_attr.name}")
            elif current_attr:
                unparsed[current_attr.name] = current_attr.collected
                current_attr = parser.CurrentCtx()

        # The subcommand we need to parse
        subcommand: type[Command] | None = None

        requested_help = sys.argv[-1].lower() in HELP_ARGS
        for a in args:
            parsed = parser.parse_as_attr(a)
            if parsed.orig.lower() in HELP_ARGS:
                cls.print_help(parents=parents)

            # ---- Try to parse as a subcommand ----
            if parsed.is_pos() and parsed.value in cls.subcommands():
                subcommand = cls.subcommands()[parsed.value]
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
                raise cls._find_similar_exc(parsed)

            if is_valid_long or is_valid_short:
                long_name = cls._get_long_name(parsed.value) or parsed.value
                option = cls.options()[long_name]
                flush_ctx()

                # Boolean flags don't need to parse more args later on
                if option.nargs == 0:
                    unparsed[long_name] = "yes"
                else:
                    current_attr = parser.CurrentCtx(
                        option.name, option.nargs, option.nargs
                    )
                continue

            # ---- Try to assign to the current positional ----
            if not current_attr.name and (pos := cls._next_positional(unparsed)):
                current_attr = parser.CurrentCtx(pos.name, pos.nargs, pos.nargs)

            # ---- Try to assign to the current ctx ----
            if current_attr.name and current_attr.has_more():
                current_attr.collect(parsed.value)
                continue

            raise cls._find_similar_exc(parsed)

        # If we finished the loop but an option needs more args, fail
        if current_attr.name and current_attr.needs_more():
            raise ValueError(f"Not enough values for {current_attr.name}")

        # If we finished the loop and we haven't saved current_attr, save it
        if current_attr.name and not current_attr.needs_more():
            unparsed[current_attr.name] = current_attr.collected
            current_attr = parser.CurrentCtx()

        # If the user requested help, skip prompting/parsing
        parsed_kwargs = {}
        if not requested_help:
            # --- Parse as the correct values ---
            for field, field_conf in cls.fields().items():
                # Get the value passed in, prompt, or the provided default
                if field in unparsed:
                    value = field_conf.parser(unparsed[field])
                elif field_conf.prompt is not None:
                    value = prompt(
                        field_conf.prompt,
                        default=field_conf.get_default_or_missing(),
                        hide_input=field_conf.hide_input,
                        max_attempts=field_conf.max_attempts,
                        parser=field_conf.parser,
                    )
                elif field_conf.has_default():
                    value = field_conf.get_default()
                elif field_conf.forwarded:
                    if field not in parent_attrs:
                        raise ValueError(f"Missing required argument {field}")
                    value = parent_attrs[field]
                else:
                    raise ValueError(f"Missing required argument {field}")

                # Try parsing the string as the right type
                parsed_kwargs[field] = value

        # --- Parse the subcommand passing in the parsed types ---
        if not subcommand and None not in cls.subcommands():
            raise ValueError("Missing required subcommand")
        elif subcommand:
            parsed_kwargs["subcommand"] = subcommand._safe_parse(
                args,
                parents=parents + [cls.prog()],
                parent_attrs=parsed_kwargs,
            )

        # Assign to an instance
        instance = cls()
        for k, v in parsed_kwargs.items():
            setattr(instance, k, v)
        return instance

    @t.final
    @classmethod
    def subcommands(cls) -> dict[str | None, type[Command] | None]:
        subcmds = t.cast(
            list[type[Command] | type[None]] | None,
            getattr(cls, "__clypi_subcommands__", None),
        )
        if subcmds is None:
            return {None: None}

        ret: dict[str | None, type[Command] | None] = {}
        for sub in subcmds:
            if issubclass(sub, Command):
                ret[sub.prog()] = sub
            else:
                ret[None] = None
        return ret

    @t.final
    @classmethod
    def options(cls) -> dict[str, _Argument]:
        options: dict[str, _Argument] = {}
        for field, field_conf in cls.fields().items():
            if field_conf.forwarded:
                continue

            # Is positional
            if not field_conf.has_default() and field_conf.prompt is None:
                continue

            options[field] = _Argument(
                field,
                type_util.remove_optionality(field_conf.arg_type),
                help=field_conf.help,
                short=field_conf.short,
                is_opt=True,
            )
        return options

    @t.final
    @classmethod
    def positionals(cls) -> dict[str, _Argument]:
        options: dict[str, _Argument] = {}
        for field, field_conf in cls.fields().items():
            if field_conf.forwarded:
                continue

            # Is option
            if field_conf.has_default() or field_conf.prompt is not None:
                continue

            options[field] = _Argument(
                field,
                field_conf.arg_type,
                help=field_conf.help,
            )
        return options

    @t.final
    @classmethod
    def parse(cls, args: t.Sequence[str] | None = None) -> t.Self:
        """
        Entry point of the program. Depending on some env vars it
        will either run the user-defined program or instead output the necessary
        completions for shells to provide autocomplete
        """
        args = args or sys.argv[1:]
        if _auto.requested_autocomplete_install(args):
            _auto.install_autocomplete(cls)

        # If this is an autocomplete call, we need the args from the env var passed in
        # by the shell's complete function
        if auto_args := _auto.get_autocomplete_args():
            args = auto_args

        norm_args = parser.normalize_args(args)
        args_iter = iter(norm_args)
        instance = cls._safe_parse(args_iter, parents=[])
        if _auto.get_autocomplete_args() is not None:
            _auto.list_arguments(cls)
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
            subcommands=[s for s in cls.subcommands().values() if s],
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
