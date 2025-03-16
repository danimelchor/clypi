from typing import overload

from clypi._components.wraps import wrap
from clypi._util import get_term_width, visible_width


def _safe_get(ls: list[str], idx: int) -> str:
    if idx >= len(ls):
        return ""
    return ls[idx]


@overload
def stack(
    *blocks: list[str],
    max_width: int | None = None,
    padding: int = 2,
    lines: bool,
) -> list[str]: ...


@overload
def stack(
    *blocks: list[str],
    max_width: int | None = None,
    padding: int = 2,
) -> str: ...


def stack(
    *blocks: list[str],
    max_width: int | None = None,
    padding: int = 2,
    lines: bool = False,
) -> str | list[str]:
    max_width = max_width or get_term_width()
    padding_str = " " * padding

    new_lines: list[str] = []
    height = max(len(b) for b in blocks)
    width_per_block = [max(visible_width(line) for line in block) for block in blocks]

    # Process line until all blocks are done
    for idx in range(height):
        more = False
        tmp: list[str] = []

        # Add the line from each block into combined line
        for block, block_width in zip(blocks, width_per_block):
            # If there was a line, next iter will happen
            block_line = _safe_get(block, idx)
            if block_line:
                more |= True

            # How much do we need to reach the actual visible length
            actual_width = (block_width - visible_width(block_line)) + len(block_line)

            # Align and append line
            tmp.append(block_line.ljust(actual_width))

        # Check if combined line would overflow and wrap if needed
        combined_line = padding_str.join(tmp).rstrip()
        if visible_width(combined_line) <= max_width:
            new_lines.append(combined_line)
        else:
            # We need to wrap the last block and the remainder needs to be aligned
            # with the start of the second block
            width_without_last = visible_width(padding_str.join(tmp[:-1]) + padding_str)
            max_last_width = max_width - width_without_last
            wrapped_last = wrap(tmp[-1], max_last_width)

            # Add the combined line
            combined_line = padding_str.join(tmp[:-1] + [wrapped_last[0]]).rstrip()
            new_lines.append(combined_line)

            # Add the remainder aligned to the start of second block
            padding_left = " " * width_without_last
            for remaining_line in wrapped_last[1:]:
                new_lines.append(padding_left + remaining_line)

        # Exit if no more lines in any iter
        if not more:
            break

    return new_lines if lines else "\n".join(new_lines)
