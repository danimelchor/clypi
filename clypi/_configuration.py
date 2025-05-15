from dataclasses import dataclass, field

from clypi._cli.formatter import ClypiFormatter, Formatter
from clypi._colors import Styler
from clypi._components.wraps import OverflowStyle
from clypi._exceptions import (
    ClypiException,
    ClypiExceptionGroup,
)


@dataclass
class Theme:
    usage: Styler = field(default_factory=lambda: Styler(fg="yellow"))
    usage_command: Styler = field(default_factory=lambda: Styler(bold=True))
    usage_args: Styler = field(default_factory=lambda: Styler())
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
    # The theme sets Clypi's colors
    theme: Theme = field(default_factory=Theme)

    # What formatting class should we use?
    help_formatter: Formatter = field(default_factory=ClypiFormatter)

    # Should we display the help page if we are missing required args?
    help_on_fail: bool = True

    # What errors should we catch and neatly display?
    nice_errors: tuple[type[Exception], ...] = field(
        default_factory=lambda: (ClypiException, ClypiExceptionGroup)
    )

    # How should sentences overwrap if they're too long?
    overflow_style: OverflowStyle = "wrap"

    # Should we disable all color printing?
    disable_colors: bool = False

    # If we cannot get the terminal size, what should be the fallback?
    fallback_term_width: int = 100


_config = ClypiConfig()


def configure(config: ClypiConfig):
    global _config
    _config = config


def get_config() -> ClypiConfig:
    return _config
