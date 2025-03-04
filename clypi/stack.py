from typing import overload

from clypi.colors import remove_style


def _safe_get(ls: list[str], idx: int) -> str:
    if idx >= len(ls):
        return ""
    return ls[idx]


def _real_len(s: str) -> int:
    s = remove_style(s)
    return len(s)


@overload
def stack(*blocks: list[str], padding: int = 1, lines: bool) -> list[str]: ...


@overload
def stack(*blocks: list[str], padding: int = 1) -> str: ...


def stack(*blocks: list[str], padding: int = 1, lines: bool = False) -> str | list[str]:
    new_lines = []
    height = max(len(b) for b in blocks)
    widths = [max(_real_len(line) for line in block) for block in blocks]

    # Process line until all blocks are done
    for idx in range(height):
        more = False
        tmp: list[str] = []

        # Add the line from each block
        for block, width in zip(blocks, widths):
            # If there was a line, next iter will happen
            block_line = _safe_get(block, idx)
            if block_line:
                more |= True

            # How much do we need to reach the actual visible length
            actual_width = (width - _real_len(block_line)) + len(block_line)

            # Align and append line
            tmp.append(block_line.ljust(actual_width))
            tmp.append(" " * padding)

        new_lines.append(" ".join(tmp))

        # Exit if no more lines in any iter
        if not more:
            break

    return new_lines if lines else "\n".join(new_lines)
