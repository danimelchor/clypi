import re
import typing as t
from dataclasses import dataclass

_COMPRESSED_ARG = re.compile(r"^-[a-zA-Z]{2,}$")
_SHORT_ARG = re.compile(r"^-[a-zA-Z]$")
_LONG_ARG = re.compile(r"^--[a-zA-Z][a-zA-Z0-9\-\_]+$")


def dash_to_snake(s: str) -> str:
    return re.sub(r"^-+", "", s).replace("-", "_")


def snake_to_dash(s: str) -> str:
    return s.replace("_", "-")


def normalize_args(args: t.Sequence[str]) -> list[str]:
    new_args: list[str] = []
    dd_index = args.index("--") if "--" in args else len(args)
    for a in args[:dd_index]:
        # Expand -a=1 or --a=1 into --a 1
        if a.startswith("-") and "=" in a:
            new_args.extend(a.split("=", 1))

        # Expand -abc into -a -b -c
        elif _COMPRESSED_ARG.match(a):
            new_args.extend(f"-{arg}" for arg in a[1:])

        # Leave as is
        else:
            new_args.append(a)
    new_args.extend(args[dd_index:])
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
    if _LONG_ARG.match(arg):
        return Arg(value=dash_to_snake(arg), orig=arg, arg_type="long-opt")

    if _SHORT_ARG.match(arg):
        return Arg(value=dash_to_snake(arg), orig=arg, arg_type="short-opt")

    return Arg(value=arg, orig=arg, arg_type="pos")
