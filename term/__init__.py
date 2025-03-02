import typing as t
from importlib import import_module

if t.TYPE_CHECKING:
    from term.boxed import boxed
    from term.colors import print, style, styler
    from term.prompts import prompt
    from term.spinner import Spinner
    from term.stack import stack

__all__ = (
    "Spinner",
    "boxed",
    "stack",
    "print",
    "prompt",
    "style",
    "styler",
)

_dynamic_imports: dict[str, tuple[str, str]] = {
    "Spinner": (__spec__.parent, ".spinner"),
    "print": (__spec__.parent, ".colors"),
    "prompt": (__spec__.parent, ".prompts"),
    "style": (__spec__.parent, ".colors"),
    "styler": (__spec__.parent, ".colors"),
    "boxed": (__spec__.parent, ".boxed"),
    "stack": (__spec__.parent, ".stack"),
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
