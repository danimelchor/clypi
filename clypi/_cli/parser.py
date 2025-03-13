import re
import typing as t
from dataclasses import dataclass


def dash_to_snake(s: str) -> str:
    return re.sub(r"^-+", "", s).replace("-", "_")


def snake_to_dash(s: str) -> str:
    return s.replace("_", "-")


def normalize_args(args: t.Sequence[str]) -> list[str]:
    new_args: list[str] = []
    for a in args:
        if a.startswith("-") and "=" in a:
            new_args.extend(a.split("=", 1))
        else:
            new_args.append(a)
    return new_args


@dataclass
class Arg:
    value: str
    orig: str
    arg_type: t.Literal["long-opt", "short-opt", "pos"]

    def is_pos(self):
        return self.arg_type == "pos"

    def is_long_opt(self):
        return self.arg_type == "long-opt"

    def is_short_opt(self):
        return self.arg_type == "short-opt"

    def is_opt(self):
        return self.is_long_opt() or self.is_short_opt()


def parse_as_attr(arg: str) -> Arg:
    if arg.startswith("--"):
        return Arg(value=dash_to_snake(arg), orig=arg, arg_type="long-opt")

    if arg.startswith("-"):
        return Arg(value=dash_to_snake(arg), orig=arg, arg_type="short-opt")

    return Arg(value=arg, orig=arg, arg_type="pos")
