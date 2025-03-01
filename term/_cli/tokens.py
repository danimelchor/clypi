import sys
import typing as t
from dataclasses import dataclass


@dataclass
class Arg:
    value: str


@dataclass
class Opt:
    name: str


@dataclass
class ShortOpt:
    name: str


Token: t.TypeAlias = Arg | Opt | ShortOpt


def parse_token(a: str) -> tuple[Token, ...]:
    if a.startswith("--"):
        parts = a.split("=", 1)
        if len(parts) == 2:
            return Opt(parts[0].removeprefix("--")), Arg(parts[1])
        else:
            return (Opt(parts[0].removeprefix("--")),)
    if a.startswith("-"):
        parts = a.split("=", 1)
        if len(parts) == 2:
            return ShortOpt(parts[0].removeprefix("-")), Arg(parts[1])
        else:
            return (ShortOpt(parts[0].removeprefix("-")),)

    return (Arg(a),)


def parse_tokens(args: list[str] | None = None) -> list[Token]:
    args = sys.argv[1:] if args is None else args

    tokens: list[Token] = []
    for a in args:
        tokens.extend(parse_token(a))
    return tokens


if __name__ == "__main__":
    print(parse_tokens())
