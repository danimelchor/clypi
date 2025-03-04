import typing as t
from importlib import import_module

if t.TYPE_CHECKING:
    from clypi.align import AlignType, align
    from clypi.boxed import boxed
    from clypi.cli import Command, config
    from clypi.colors import print, style, styler
    from clypi.prompts import prompt
    from clypi.spinner import Spinner
    from clypi.stack import stack

__all__ = (
    "AlignType",
    "Command",
    "Spinner",
    "align",
    "boxed",
    "config",
    "print",
    "prompt",
    "stack",
    "style",
    "styler",
)

_dynamic_imports: dict[str, tuple[str, str]] = {
    "Command": (__spec__.parent, ".cli"),
    "Spinner": (__spec__.parent, ".spinner"),
    "boxed": (__spec__.parent, ".boxed"),
    "config": (__spec__.parent, ".cli"),
    "print": (__spec__.parent, ".colors"),
    "prompt": (__spec__.parent, ".prompts"),
    "stack": (__spec__.parent, ".stack"),
    "style": (__spec__.parent, ".colors"),
    "styler": (__spec__.parent, ".colors"),
    "align": (__spec__.parent, ".align"),
    "AlignType": (__spec__.parent, ".align"),
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
