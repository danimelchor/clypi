from __future__ import annotations

import typing as t
from getpass import getpass

import clypi
from clypi._cli import parser
from clypi._util import UNSET, Unset
from clypi.configuration import get_config
from clypi.exceptions import AbortException, MaxAttemptsException

MAX_ATTEMPTS: int = 20


def _error(msg: str):
    clypi.print(msg, fg="red")


def _input(
    prompt: str,
    default: T | Unset = UNSET,
    hide_input: bool = False,
) -> str | T | Unset:
    fun = getpass if hide_input else input
    styled_prompt = get_config().theme.prompts(prompt)
    res = fun(styled_prompt)
    if res:
        return res
    return default


def _display_default(default: t.Any) -> str:
    if isinstance(default, bool):
        return "Y/n" if default else "y/N"
    return f"{default}"


def _build_prompt(text: str, default: t.Any) -> str:
    prompt = text
    if default is not UNSET:
        prompt += f" [{_display_default(default)}]"
    prompt += ": "
    return prompt


def confirm(
    text: str,
    *,
    default: bool | Unset = UNSET,
    max_attempts: int = MAX_ATTEMPTS,
    abort: bool = False,
) -> bool:
    """
    Prompt the user for a yes/no value

    :param text: The prompt text.
    :param default: The default value.
    :param max_attempts: The maximum number of attempts to get a valid value.
    :return: The parsed value.
    """
    parsed_inp = prompt(
        text=text,
        default=default,
        max_attempts=max_attempts,
        parser=parser.from_type(bool),
    )
    if abort and not parsed_inp:
        raise AbortException()
    return parsed_inp


T = t.TypeVar("T")

Parser: t.TypeAlias = t.Callable[[t.Any], T]


@t.overload
def prompt(
    text: str,
    *,
    default: str | Unset = UNSET,
    hide_input: bool = False,
    max_attempts: int = MAX_ATTEMPTS,
) -> str: ...


@t.overload
def prompt(
    text: str,
    *,
    parser: Parser[T] | type[T],
    default: T | Unset = UNSET,
    hide_input: bool = False,
    max_attempts: int = MAX_ATTEMPTS,
) -> T: ...


def prompt(
    text: str,
    *,
    parser: Parser[T] | type[T] | type[str] = str,
    default: T | Unset = UNSET,
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
    prompt = _build_prompt(text, default)

    # Loop until we get a valid value
    for _ in range(max_attempts):
        inp = _input(prompt, default=default, hide_input=hide_input)
        if inp is UNSET:
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
