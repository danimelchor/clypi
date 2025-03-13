import typing as t
from importlib import import_module

if t.TYPE_CHECKING:
    from clypi import parsers
    from clypi.align import AlignType, align
    from clypi.boxed import Boxes, boxed
    from clypi.cli import ClypiFormatter, Command, Formatter, Positional, arg
    from clypi.colors import ALL_COLORS, Styler, print, style
    from clypi.configuration import ClypiConfig, Theme, configure, get_config
    from clypi.exceptions import (
        AbortException,
        ClypiException,
        MaxAttemptsException,
        format_traceback,
        print_traceback,
    )
    from clypi.indented import indented
    from clypi.parsers import Parser
    from clypi.prompts import (
        confirm,
        prompt,
    )
    from clypi.spinners import Spin, Spinner, spinner
    from clypi.stack import stack
    from clypi.wraps import OverflowStyle, wrap

__all__ = (
    "ALL_COLORS",
    "AbortException",
    "AlignType",
    "Boxes",
    "ClypiConfig",
    "ClypiException",
    "ClypiFormatter",
    "Command",
    "Formatter",
    "MaxAttemptsException",
    "OverflowStyle",
    "Parser",
    "parsers",
    "Positional",
    "Spin",
    "Spinner",
    "Styler",
    "Theme",
    "align",
    "arg",
    "boxed",
    "configure",
    "confirm",
    "format_traceback",
    "get_config",
    "indented",
    "print",
    "print_traceback",
    "prompt",
    "spinner",
    "stack",
    "style",
    "wrap",
)

_dynamic_imports: dict[str, tuple[str | None, str]] = {
    "ALL_COLORS": (__spec__.parent, ".colors"),
    "AbortException": (__spec__.parent, ".exceptions"),
    "AlignType": (__spec__.parent, ".align"),
    "Boxes": (__spec__.parent, ".boxed"),
    "ClypiConfig": (__spec__.parent, ".configuration"),
    "ClypiException": (__spec__.parent, ".exceptions"),
    "ClypiFormatter": (__spec__.parent, ".cli"),
    "Command": (__spec__.parent, ".cli"),
    "Formatter": (__spec__.parent, ".cli"),
    "MaxAttemptsException": (__spec__.parent, ".exceptions"),
    "OverflowStyle": (__spec__.parent, ".wraps"),
    "Parser": (__spec__.parent, ".parsers"),
    "parsers": (__spec__.parent, ".parsers"),
    "Positional": (__spec__.parent, ".cli"),
    "Spin": (__spec__.parent, ".spinners"),
    "Spinner": (__spec__.parent, ".spinners"),
    "Styler": (__spec__.parent, ".colors"),
    "Theme": (__spec__.parent, ".configuration"),
    "align": (__spec__.parent, ".align"),
    "arg": (__spec__.parent, ".cli"),
    "boxed": (__spec__.parent, ".boxed"),
    "configure": (__spec__.parent, ".configuration"),
    "confirm": (__spec__.parent, ".prompts"),
    "format_traceback": (__spec__.parent, ".exceptions"),
    "get_config": (__spec__.parent, ".configuration"),
    "indented": (__spec__.parent, ".indented"),
    "print": (__spec__.parent, ".colors"),
    "print_traceback": (__spec__.parent, ".exceptions"),
    "prompt": (__spec__.parent, ".prompts"),
    "spinner": (__spec__.parent, ".spinners"),
    "stack": (__spec__.parent, ".stack"),
    "style": (__spec__.parent, ".colors"),
    "wrap": (__spec__.parent, ".wraps"),
}


def __getattr__(attr: str) -> object:
    """
    Dynamically re-exports modules with lazy loading
    """

    dynamic_attr = _dynamic_imports.get(attr)
    if dynamic_attr is None:
        raise AttributeError(f"module {__name__!r} has no attribute {attr!r}")

    package, module_name = dynamic_attr

    # Import module and find the object
    module = import_module(module_name, package=package)
    result = getattr(module, attr)

    # Import everything else in that module
    g = globals()
    for k, (_, other) in _dynamic_imports.items():
        if other == module_name:
            g[k] = getattr(module, k)
    return result


def __dir__() -> list[str]:
    return list(__all__)
