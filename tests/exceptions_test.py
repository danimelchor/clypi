from textwrap import dedent

from clypi import format_traceback
from clypi._exceptions import ClypiExceptionGroup


def test_basic_traceback():
    root_cause = RuntimeError("Actual root cause")

    context = ValueError("Some context")
    context.__cause__ = root_cause

    err = ValueError("User facing error")
    err.__cause__ = context

    result = format_traceback(err, color=None)
    result_str = "\n".join(result)
    assert (
        result_str
        == dedent(
            """
            User facing error
             ↳ Some context
               ↳ Actual root cause
            """
        ).strip()
    )


def test_traceback_exc_group():
    context1 = ValueError("Failed to parse 'foo' as int()")
    context2 = ValueError("Failed to parse 'foo' as None")
    err = ClypiExceptionGroup("Failed to parse as int|none", [context1, context2])

    result = format_traceback(err, color=None)
    result_str = "\n".join(result)
    assert (
        result_str
        == dedent(
            """
            Failed to parse as int|none
             ↳ Failed to parse 'foo' as int()
             ↳ Failed to parse 'foo' as None
            """
        ).strip()
    )


def test_traceback_complex():
    root1 = ValueError("Invalid int literal for base 10 'foo'")
    context1 = ValueError("Failed to parse 'foo' as int()")
    context1.__cause__ = root1

    root2_1 = ValueError("Text 'foo' does not match 'none'")
    root2_2 = ValueError("Text 'foo' is not an empty list")
    context2 = ClypiExceptionGroup("Failed to parse 'foo' as None", [root2_1, root2_2])

    err = ClypiExceptionGroup("Failed to parse as int|none", [context1, context2])

    result = format_traceback(err, color=None)
    result_str = "\n".join(result)
    assert (
        result_str
        == dedent(
            """
            Failed to parse as int|none
             ↳ Failed to parse 'foo' as int()
               ↳ Invalid int literal for base 10 'foo'
             ↳ Failed to parse 'foo' as None
               ↳ Text 'foo' does not match 'none'
               ↳ Text 'foo' is not an empty list
            """
        ).strip()
    )
