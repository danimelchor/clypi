from __future__ import annotations

from src.python.term import validations as v
from src.python.util.scripting import colors


# --- DEMO UTILS ---
def print_title(x: str) -> None:
    print("\n" + colors.fg.blue(colors.style.bold(x)))


def print_example(prompt: str, result: bool) -> None:
    color = colors.fg.green if result else colors.fg.red
    print(prompt, color(str(result)))


# --- DEMO ---
def main() -> None:
    # Basic usage
    can_drink = v.Gte(21)
    print_title("Basic - Age")
    print_example("With age 21 can you drink?", can_drink.test(21))
    print_example("With age 20 can you drink?", can_drink.test(20))

    # You can "AND" multiple validations
    interview_channel = v.StartsWith("#") & v.ReSearch("interview.*[0-9]{2}-[0-9]{2}")
    print_title("AND Validations - Slack Channel")
    print_example(
        "Is channel #interview-foo-feb-01-12 an interview slack channel?",
        interview_channel.test("#interview-foo-feb-01-12"),
    )
    print_example(
        "Is channel #foo-feb-01-12 an interview slack channel?",
        interview_channel.test("#foo-feb-01-12"),
    )

    # You can "OR" multiple validations
    slack_or_jira = v.ReMatch(r"#[a-z0-9-]+") | v.ReMatch(r"[A-Z0-9_]+")
    print_title("OR Validations - Slack or Jira")
    print_example("Is #foo-bar-1 a valid slack or Jira?", slack_or_jira.test("#foo-bar-1"))
    print_example("Is FOO_BAR100 a valid slack or Jira?", slack_or_jira.test("FOO_BAR100"))
    print_example("Is foo-bar-1 a valid slack or Jira?", slack_or_jira.test("foo-bar-1"))

    # You can create your own custom validations
    def _validate_earth_age(x: int) -> None:
        if x != 4_543_000_000:
            raise ValueError("The Earth is 4.543 billion years old. Try 4543000000.")

    earth_age = v.Custom(_validate_earth_age)
    print_title("Custom Validation - Earth Age")
    print_example("Is 4.543 billion years a valid Earth age?", earth_age.test(4_543_000_000))
    print_example("Is 4.543 million years a valid Earth age?", earth_age.test(4_543_000))

    # You can create your own reusable validation types
    class SlackChannel(v.Validation[str]):
        def validate(self, x: str):
            if not x.startswith("#"):
                raise v.ValidationException("Slack channels must start with '#'")

    slack_channel = SlackChannel()
    print_title("Reusable Validation Type - Slack Channel")
    print_example("Is #foo-bar a valid slack channel?", slack_channel.test("#foo-bar"))
    print_example("Is foo-bar a valid slack channel?", slack_channel.test("foo-bar"))


if __name__ == "__main__":
    main()
