from __future__ import annotations

import typing as t
from enum import Enum, auto

from term import colors
from term.klasses import (
    Bool,
    Date,
    DateTime,
    Float,
    Int,
    Klass,
    Str,
    TimeDelta,
    parse_klass,
)
from term.validations import (
    Validation,
    ValidationException,
    ValidationType,
    parse_validation,
)

# Needed to re-export
__all__ = [
    "Bool",
    "Date",
    "DateTime",
    "Float",
    "Int",
    "Klass",
    "MAX_ATTEMPTS",
    "MaxAttemptsException",
    "Str",
    "TimeDelta",
    "Validation",
    "ValidationException",
    "ValidationType",
    "prompt",
]


class Unset(Enum):
    TOKEN = auto()


_UNSET = Unset.TOKEN

MAX_ATTEMPTS: int = 20


def _error(msg: str):
    print(colors.fg.red(msg))


def _input(prompt: str) -> str:
    return input(colors.fg.blue(colors.style.bold(prompt)))


class MaxAttemptsException(Exception):
    pass


T = t.TypeVar("T")


def prompt(
    text: str,
    default: T | Unset = _UNSET,
    klass: t.Type[T] | Klass[T] = str,
    validate: ValidationType[T] | None = None,
    max_attempts: int = MAX_ATTEMPTS,
    provided: T | None = None,
) -> T:
    """
    Prompt the user for a value.

    :param text: The prompt text.
    :param default: The default value.
    :param klass: The class to parse the input as.
    :param validate: A function to validate the parsed value.
    :param max_attempts: The maximum number of attempts to get a valid value.
    :param provided: The value the user passed in as a command line argument.
    :return: The parsed value.
    """

    # If the value was provided as a command line argument, use that
    if provided is not None:
        return provided

    # Build the prompt
    prompt = text
    if default is not _UNSET:
        prompt += f" [{default}]"
    prompt += ": "

    # Loop until we get a valid value
    for _ in range(max_attempts):
        inp = _input(prompt)

        # User hit enter without a value
        if inp == "":
            if default is not _UNSET:
                return default
            _error("A value is required.")
            continue

        # User answered the prompt -- Parse
        try:
            parsed_inp = parse_klass(klass)(inp)
        except ValueError:
            _error(f"Unable to parse {inp} as {klass}, please provide a valid value.")
            continue

        # Validate the parsed value
        if validate is not None:
            try:
                parse_validation(validate)(parsed_inp)
            except ValidationException as e:
                _error(str(e))
                continue

        return parsed_inp

    raise MaxAttemptsException(
        f"Failed to get a valid value after {max_attempts} attempts."
    )
