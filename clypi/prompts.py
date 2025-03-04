from __future__ import annotations

import typing as t
from getpass import getpass

import clypi
from clypi._util import _UNSET, Unset

MAX_ATTEMPTS: int = 20


def _error(msg: str):
    clypi.print(msg, fg="red")


def _input(prompt: str, hide_input: bool) -> str:
    fun = getpass if hide_input else input
    return fun(clypi.style(prompt, fg="blue", bold=True))


class MaxAttemptsException(Exception):
    pass


T = t.TypeVar("T")

Parser: t.TypeAlias = t.Callable[[t.Any], T]


@t.overload
def prompt(
    text: str,
    *,
    default: str | Unset = _UNSET,
    hide_input: bool = False,
    max_attempts: int = MAX_ATTEMPTS,
) -> str: ...


@t.overload
def prompt(
    text: str,
    *,
    parser: type[T],
    default: T | Unset = _UNSET,
    hide_input: bool = False,
    max_attempts: int = MAX_ATTEMPTS,
) -> T: ...


@t.overload
def prompt(
    text: str,
    *,
    parser: Parser[T],
    default: T | Unset = _UNSET,
    hide_input: bool = False,
    max_attempts: int = MAX_ATTEMPTS,
) -> T: ...


def prompt(
    text: str,
    *,
    parser: Parser[T] | type[T] | type[str] = str,
    default: T | Unset = _UNSET,
    hide_input: bool = False,
    max_attempts: int = MAX_ATTEMPTS,
) -> T:
    """
    Prompt the user for a value.

    :param text: The prompt text.
    :param default: The default value.
    :param parser: The parser function parse the input with.
    :param max_attempts: The maximum number of attempts to get a valid value.
    :return: The parsed value.
    """

    # Build the prompt
    prompt = text
    if default is not _UNSET:
        prompt += f" [{default}]"
    prompt += ": "

    # Loop until we get a valid value
    for _ in range(max_attempts):
        inp = _input(prompt, hide_input=hide_input)

        # User hit enter without a value
        if inp == "":
            if default is not _UNSET:
                return default
            _error("A value is required.")
            continue

        # User answered the prompt -- Parse
        try:
            if t.TYPE_CHECKING:
                parser = t.cast(Parser[T], parser)
            parsed_inp = parser(inp)
        except (ValueError, TypeError) as e:
            _error(f"Unable to parse {inp!r}, please provide a valid value.\n  ↳  {e}")
            continue

        return parsed_inp

    raise MaxAttemptsException(
        f"Failed to get a valid value after {max_attempts} attempts."
    )
