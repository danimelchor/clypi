def indented(lines: list[str], prefix: str = "  ") -> list[str]:
    return [prefix + s for s in lines]
