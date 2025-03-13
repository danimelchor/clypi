from __future__ import annotations

import clypi
import clypi.parsers as cp
from clypi import colors


def _validate_earth_age(x: int) -> int:
    if x != 4_543_000_000:
        raise ValueError("The Earth is 4.543 billion years old. Try 4543000000.")
    return x


def main() -> None:
    # Basic prompting
    name = clypi.prompt("What's your name?")

    # Default values
    is_cool = clypi.confirm("Is clypi cool?", default=True)

    # Custom types with parsing
    age = clypi.prompt(
        "How old are you?",
        parser=int,
        hide_input=True,
    )
    hours = clypi.prompt(
        "How many hours are there in a day?",
        parser=cp.Union(cp.TimeDelta(), cp.Int()),
    )

    # Custom validations
    earth = clypi.prompt(
        "How old is The Earth?",
        parser=_validate_earth_age,
    )

    # -----------
    print()
    colors.print("🚀 Summary", bold=True, fg="green")
    answer = colors.Styler(fg="magenta", bold=True)
    print(" ↳  Name:", answer(name))
    print(" ↳  Clypi is cool:", answer(is_cool))
    print(" ↳  Age:", answer(age))
    print(" ↳  Hours in a day:", answer(hours), f"({type(hours).__name__})")
    print(" ↳  Earth age:", answer(earth))


if __name__ == "__main__":
    main()
