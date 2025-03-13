from dataclasses import dataclass, field

from clypi._cli.formatter import ClypiFormatter, Formatter
from clypi.colors import Styler
from clypi.exceptions import (
    ClypiException,
)
from clypi.wraps import OverflowStyle


@dataclass
class Theme:
    usage: Styler = field(default_factory=lambda: Styler(fg="yellow"))
    prog: Styler = field(default_factory=lambda: Styler(bold=True))
    prog_args: Styler = field(default_factory=lambda: Styler())
    section_title: Styler = field(default_factory=lambda: Styler())

    # Subcommands
    subcommand: Styler = field(default_factory=lambda: Styler(fg="blue", bold=True))

    # Options
    long_option: Styler = field(default_factory=lambda: Styler(fg="blue", bold=True))
    short_option: Styler = field(default_factory=lambda: Styler(fg="green", bold=True))

    # Positionals
    positional: Styler = field(default_factory=lambda: Styler(fg="blue", bold=True))

    placeholder: Styler = field(default_factory=lambda: Styler(fg="blue"))
    type_str: Styler = field(default_factory=lambda: Styler(fg="yellow", bold=True))
    prompts: Styler = field(default_factory=lambda: Styler(fg="blue", bold=True))


@dataclass
class ClypiConfig:
    theme: Theme = field(default_factory=Theme)
    help_formatter: Formatter = field(default_factory=ClypiFormatter)
    help_on_fail: bool = True
    nice_errors: tuple[type[Exception]] = field(
        default_factory=lambda: (ClypiException,)
    )
    overflow_style: OverflowStyle = "wrap"


_config = ClypiConfig()


def configure(config: ClypiConfig):
    global _config
    _config = config


def get_config() -> ClypiConfig:
    return _config
