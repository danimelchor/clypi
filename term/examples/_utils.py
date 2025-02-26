from term.colors import remove_style


def _safe_get(ls: list[str], idx: int) -> str:
    if idx >= len(ls):
        return ""
    return ls[idx]


def _real_len(s: str) -> int:
    s = remove_style(s)
    return len(s)


def assemble(*blocks: list[str], padding: int = 1) -> list[str]:
    new_lines = []
    height = max(len(b) for b in blocks)
    widths = [max(_real_len(line) for line in block) for block in blocks]

    for line in range(height):
        tmp: list[str] = []
        for block, width in zip(blocks, widths):
            block_line = _safe_get(block, line)
            tmp.append(block_line.ljust(width))
            tmp.append(" " * padding)
        new_lines.append(" ".join(tmp))

    return new_lines
