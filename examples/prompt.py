from __future__ import annotations

import argparse

import term
from term import colors
from term import klasses as k
from term import validations as v


def _validate_earth_age(x: int) -> None:
    if x != 4_543_000_000:
        raise ValueError("The Earth is 4.543 billion years old. Try 4543000000.")


def main() -> None:
    # Basic prompting
    name = term.prompt("What's your name?")

    # Default values
    is_cool = term.prompt("Is Term cool?", default=True, klass=bool)

    # Custom types with parsing
    age = term.prompt(
        "How old are you?",
        klass=int,
    )
    hours = term.prompt(
        "How many hours are there in a day?",
        klass=k.TimeDelta() | k.Int(),
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
    colors.print("🚀 Summary", bold=True, fg="green")
    print(f"  Name: {name}")
    print(f"  Term is cool: {is_cool}")
    print(f"  Age: {age}")
    print(f"  Hours in a day: {hours} ({type(hours).__name__})")
    print(f"  Earth age: {earth}")
    print(f"  Moon age: {moon}")
    print(f"  Favorite animal: {animal}")


if __name__ == "__main__":
    main()
