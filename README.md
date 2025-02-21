# 🦄 Term

Type-safe Python CLI prompts with validations, retries, custom messages, etc.

## Examples

Check out the examples in `./examples`! You can run them locally with:

```
python -m examples.<name>
```

For example:
```
python -m examples.validations
```

## Usage


### ✔️ Validations

First, you'll need to import the `validations` module:
```python
from term import validations as v
```

**Basic validations**
```python
my_validation = v.Range(18, 21)

# .test(...)
my_validation.test(18)  # True
my_validation.test(21)  # True
my_validation.test(54)  # False

# .validate(...)
my_validation.validate(21)  # Nothing happens -> continue to next line
my_validation.validate(54)  # Raises a ValidationException()
```

**`AND` and `OR` validations**
```python
my_validation = (v.StartsWith("foo") | v.EndsWith("foo")) & v.ReMatch(r"^[a-z]*$")
my_validation.test("foo12")  # True
my_validation.test("12foo")  # True
my_validation.test("1foo2")  # False
```

**Custom validations**
```python
def is_div_three(x: int):
    if x % 3 != 0:
        raise ValueError("Woops! The Earth is 4.543 billion years old. (Try 4543000000)")

my_validation = v.Custom(validate_earth_age)
my_validation.test(3)  # True
my_validation.test(6)  # True
my_validation.test(4)  # False
```

### ❓ Prompting

First, you'll need to import the `term` module:
```python
from term import term
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
    klass=term.TimeDelta() | term.Int(),
)
```

**Built-in validations (see the validations section)**
```python
earth = term.prompt(
    "How old is The Earth?",
    klass=term.Int(),
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
    klass=term.Int(),
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

### 🐍 Type-checking

This library is fully type-checked. This means that all types will be correctly inferred
from the arguments you pass in.

In this example your editor will correctly infer the type:
```python
hours = term.prompt(
    "How many hours are there in a day?",
    klass=term.TimeDelta() | term.Str() | term.Int(),
)
reveal_type(hours)  # Type of "res" is "timedelta | str | int"
```

In some cases, like prompting, the type will also indicate how to validate and parse the passed argument.
For example, the following code will validate that the passed input is a valid number:
```python
age = term.prompt("What's your age?", klass=term.Int())
```


## Why do I care?

Type checking will help you catch issues way earlier in the development cycle. It will also
provide nice autocomplete features in your editor that will make you faster 󱐋.
