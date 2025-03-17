from __future__ import annotations

import asyncio
import dataclasses
import inspect
import logging
import re
import sys
import typing as t
from types import NoneType, UnionType

from clypi import _type_util, parsers
from clypi._cli import arg_config, arg_parser, autocomplete
from clypi._cli.arg_config import Config, Positional, arg
from clypi._cli.context import CurrentCtx
from clypi._cli.deferred import DeferredValue
from clypi._cli.distance import closest
from clypi._cli.formatter import ClypiFormatter, Formatter
from clypi._configuration import get_config
from clypi._exceptions import print_traceback
from clypi._prompts import prompt
from clypi._util import UNSET

logger = logging.getLogger(__name__)

__all__ = (
    "ClypiFormatter",
    "Command",
    "Formatter",
    "Positional",
    "arg",
)


HELP_ARGS: tuple[str, ...] = ("help", "-h", "--help")

CLYPI_OPTIONS = "__clypi_options__"
CLYPI_POSITIONALS = "__clypi_positionals__"
CLYPI_IN_ORDER_FIELD_NAMES = "__clypi_in_order_field_names__"
CLYPI_SUBCOMMANDS = "__clypi_subcommands__"
CLYPI_PARENTS = "__clypi_parents__"


def _camel_to_dashed(s: str):
    return re.sub(r"(?<!^)(?=[A-Z])", "-", s).lower()


class _CommandMeta(type):
    def __init__(
        self,
        name: str,
        bases: tuple[type, ...],
        attrs: dict[str, t.Any],
        /,
        **kwds: t.Any,
    ) -> None:
        super(_CommandMeta, self).__init__(name, bases, attrs)
        self._ensure_fields_are_annotated()
        self._configure_subcommands()
        self._configure_fields()

    @t.final
    def _ensure_fields_are_annotated(self) -> None:
        """
        Ensures that every single field is annotated with type hints
        """
        annotations: dict[str, t.Any] = inspect.get_annotations(self, eval_str=True)
        for name, value in self.__dict__.items():
            if (
                not name.startswith("_")
                and not isinstance(value, classmethod)
                and not callable(value)
                and name not in annotations
            ):
                raise TypeError(f"{name!r} has no type annotation")

    @t.final
    def _configure_fields(self) -> None:
        """
        Parses the type hints from the class extending Command and assigns each
        a field Config with all the necessary info to display and parse them.
        """
        annotations: dict[str, t.Any] = inspect.get_annotations(self, eval_str=True)

        # Mappings for each arg type
        options: dict[str, arg_config.Config[t.Any]] = {}
        positionals: dict[str, arg_config.Config[t.Any]] = {}
        field_names: list[str] = []

        # Get the config for each field
        for field, _type in annotations.items():
            field_names.append(field)
            if field == "subcommand":
                continue

            # Get the specified default for the field (e.g.: foo: bool)
            default = getattr(self, field, UNSET)

            # Check if it comes from `arg()` or if it's a real value
            if isinstance(default, arg_config.PartialConfig):
                field_conf = arg_config.Config.from_partial(
                    partial=default,
                    name=field,
                    parser=default.parser or parsers.from_type(_type),
                    arg_type=_type,
                )
            else:
                # If it's a real value then the default is the value itself
                field_conf = arg_config.Config(
                    name=field,
                    default=default,
                    parser=parsers.from_type(_type),
                    arg_type=_type,
                )

            # Store in the right dict
            if field_conf.is_positional:
                positionals[field] = field_conf
            else:
                options[field] = field_conf

            # Set the values in the class properly instead of keeping the
            # Config fields around
            if not field_conf.has_default() and hasattr(self, field):
                delattr(self, field)
            elif field_conf.has_default():
                setattr(self, field, field_conf.get_default())

        # Store all fields
        setattr(self, CLYPI_OPTIONS, options)
        setattr(self, CLYPI_POSITIONALS, positionals)
        setattr(self, CLYPI_IN_ORDER_FIELD_NAMES, field_names)

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
            subcmds_tmp = _type_util.union_inner(_type)

        # Store in mapping (name -> type)
        subcmds: dict[str | None, type[Command] | None] = {}
        for v in subcmds_tmp:
            if inspect.isclass(v) and issubclass(v, Command):
                subcmds[v.prog()] = v
            elif v is NoneType:
                subcmds[None] = None
            else:
                raise TypeError(
                    f"Did not expect to see a subcommand {v} of type {type(v)}"
                )

        # Replace the class with a default if it has any
        default = getattr(self, "subcommand", UNSET)
        if default is not UNSET:
            setattr(self, "subcommand", default)
        elif hasattr(self, "subcommand"):
            delattr(self, "subcommand")

        # Store list of subcommands
        setattr(self, CLYPI_SUBCOMMANDS, subcmds)

    @t.final
    def inherit(self, parent: type[Command]) -> list[str]:
        """
        This function is called by the parent command during parsing to configure
        inherited fields and the parenthood relationship so that the full command
        is displayed properly.

        Returns the list of inherited fields
        """
        setattr(self, CLYPI_PARENTS, parent.full_command())

        # For inherited args, configure them with the parent's configs
        options = self.options()
        inherited: list[str] = []
        for opt, opt_config in parent.options().items():
            if opt not in options or not options[opt].inherited:
                continue
            options[opt] = dataclasses.replace(
                opt_config,
                # Keep inherited and group config
                inherited=True,
                group=options[opt].group or opt_config.group,
            )
            inherited.append(opt)

        return inherited

    @t.final
    def subcommands(self) -> dict[str | None, type[Command] | None]:
        return getattr(self, CLYPI_SUBCOMMANDS, None) or {None: None}

    @t.final
    def options(self) -> dict[str, Config[t.Any]]:
        return getattr(self, CLYPI_OPTIONS, {})

    @t.final
    def positionals(self) -> dict[str, Config[t.Any]]:
        return getattr(self, CLYPI_POSITIONALS, {})

    @t.final
    def field_names(self) -> list[str]:
        return getattr(self, CLYPI_IN_ORDER_FIELD_NAMES, [])

    @t.final
    def get_field_conf(self, name: str) -> Config[t.Any]:
        """
        Helper function to find a field config with a given name. We need this
        since we store the args in different dicts yet we want to iterate through
        them in order to parse them how the user specified.
        """
        if conf := self.positionals().get(name):
            return conf
        if conf := self.options().get(name):
            return conf
        raise ValueError(f"Unknown field {name}")


