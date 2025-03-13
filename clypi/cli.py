from __future__ import annotations

import asyncio
import inspect
import logging
import re
import sys
import typing as t
from types import NoneType, UnionType

from clypi import parsers
from clypi._cli import autocomplete as _auto
from clypi._cli import config as _conf
from clypi._cli import parser, type_util
from clypi._cli.config import Config, Positional, arg
from clypi._cli.context import CurrentCtx
from clypi._cli.formatter import ClypiFormatter, Formatter
from clypi._levenshtein import distance
from clypi._util import UNSET
from clypi.configuration import get_config
from clypi.exceptions import ClypiException, print_traceback
from clypi.prompts import prompt

logger = logging.getLogger(__name__)

__all__ = (
    "ClypiFormatter",
    "Command",
    "Formatter",
    "Positional",
    "arg",
)


HELP_ARGS: tuple[str, ...] = ("help", "-h", "--help")

CLYPI_FIELDS = "__clypi_fields__"
CLYPI_SUBCOMMANDS = "__clypi_subcommands__"
CLYPI_PARENTS = "__clypi_parents__"


def _camel_to_dashed(s: str):
    return re.sub(r"(?<!^)(?=[A-Z])", "-", s).lower()


class _CommandMeta(type):
    def __init__(
        self,
        name: str,
        bases: tuple[type, ...],
        dict: dict[str, t.Any],
        /,
        **kwds: t.Any,
    ) -> None:
        self._configure_fields()
        self._configure_subcommands()

    @t.final
    def _configure_fields(self) -> None:
        """
        Parses the type hints from the class extending Command and assigns each
        a _Config field with all the necessary info to display and parse them.
        """
        annotations: dict[str, t.Any] = inspect.get_annotations(self, eval_str=True)

        # Ensure each field is annotated
        for name, value in self.__dict__.items():
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

            default = getattr(self, field, UNSET)
            if isinstance(default, _conf.PartialConfig):
                value = _conf.Config.from_partial(
                    partial=default,
                    name=field,
                    parser=default.parser or parsers.from_type(_type),
                    arg_type=_type,
                )
            else:
                value = _conf.Config(
                    name=field,
                    default=default,
                    parser=parsers.from_type(_type),
                    arg_type=_type,
                )

            fields[field] = value

            # Set the values in the class properly instead of keeping the
            # _Config classes around
            if not value.has_default() and hasattr(self, field):
                delattr(self, field)
            elif value.has_default():
                setattr(self, field, value.get_default())

        setattr(self, CLYPI_FIELDS, fields)

    @t.final
    def _configure_subcommands(self) -> None:
        """
        Parses the type hints from the class extending Command and stores the
        subcommand class if any
        """
        annotations: dict[str, t.Any] = inspect.get_annotations(self, eval_str=True)
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

        setattr(self, CLYPI_SUBCOMMANDS, subcmds)


