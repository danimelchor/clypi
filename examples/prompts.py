from __future__ import annotations

import v6e as v

import clypi
from clypi import colors


def _validate_earth_age(x: int) -> None:
    if x != 4_543_000_000:
        raise ValueError("The Earth is 4.543 billion years old. Try 4543000000.")


def main() -> None:
    # Basic prompting
    name = clypi.prompt("What's your name?")

    # Default values
    is_cool = clypi.prompt("Is Term cool?", default=True, parser=bool)

    # Custom types with parsing using v6e
    age = clypi.prompt(
        "How old are you?",
        parser=int,
        hide_input=True,
    )
    hours = clypi.prompt(
        "How many hours are there in a day?",
        parser=v.timedelta() | v.int(),
    )

    # Custom validations using v6e
    earth = clypi.prompt(
        "How old is The Earth?",
        parser=v.int().custom(_validate_earth_age),
    )
    moon = clypi.prompt(
        "How old is The Moon?",
        parser=v.int().gte(3).lte(9).multiple_of(3),  # You can chain validations
    )

    # -----------
    print()
    colors.print("🚀 Summary", bold=True, fg="green")
    answer = colors.styler(fg="magenta", bold=True)
    print(" ↳  Name:", answer(name))
    print(" ↳  Term is cool:", answer(is_cool))
    print(" ↳  Age:", answer(age))
    print(" ↳  Hours in a day:", answer(hours), f"({type(hours).__name__})")
    print(" ↳  Earth age:", answer(earth))
    print(" ↳  Moon age:", answer(moon))


if __name__ == "__main__":
    main()
