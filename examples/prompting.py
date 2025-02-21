from __future__ import annotations

import argparse

from src.python.term import term
from src.python.term import validations as v
from src.python.util.scripting import colors


def _validate_earth_age(x: int) -> None:
    if x != 4_543_000_000:
        raise ValueError("The Earth is 4.543 billion years old. Try 4543000000.")


def main() -> None:
    # Basic prompting
    name = term.prompt("What's your name?")

    # Default values
    to_the_moon = term.prompt("Stripe coin to the moon?", default=True, klass=bool)

    # Custom types with parsing
    age = term.prompt(
        "How old are you?",
        klass=int,
    )
    hours = term.prompt(
        "How many hours are there in a day?",
        klass=term.TimeDelta() | term.Int(),
    )

    # Custom validations
    earth = term.prompt(
        "How old is The Earth?",
        klass=int,
        validate=_validate_earth_age,
    )
    moon = term.prompt(
        "How old is The Moon?",
        klass=int,
        validate=v.Gte(4) & v.Lte(5) | v.Choices([5]),  # You can chain validations
    )

    # Integration with argparse
    parser = argparse.ArgumentParser()
    _ = parser.add_argument("--animal", type=str)
    args = parser.parse_args()
    animal = term.prompt("What's your favorite animal?", provided=args.animal)

    # -----------
    print()
    print(colors.style.bold(colors.fg.green("🚀 Summary")))
    print(f"  Name: {name}")
    print(f"  Stripe coin to the moon: {to_the_moon}")
    print(f"  Age: {age}")
    print(f"  Hours in a day: {hours} ({type(hours).__name__})")
    print(f"  Earth age: {earth}")
    print(f"  Moon age: {moon}")
    print(f"  Favorite animal: {animal}")


if __name__ == "__main__":
    main()
