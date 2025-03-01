import inspect
import sys
import typing as t
from dataclasses import dataclass

from term._cli import tokens

@dataclass
class Option:
    name: str
    value: str

@dataclass
class Flag:
    name: str

@dataclass
class Command:
    name: str


ParsedArgs: t.TypeAlias = Option | Flag | Command


def parse_opts(tokens: list[tokens.Token]) -> t.Generator[]:
    while tokens:
        match tokens:
            case [Opt(opt), Word(value), *_] | [ShortOpt(opt), Word(value), *_]:
                options[opt] = value
                tokens = tokens[2:]
            case [Opt(opt), *_] | [ShortOpt(opt), *_]:
                options[opt] = True
                tokens = tokens[1:]
            case [Word(value), *_]:
                if not options:
                    command.append(value)
                else:
                    positional.append(value)
                tokens = tokens[1:]

