import typing as t
from dataclasses import dataclass, field

from clypi._colors import ColorType, style


class ClypiException(Exception):
    pass


class ClypiExceptionGroup(ExceptionGroup):
    pass


class MaxAttemptsException(ClypiException):
    pass


class AbortException(ClypiException):
    pass


@dataclass
class TreeExcNode:
    exc: BaseException
    children: list[t.Self] = field(default_factory=list)


def _build_exc_tree(err: BaseException) -> TreeExcNode:
    root = TreeExcNode(err)

    # Add __cause__ levels
    if err.__cause__ is not None:
        root.children.append(_build_exc_tree(err.__cause__))

    # Add exception group levels
    if isinstance(err, ExceptionGroup):
        for sub_exc in err.exceptions:
            root.children.append(_build_exc_tree(sub_exc))

    return root


def format_traceback(err: BaseException, color: ColorType | None = "red") -> list[str]:
    def _format_exc(e: BaseException, indent: int):
        msg, *_ = e.args
        icon = "  " * (indent - 1) + " ↳ " if indent != 0 else ""
        return style(f"{icon}{str(msg)}", fg=color)

    def _print_level(tree: TreeExcNode, indent: int) -> list[str]:
        ret: list[str] = []
        for child_node in tree.children:
            ret.append(_format_exc(child_node.exc, indent))
            ret.extend(_print_level(child_node, indent=indent + 1))
        return ret

    tree = _build_exc_tree(err)
    lines = [_format_exc(tree.exc, indent=0)]
    lines.extend(_print_level(tree, indent=1))
    return lines


def print_traceback(err: BaseException) -> None:
    for line in format_traceback(err):
        print(line)


def flatten_exc(err: Exception) -> list[Exception]:
    if not isinstance(err, ExceptionGroup):
        return [err]

    result: list[Exception] = []
    for sub_err in err.exceptions:
        result.extend(flatten_exc(sub_err))
    return result
