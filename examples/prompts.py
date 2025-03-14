from __future__ import annotations

import clypi
import clypi.parsers as cp


def _validate_earth_age(x: str | list[str]) -> int:
    if isinstance(x, str):
        x_int = int(x)
        if x_int == 4_543_000_000:
            return x_int
    raise ValueError("The Earth is 4.543 billion years old. Try 4543000000.")


def main() -> None:
    # Basic prompting
    name = clypi.prompt("What's your name?")

    # Default values
    is_cool = clypi.confirm("Is clypi cool?", default=True)

    # Custom types with parsing
    age = clypi.prompt(
        "How old are you?",
        parser=cp.Int(gte=18),
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
    clypi.cprint("🚀 Summary", bold=True, fg="green")
    answer = clypi.Styler(fg="magenta", bold=True)
    print(" ↳  Name:", answer(name))
    print(" ↳  Clypi is cool:", answer(is_cool))
    print(" ↳  Age:", answer(age))
    print(" ↳  Hours in a day:", answer(hours), f"({type(hours).__name__})")
    print(" ↳  Earth age:", answer(earth))


if __name__ == "__main__":
    main()
