from clypi import separator


def test_default_separator():
    assert separator(width=20) == "━" * 20


def test_separator_with_title():
    expected = "━" * 19 + " Test " + "━" * 20
    assert separator(width=45, title="Test") == expected