@t.dataclass_transform()
class Command(metaclass=_CommandMeta):
    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        """
        Implementation of the init function for Commands. Similar to
        dataclasses, we only check for the field's existence and for the
        order the fields are provided in, but we do not check the data type
        for the actual provided values due to complication of checking types
        from type hints to real variables.
        """
        fields: dict[str, t.Any] = {}

        # Reversed so that we can `.pop()` in order
        field_names = list(reversed(self.__class__.field_names()))
        arg_ls = list(reversed(args))

        # From *args
        while arg_ls:
            fields[field_names.pop()] = arg_ls.pop()

        # From *kwargs
        for k, v in kwargs.items():
            if k in fields:
                raise TypeError(
                    f"Found duplicate field {k} for {self.__class__.__name__}"
                )
            if k not in field_names:
                raise TypeError(f"Invalid argument {k} for {self.__class__.__name__}")

            fields[k] = v
            field_names.remove(k)

        # Validate all fields and populate defaults
        validated = self._validate_fields(fields, name=self.__class__.__name__)

        # Save all fields to current instance
        for k, v in validated.items():
            setattr(self, k, v)

    @classmethod
    def _validate_fields(cls, fields: dict[str, t.Any], name: str) -> dict[str, t.Any]:
        """
        Takes in a dictionary of field names and values, checks if the fields are all
        part of the current Command class, and populates default fields. Raises if any
        field is missing or not a valid one.
        """

        field_map: dict[str, t.Any] = {}

        # Reversed so that we can `.pop()` in order
        field_names = set(cls.field_names())

        # From *kwargs
        for field, value in fields.items():
            if field not in field_names:
                raise TypeError(f"Invalid argument {field} for {name!r}")

            field_map[field] = value
            field_names.remove(field)

        # Check if subcommand is missing
        if "subcommand" in field_names:
            # If command is optional, set it to None
            if None in cls.subcommands():
                field_names.remove("subcommand")
                field_map["subcommand"] = None
            else:
                raise TypeError(f"Missing required subcommand for {name!r}")

        # Set defaults for any other missing fields
        missing_field_names: list[str] = []
        for field in field_names:
            conf = cls.get_field_conf(field)
            if conf.has_default():
                field_map[field] = conf.get_default()
            else:
                missing_field_names.append(field)

        # The user did not provide all of the necessary fields
        if missing_field_names:
            raise TypeError(
                f"Missing required arguments {', '.join(missing_field_names)} for {name!r}"
            )

        return field_map

    @classmethod
    def prog(cls) -> str:
        """
        The name of the command being executed. E.g.: install
        """
        return _camel_to_dashed(cls.__name__)

    @t.final
    @classmethod
    def full_command(cls) -> list[str]:
        """
        The full path to the current command being ran. E.g.: pip install
        """
        return cls.parents() + [cls.prog()]

    @classmethod
    def epilog(cls) -> str | None:
        """
        Optionally define text to display after the help message
        """
        return None

    @classmethod
    def parents(cls) -> list[str]:
        """
        A list of parent commands for this command. E.g.: pip
        """
        return getattr(cls, CLYPI_PARENTS, [])

    @t.final
    @classmethod
    def help(cls):
        """
        A brief description for the command
        """
        doc = inspect.getdoc(cls) or ""
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
    def _next_positional(cls, kwargs: dict[str, t.Any]) -> Config[t.Any] | None:
        """
        Traverse the current collected arguments and find the next positional
        arg we can assign to.
        """
        for name, pos in cls.positionals().items():
            # List positionals are a catch-all
            if _type_util.is_list(pos.arg_type):
                return pos

            if name not in kwargs:
                return pos

        return None

    @t.final
    @classmethod
    def _get_long_name(cls, short: str) -> str | None:
        for field, field_conf in cls.options().items():
            if field_conf.short == short:
                return field
        return None

    @t.final
    @classmethod
    def get_similar_arg_error(cls, arg: arg_parser.Arg) -> ValueError:
        """
        Utility function to find arguments similar to the one the
        user passed in to correct typos.
        """
        similar = None

        if arg.is_pos():
            all_pos: list[str] = [
                *[s for s in cls.subcommands() if s],
                *list(cls.positionals()),
            ]
            pos, dist = closest(arg.value, all_pos)
            # 2 is ~good for typos (e.g.: this -> that)
            if dist <= 2:
                similar = pos
        else:
            all_pos: list[str] = [
                *list(cls.options()),
                *[o.short for o in cls.options().values() if o.short],
            ]
            pos, dist = closest(arg.value, all_pos)
            # 2 is ~good for typos (e.g.: this -> that)
            if dist <= 2:
                similar = f"--{pos}" if len(pos) > 1 else f"-{pos}"

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
        except parsers.CATCH_ERRORS as e:
            if not get_config().help_on_fail:
                raise

            # The user might have started typing a subcommand but not
            # finished it so we cannot fully parse it, but we can recommend
            # the current command's args to autocomplete it
            if autocomplete.get_autocomplete_args() is not None:
                autocomplete.list_arguments(cls)

            # Otherwise, help page
            cls.print_help(exception=e)

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
        subcommand whilst we assign all inherited types.
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

        # If the user is trying to display the help page we can skip some parts
        requested_help = sys.argv[-1].lower() in HELP_ARGS

        # Parse the cmd line arguments
        for a in args:
            parsed = arg_parser.parse_as_attr(a)

            # If we've reached -h or --help
            if parsed.orig.lower() in HELP_ARGS:
                cls.print_help()

            # Try to parse as a subcommand
            if parsed.is_pos() and parsed.value in cls.subcommands():
                subcommand = cls.subcommands()[parsed.value]
                break

            # ---- Try to set to the current option ----
            is_valid_long = parsed.is_long_opt() and parsed.value in cls.options()
            is_valid_short = parsed.is_short_opt() and cls._get_long_name(parsed.value)
            if parsed.is_opt() and not (is_valid_long or is_valid_short):
                raise cls.get_similar_arg_error(parsed)

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

            # Try to assign to the current positional
            if not current_attr.name and (pos := cls._next_positional(unparsed)):
                current_attr = CurrentCtx(pos.name, pos.nargs, pos.nargs)

            # Try to assign to the current ctx
            if current_attr.name and current_attr.has_more():
                current_attr.collect(parsed.value)
                if not current_attr.has_more():
                    flush_ctx()
                continue

            raise cls.get_similar_arg_error(parsed)

        # Flush the context after the loop in case anything is left uncollected
        flush_ctx()

        # If the user requested help, skip prompting/parsing
        parsed_kwargs: dict[str, t.Any] = {}
        if not requested_help:
            # --- Parse as the correct values ---
            for field in cls.field_names():
                if field == "subcommand":
                    continue
                field_conf = cls.get_field_conf(field)

                # If the field was provided through args
                if field in unparsed:
                    parsed_kwargs[field] = field_conf.parser(unparsed[field])

                # If the field comes from a parent command, use that
                elif field_conf.inherited and field in parent_attrs:
                    parsed_kwargs[field] = parent_attrs[field]

                # If the field was not provided but we can defer prompting for the
                # value, we instead set it to a DeferrableValue
                elif field_conf.prompt is not None and field_conf.defer:
                    parsed_kwargs[field] = DeferredValue(
                        prompt=field_conf.prompt,
                        parser=field_conf.parser,
                        default=field_conf.default,
                        default_factory=field_conf.default_factory,
                        hide_input=field_conf.hide_input,
                        max_attempts=field_conf.max_attempts,
                    )

                # If the field was not provided but we can prompt, do so
                elif field_conf.prompt is not None:
                    parsed_kwargs[field] = prompt(
                        field_conf.prompt,
                        default=field_conf.default,
                        default_factory=field_conf.default_factory,
                        hide_input=field_conf.hide_input,
                        max_attempts=field_conf.max_attempts,
                        parser=field_conf.parser,
                    )

                # Otherwise, if the field has a default, use that
                elif field_conf.has_default():
                    parsed_kwargs[field] = field_conf.get_default()

        # Parse the subcommand passing in the parsed types
        if subcommand:
            # Configure parenthood and inherited args
            inherited_fields = subcommand.inherit(cls)

            # Parse the subcommand
            subcmd_instance = subcommand._safe_parse(args, parent_attrs=parsed_kwargs)
            parsed_kwargs["subcommand"] = subcmd_instance

            # If any fields were inherited by the subcommand and populated there,
            # get the same value for this instance
            for inh_field in inherited_fields:
                parsed_kwargs[inh_field] = getattr(subcmd_instance, inh_field)

        # Initialize the instance
        validated = cls._validate_fields(parsed_kwargs, name=cls.prog())
        return cls(**validated)

    @t.final
    @classmethod
    def parse(cls, args: t.Sequence[str] | None = None) -> t.Self:
        """
        Entry point of the program. Depending on some env vars it
        will either run the user-defined program or instead output the necessary
        completions for shells to provide autocomplete
        """
        args = args if args is not None else sys.argv[1:]
        if autocomplete.requested_autocomplete_install(args):
            autocomplete.install_autocomplete(cls)

        # If this is an autocomplete call, we need the args from the env var passed in
        # by the shell's complete function
        if auto_args := autocomplete.get_autocomplete_args():
            args = auto_args

        norm_args = arg_parser.normalize_args(args)
        args_iter = iter(norm_args)
        instance = cls._safe_parse(args_iter)
        if autocomplete.get_autocomplete_args() is not None:
            autocomplete.list_arguments(cls)
        if list(args_iter):
            raise ValueError(f"Unknown arguments {list(args_iter)}")

        return instance

    @classmethod
    def print_help(cls, exception: Exception | None = None) -> t.NoReturn:
        help_str = get_config().help_formatter.format_help(
            full_command=cls.full_command(),
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
