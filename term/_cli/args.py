import typing as t
from dataclasses import dataclass

from term._cli import tokens as tk


@dataclass
class Option:
    name: str
    value: str


@dataclass
class Flag:
    name: str


@dataclass
class Positional:
    value: str


ParsedArgs: t.TypeAlias = Option | Flag | Positional


def parse_args(args: list[str] | None = None) -> t.Generator[ParsedArgs, None, None]:
    tokens = tk.parse_tokens(args)
    while tokens:
        match tokens:
            case [tk.Opt(opt), tk.Arg(value), *_] | [
                tk.ShortOpt(opt),
                tk.Arg(value),
                *_,
            ]:
                yield Option(opt, value)
                tokens = tokens[2:]
            case [tk.Opt(opt), *_] | [tk.ShortOpt(opt), *_]:
                yield Flag(opt)
                tokens = tokens[1:]
            case [tk.Arg(value), *_]:
                yield Positional(value)
                tokens = tokens[1:]


if __name__ == "__main__":
    print(list(parse_args()))
