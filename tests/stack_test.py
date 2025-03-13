from clypi import stack


def test_one_line_stack():
    result = stack(["a" * 10], ["b" * 10])
    expected = "aaaaaaaaaa  bbbbbbbbbb"
    assert result == expected.strip()


def test_two_line_stack():
    result = stack(["a", "a" * 10], ["b" * 10, "b"], lines=True)
    expected = [
        "a           bbbbbbbbbb",
        "aaaaaaaaaa  b",
    ]
    assert result == expected


def test_overflowing_line_stack():
    result = stack(["a", "a"], ["b" * 12, "b" * 10], max_width=13, lines=True)
    expected = [
        "a  bbbbbbbbbb",
        "   bb",
        "a  bbbbbbbbbb",
    ]
    assert result == expected
