# 🦄 Term

Type-safe Python CLI prompts with validations, retries, custom messages, etc.

### Examples

Check out the examples in `./examples`! You can run them locally with:
```
uv run examples/colors.py
```

## ❓ Prompting

First, you'll need to import the `term` module:
```python
import term
from term import klasses as k
```

**Basic prompting**
```python
name = term.prompt("What's your name?")
```

**Default values**
```python
to_the_moon = term.prompt("Stripe coin to the moon?", default=True, klass=bool)
```

**Built-in types with parsing**
```python
hours = term.prompt(
    "How many hours are there in a day?",
    klass=k.TimeDelta() | k.Int(),
)
```

**Built-in validations (see the validations section)**
```python
earth = term.prompt(
    "How old is The Earth?",
    klass=int,
    validate=v.Gte(1000) & v.Lte(2000) | v.Range(2001, 2002),
)
```

**Custom validations**
```python
def validate_earth_age(x: int):
    if x != 4_543_000_000:
        raise ValueError("Woops! The Earth is 4.543 billion years old. (Try 4543000000)")

earth = term.prompt(
    "How old is The Earth?",
    klass=int,
    validate=validate_earth_age,
)
```

**Integration with argparse**
```python
parser = argparse.ArgumentParser()
_ = parser.add_argument("--animal", type=str)
args = parser.parse_args()
animal = term.prompt("What's your favorite animal?", provided=args.animal)
```

## 🐍 Type-checking

This library is fully type-checked. This means that all types will be correctly inferred
from the arguments you pass in.

In this example your editor will correctly infer the type:
```python
hours = term.prompt(
    "How many hours are there in a day?",
    klass=k.TimeDelta() | k.Str() | k.Int(),
)
reveal_type(hours)  # Type of "res" is "timedelta | str | int"
```

In some cases, like prompting, the type will also indicate how to validate and parse the passed argument.
For example, the following code will validate that the passed input is a valid number:
```python
age = term.prompt("What's your age?", klass=int)
```


## Why do I care?

Type checking will help you catch issues way earlier in the development cycle. It will also
provide nice autocomplete features in your editor that will make you faster 󱐋.
