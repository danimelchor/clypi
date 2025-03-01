from typing import Iterable

from term.colors import remove_style


def _safe_get(ls: list[str], idx: int) -> str:
    if idx >= len(ls):
        return ""
    return ls[idx]


def _real_len(s: str) -> int:
    s = remove_style(s)
    return len(s)


def assemble(*blocks: Iterable[str], padding: int = 1) -> list[str]:
    new_lines = []
    blocks_ls = [list(b) for b in blocks]
    height = max(len(b) for b in blocks_ls)
    widths = [max(_real_len(line) for line in block) for block in blocks_ls]

    # Process line until all blocks are done
    for idx in range(height):
        more = False
        tmp: list[str] = []

        # Add the line from each block
        for block, width in zip(blocks_ls, widths):
            # If there was a line, next iter will happen
            block_line = _safe_get(block, idx)
            if block_line:
                more |= True

            # Align and append line
            tmp.append(block_line.ljust(width))
            tmp.append(" " * padding)
        new_lines.append(" ".join(tmp))

        # Exit if no more lines in any iter
        if not more:
            break

    return new_lines
