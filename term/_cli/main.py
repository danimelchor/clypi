from __future__ import annotations

import inspect
import logging
import typing as t
from dataclasses import MISSING
from types import NoneType, UnionType

from term._cli import args as a

logger = logging.getLogger(__name__)


def _get_subcmd_from_type(_type: t.Any) -> type[Command] | None:
    if isinstance(_type, UnionType):
        for tp in _type.__args__:
            if ret := _get_subcmd_from_type(tp):
                return ret
        return None

    if inspect.isclass(_type) and issubclass(_type, Command):
        return _type

    return None


def _is_type_nullable(_type: t.Any) -> bool:
    if isinstance(_type, UnionType):
        for tp in _type.__args__:
            if _is_type_nullable(tp):
                return True
        return False

    return _type is NoneType


class Command:
    @classmethod
    def _annotations(cls):
        return inspect.get_annotations(cls)

    @classmethod
    def _type_for_name(cls, name: str):
        if name not in cls._annotations():
            raise ValueError(f"{cls.__name__} has no value {name}")

        return cls._annotations()[name]

    @classmethod
    def _try_positional(cls, value: str):
        return value

    @classmethod
    def _try_option(cls, name: str, value: str):
        _type = cls._type_for_name(name)
        print(_type, value)
        return value

    @classmethod
    def _try_flag(cls, name: str):
        _type = cls._type_for_name(name)
        if _type is not bool:
            raise ValueError(f"{cls.__name__} has no boolean attribute {name}")
        return True

    @classmethod
    def _get_subcommand(cls, value: str) -> type[Command] | None:
        _type = cls._type_for_name("subcommand")
        assert isinstance(_type, UnionType)
        for subcmd in _type.__args__:
            if subcmd.__name__.lower() == value:
                return subcmd

        raise ValueError(f"Invalid subcommand {value} does not exist")

    @classmethod
    def _get_optional_value(cls, name: str) -> t.Any:
        _type = cls._type_for_name(name)

        # Use dataclass default value
        if dataclass_default := getattr(cls, "__dataclass_fields__", None):
            if (df := dataclass_default[name].default_factory) and df is not MISSING:
                return df()

        # Boolean fields set to False
        if _type is bool:
            return False

        # None-able fields set to None
        if _is_type_nullable(_type):
            return None

        raise ValueError(f"Missing non-optional argument {name} for {cls.__name__}")

    @classmethod
    def _validate_kwargs(cls, kwargs: dict[str, t.Any]):
        for name in cls._annotations():
            if name not in kwargs:
                kwargs[name] = cls._get_optional_value(name)

    @classmethod
    def _parse(cls, args: t.Iterator[a.ParsedArgs]) -> t.Self:
        kwargs = {}
        for arg in args:
            match arg:
                case a.Option(name, value):
                    cls.debug(f"Attempting to parse option {name=} {value=}")
                    kwargs[name] = cls._try_option(name, value)
                case a.Flag(name):
                    cls.debug(f"Attempting to parse flag {name=}")
                    kwargs[name] = cls._try_flag(name)
                case a.Positional(value):
                    if subcmd := cls._get_subcommand(value):
                        cls.debug(f"Attempting to parse subcommand {value=}")
                        kwargs["subcommand"] = subcmd._parse(args)
                    else:
                        cls.debug(f"Attempting to parse positional {value=}")
                        kwargs[value] = cls._try_positional(value)

        cls._validate_kwargs(kwargs)

        cls.debug(f"Attempting to instantiate with {kwargs=}")
        return cls(**kwargs)

    @classmethod
    def parse(cls) -> t.Self:
        args_iter = a.parse_args()
        return cls._parse(args_iter)

    @classmethod
    def debug(cls, msg: str):
        logger.debug(f"[{cls.__name__}] {msg}")
