from __future__ import annotations

import random

import clypi
from clypi.colors import ALL_COLORS


def main() -> None:
    for box in clypi.Boxes:
        color = random.choice(ALL_COLORS)
        content = f"This is a {box.human_name()!r} {color} box!"
        print(clypi.boxed(content, style=box, color=color))


if __name__ == "__main__":
    main()