class Command(metaclass=_CommandMeta):
    def __init__(self, _from_parser=False) -> None:
        if not _from_parser:
            raise ClypiException(
                "Please, call `.parse()` on your command instead of instantiating it directly"
            )

    @classmethod
    def prog(cls) -> str:
        return _camel_to_dashed(cls.__name__)

    @classmethod
    def epilog(cls) -> str | None:
        return None

    @classmethod
    def _parents(cls) -> list[str]:
        return getattr(cls, CLYPI_PARENTS, [])

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
        self.print_help()

    @t.final
    async def astart(self) -> None:
        if subcommand := getattr(self, "subcommand", None):
            return await subcommand.astart()

        try:
            return await self.run()
        except get_config().nice_errors as e:
            print_traceback(e)

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
        return getattr(cls, CLYPI_FIELDS)

    @t.final
    @classmethod
    def _next_positional(cls, kwargs: dict[str, t.Any]) -> Config | None:
        """
        Traverse the current collected arguments and find the next positional
        arg we can assign to.
        """
        for name, pos in cls.positionals().items():
            # List positionals are a catch-all
            if type_util.is_list(pos.arg_type):
                return pos

            if name not in kwargs:
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
    def subcommands(cls) -> dict[str | None, type[Command] | None]:
        subcmds = t.cast(
            list[type[Command] | type[None]] | None,
            getattr(cls, CLYPI_SUBCOMMANDS, None),
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
    def options(cls) -> dict[str, Config]:
        options: dict[str, Config] = {}
        for field, field_conf in cls.fields().items():
            if field_conf.forwarded or field_conf.is_positional:
                continue

            options[field] = field_conf
        return options

    @t.final
    @classmethod
    def positionals(cls) -> dict[str, Config]:
        positionals: dict[str, Config] = {}
        for field, field_conf in cls.fields().items():
            if field_conf.forwarded or field_conf.is_opt:
                continue

            positionals[field] = field_conf
        return positionals

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
                *[name for name in cls.positionals()],
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
        parent_attrs: dict[str, str | list[str]] | None = None,
    ) -> t.Self:
        """
        Tries parsing args and if an error is shown, it displays the subcommand
        that failed the parsing's help page.
        """
        try:
            return cls._parse(args, parent_attrs)
        except (ValueError, TypeError) as e:
            if not get_config().help_on_fail:
                raise

            # The user might have started typing a subcommand but not
            # finished it so we cannot fully parse it, but we can recommend
            # the current command's args to autocomplete it
            if _auto.get_autocomplete_args() is not None:
                _auto.list_arguments(cls)

            # Otherwise, help page
            cls.print_help(exception=e)

        assert False, "Should never happen"

    @t.final
    @classmethod
    def _parse(
        cls,
        args: t.Iterator[str],
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
        unparsed: dict[str, str | list[str]] = {}

        # The current option or positional arg being parsed
        current_attr: CurrentCtx = CurrentCtx()

        def flush_ctx():
            nonlocal current_attr
            if current_attr and current_attr.needs_more():
                raise ValueError(f"Not enough values for {current_attr.name}")
            elif current_attr:
                unparsed[current_attr.name] = current_attr.collected
                current_attr = CurrentCtx()

        # The subcommand we need to parse
        subcommand: type[Command] | None = None

        requested_help = sys.argv[-1].lower() in HELP_ARGS
        for a in args:
            parsed = parser.parse_as_attr(a)
            if parsed.orig.lower() in HELP_ARGS:
                cls.print_help()

            # ---- Try to parse as a subcommand ----
            if parsed.is_pos() and parsed.value in cls.subcommands():
                subcommand = cls.subcommands()[parsed.value]
                break

            # ---- Try to set to the current option ----
            is_valid_long = parsed.is_long_opt() and parsed.value in cls.options()
            is_valid_short = parsed.is_short_opt() and cls._get_long_name(parsed.value)
            if parsed.is_opt() and not (is_valid_long or is_valid_short):
                raise cls._find_similar_exc(parsed)

            if is_valid_long or is_valid_short:
                long_name = cls._get_long_name(parsed.value) or parsed.value
                option = cls.options()[long_name]
                flush_ctx()

                # Boolean flags don't need to parse more args later on
                if option.nargs == 0:
                    unparsed[long_name] = "yes"
                else:
                    current_attr = CurrentCtx(option.name, option.nargs, option.nargs)
                continue

            # ---- Try to assign to the current positional ----
            if not current_attr.name and (pos := cls._next_positional(unparsed)):
                current_attr = CurrentCtx(pos.name, pos.nargs, pos.nargs)

            # ---- Try to assign to the current ctx ----
            if current_attr.name and current_attr.has_more():
                current_attr.collect(parsed.value)
                if not current_attr.has_more():
                    flush_ctx()
                continue

            raise cls._find_similar_exc(parsed)

        # Flush the context after the loop in case anything is left uncollected
        flush_ctx()

        # If the user requested help, skip prompting/parsing
        parsed_kwargs: dict[str, t.Any] = {}
        if not requested_help:
            # --- Parse as the correct values ---
            for field, field_conf in cls.fields().items():
                # If the field was provided through args
                if field in unparsed:
                    value = field_conf.parser(unparsed[field])

                # If the field was not provided but we can prompt, do so
                elif field_conf.prompt is not None:
                    value = prompt(
                        field_conf.prompt,
                        default=field_conf.get_default_or_missing(),
                        hide_input=field_conf.hide_input,
                        max_attempts=field_conf.max_attempts,
                        parser=field_conf.parser,
                    )

                # If the field is not provided yet but it has a default, use that
                elif field_conf.has_default():
                    value = field_conf.get_default()

                # If the field comes from a parent command, use that
                elif field_conf.forwarded and field in parent_attrs:
                    value = parent_attrs[field]

                # Whoops!
                else:
                    what = "argument" if field_conf.is_positional else "option"
                    raise ValueError(f"Missing required {what} {field!r}")

                # Try parsing the string as the right type
                parsed_kwargs[field] = value

        # --- Parse the subcommand passing in the parsed types ---
        if not subcommand and None not in cls.subcommands():
            raise ValueError("Missing required subcommand")
        elif subcommand:
            # Pass parent configs to child to get parenthood + config
            setattr(subcommand, CLYPI_PARENTS, cls._parents() + [cls.prog()])

            parsed_kwargs["subcommand"] = subcommand._safe_parse(
                args, parent_attrs=parsed_kwargs
            )

        # Assign to an instance
        instance = cls(_from_parser=True)
        for k, v in parsed_kwargs.items():
            setattr(instance, k, v)
        return instance

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
        instance = cls._safe_parse(args_iter)
        if _auto.get_autocomplete_args() is not None:
            _auto.list_arguments(cls)
        if list(args_iter):
            raise ValueError(f"Unknown arguments {list(args_iter)}")

        return instance

    @classmethod
    def print_help(cls, exception: Exception | None = None) -> t.NoReturn:
        help_str = get_config().help_formatter.format_help(
            prog=cls._parents() + [cls.prog()],
            description=cls.help(),
            epilog=cls.epilog(),
            options=list(cls.options().values()),
            positionals=list(cls.positionals().values()),
            subcommands=[s for s in cls.subcommands().values() if s],
            exception=exception,
        )
        sys.stdout.write(help_str)
        sys.stdout.flush()
        sys.exit(1 if exception else 0)

    def __repr__(self) -> str:
        fields = ", ".join(
            f"{k}={v}"
            for k, v in vars(self).items()
            if v is not None and not k.startswith("_")
        )
        return f"{self.__class__.__name__}({fields})"
