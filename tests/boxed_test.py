from textwrap import dedent

from clypi import boxed


def test_boxed():
    result = boxed("a" * 16, width=20)
    expected = dedent(
        """
        ┏━━━━━━━━━━━━━━━━━━┓
        ┃ aaaaaaaaaaaaaaaa ┃
        ┗━━━━━━━━━━━━━━━━━━┛
        """
    )
    assert result == expected.strip()


def test_boxed_with_wrapping():
    result = boxed("a" * 40, width=20)
    expected = dedent(
        """
        ┏━━━━━━━━━━━━━━━━━━┓
        ┃ aaaaaaaaaaaaaaaa ┃
        ┃ aaaaaaaaaaaaaaaa ┃
        ┃ aaaaaaaa         ┃
        ┗━━━━━━━━━━━━━━━━━━┛
        """
    )
    assert result == expected.strip()
