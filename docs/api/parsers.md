For this section, parsers will be imported as such:
```python
import clypi.parsers as cp
```

### `Int`

The `Int` parser converts string input into an integer.

```python
Int(
    gt: int | None = None,
    gte: int | None = None,
    lt: int | None = None,
    lte: int | None = None,
    max: int | None = None,
    min: int | None = None,
    positive: bool = False,
    nonpositive: bool = False,
    negative: bool = False,
    nonnegative: bool = False,

```

Parameters:

- `gt`: A value the integer must be greater than
- `gte`: A value the integer must be greater than or equal to
- `lt`: A value the integer must be less than
- `lte`: A value the integer must be less than or equal to
- `max`: The maximum value the integer can be (same as lte)
- `min`: The maximum value the integer can be (same as gte)
- `positive`: The integer must be greater than 0
- `nonpositive`: The integer must be less than or equal to 0
- `negative`: The integer must be less than 0
- `nonnegative`: The integer must be greater than or equal to 0

Examples:
<!-- mdtest -->
```python
import clypi.parsers as cp

parser = cp.Int(lte=10, gt=2)
assert parser("3") == 3
assert_raises(lambda: parser("2"))  # Not >2
assert_raises(lambda: parser("11"))  # Not <=10
```

### `Float`

The `Float` parser converts string input into a floating-point number.

```python
Float(
    gt: float | None = None,
    gte: float | None = None,
    lt: float | None = None,
    lte: float | None = None,
    max: float | None = None,
    min: float | None = None,
    positive: bool = False,
    nonpositive: bool = False,
    negative: bool = False,
    nonnegative: bool = False,
)
```
Parameters:

- `gt`: A value the float must be greater than
- `gte`: A value the float must be greater than or equal to
- `lt`: A value the float must be less than
- `lte`: A value the float must be less than or equal to
- `max`: The maximum value the float can be (same as lte)
- `min`: The maximum value the float can be (same as gte)
- `positive`: The float must be greater than 0
- `nonpositive`: The float must be less than or equal to 0
- `negative`: The float must be less than 0
- `nonnegative`: The float must be greater than or equal to 0

Examples:
<!-- mdtest -->
```python
import clypi.parsers as cp

parser = cp.Float(lte=10, gt=2)
assert parser("3") == 3
assert parser("2.01") == 2.01
assert_raises(lambda: parser("2"))  # Not >2
assert_raises(lambda: parser("11"))  # Not <=10
```

### `Bool`

The `Bool` parser converts string input into a boolean.

```python
Bool()
```

Accepted values:
- `true`, `yes`, `y` → `True`
- `false`, `no`, `n` → `False`


Examples:
<!-- mdtest -->
```python
import clypi.parsers as cp

parser = cp.Bool()
assert parser("y") is True
assert parser("NO") is False
```

### `Str`

The `Str` parser returns the string input as-is.

```python
Str(
    length: int | None = None,
    max: int | None = None,
    min: int | None = None,
    startswith: str | None = None,
    endswith: str | None = None,
    regex: str | None = None,
    regex_group: int | None = None,
)
```
Parameters:

- `length`: The string must be of this length
- `max`: The string's length must be at most than this number
- `min`: The string's length must be at least than this number
- `startswith`: The string must start with that substring
- `endsswith`: The string must end with that substring
- `regex`: The string must match this regular expression
- `regex_group`: (required `regex`) extracts the group from the regular expression

Examples:

<!-- mdtest -->
```python
import clypi.parsers as cp

parser = cp.Str(regex=r"[a-z]([0-9]+)", regex_group=1)
assert parser("f1") == "1"
assert parser("f123") == "123"
assert_raises(lambda: parser("123f"))
assert_raises(lambda: parser("f"))
```

### `DateTime`

The `DateTime` parser converts string input into a `datetime` object.

```python
DateTime(
    tz: timezone | None = None,
)
```
Parameters:

- `tz`: the timezone to convert the date to. If the date is provided without a timezone, it will be forced as the specified one. If it's passed with a timezone, it will convert the date to the right offset.

### `TimeDelta`

The `TimeDelta` parser converts string input into a `timedelta` object.

```python
TimeDelta(
    gt: timedelta | None = None,
    gte: timedelta | None = None,
    lt: timedelta | None = None,
    lte: timedelta | None = None,
    max: timedelta | None = None,
    min: timedelta | None = None,
)
```
- `gt`: A value the timedelta must be greater than
- `gte`: A value the timedelta must be greater than or equal to
- `lt`: A value the timedelta must be less than
- `lte`: A value the timedelta must be less than or equal to
- `max`: The maximum value the timedelta can be (same as lte)
- `min`: The maximum value the timedelta can be (same as gte)

Examples:
<!-- mdtest -->
```python
import clypi.parsers as cp

parser = cp.TimeDelta(gte=timedelta(days=1))
assert parser("1 day") == timedelta(days=1)
assert parser("1w") == timedelta(weeks=1)
assert_raises(lambda: parser("23h")) # Under 1 day
```

Supported time units:
- `weeks (w)`, `days (d)`, `hours (h)`, `minutes (m)`, `seconds (s)`, `milliseconds (ms)`, `microseconds (us)`

### `Path`

The `Path` parser is useful to parse file or directory-like arguments from the CLI.

```python
Path(exists: bool = False)
```
Parameters:

- `exists`: If `True`, it checks whether the provided path exists.

Examples:
<!-- mdtest -->
```python
import clypi.parsers as cp

cp.Path(exists=True)
```

### `List`

The `List` parser parses comma-separated values into a list of parsed elements. The CLI parser will, by default, pass
in multiple arguments as a list of strings to the top-level `List` parser. Nested items will be parsed by splitting the string by commas.

```python
List(inner: Parser[T])
```

Examples:
<!-- mdtest -->
```python
import clypi.parsers as cp

# list[int]
# E.g.: --foo 1 2 3
parser = cp.List(cp.Int())
assert parser(["1", "2", "3"]) == [1, 2, 3]
assert parser("1, 2, 3") == [1, 2, 3]

# list[list[int]]
# E.g.: --foo 1,2 2,3 3,4
parser = cp.List(cp.List(cp.Int()))
assert parser(["1,2", "2,3", "3, 4"]) == [
    [1, 2],
    [2, 3],
    [3, 4],
]
```

Parameters:

- `inner`: The parser used to convert each list element.

### `Tuple`

The `Tuple` parser parses a string input into a tuple of values. The tuple parser will split the input string by commas.

```python
Tuple(*inner: Parser, num: int | None = None)
```

Examples:
<!-- mdtest -->
```python
import clypi.parsers as cp

# tuple[str, ...]
# E.g.: --foo a,b,c
parser = cp.Tuple(cp.Str(), num=None)
assert parser(["a", "b", "c"]) == ("a", "b", "c")
assert parser("a,b,c") == ("a", "b", "c")

# tuple[str, int]
# E.g.: --foo a,2
parser = cp.Tuple(cp.Str(), cp.Int())
assert parser(["a", "2"]) == ("a", 2)
assert parser("a,2") == ("a", 2)

# list[tuple[str, int]]
# E.g.: --foo a,2 b,3 c,4
parser = cp.List(cp.Tuple(cp.Str(), cp.Int()))
assert parser(["a,2", "b,3", "c, 4"]) == [
    ("a", 2),
    ("b", 3),
    ("c", 4),
]
```

Parameters:

- `inner`: List of parsers for each tuple element.
- `num`: Expected tuple length. If None, the tuple will accept unlimited arguments (equivalent to `tuple[<type>, ...]`)

### `Union`

The `Union` parser attempts to parse input using multiple parsers.

```python
Union(left: Parser[X], right: Parser[Y])
```

You can also use the short hand `|` syntax for two parsers, e.g.:
<!-- mdtest -->
```python
import clypi.parsers as cp
from pathlib import Path

parser = cp.Union(cp.Path(exists=True), cp.Int())
parser = cp.Path(exists=True) | cp.Int()
assert parser("README.md") == Path("README.md")
assert parser("1") == 1
assert_raises(lambda: parser("foo"))
```

### `Literal`

The `Literal` parser ensures that input matches one of the predefined values.

```python
Literal(*values: t.Any)
```

Examples:
<!-- mdtest -->
```python
import clypi.parsers as cp

parser = cp.Literal(1, "foo")
assert parser("1") == 1
assert parser("foo") == "foo"
assert_raises(lambda: parser("bar"))
```

### `Enum`

The `Enum` parser maps string input to a valid enum value.

```python
Enum(enum: type[enum.Enum])
```

Examples:
<!-- mdtest -->
```python
import clypi.parsers as cp
from enum import Enum

class Color(Enum):
    RED = 1
    BLUE = 2

parser = cp.Enum(Color)
assert parser("red") == Color.RED
assert parser("blue") == Color.BLUE
assert_raises(lambda: parser("green"))
```

### `from_type`

The `from_type` function returns the appropriate parser for a given type.

```python
@tu.ignore_annotated
def from_type(_type: type) -> Parser: ...
```

Examples:
<!-- mdtest -->
```python
import clypi.parsers as cp

assert cp.from_type(bool) == cp.Bool()
```

### Supported built-in types

- `None` :material-arrow-right: `cp.NoneParser()`
- `bool` :material-arrow-right: `cp.Bool()`
- `int` :material-arrow-right: `cp.Int()`
- `float` :material-arrow-right: `cp.Float()`
- `str` :material-arrow-right: `cp.Str()`
- `Path` :material-arrow-right: `cp.Path()`
- `datetime` :material-arrow-right: `cp.DateTime()`
- `timedelta` :material-arrow-right: `cp.TimeDelta()`
- `Enum` :material-arrow-right: `cp.Enum(<type>)`
- `list[<type>]` :material-arrow-right: `cp.List(<type>)`. E.g.:
    - `list[str]` :material-arrow-right: `cp.List(cp.Str())`)
- `tuple[<type(s)>]` :material-arrow-right: `cp.Tuple(<type>, <len>)`. E.g.:
    - `tuple[str]` :material-arrow-right: `cp.Tuple(cp.Str())`)
    - `tuple[str, int]` :material-arrow-right: `cp.Tuple(cp.Str(), cp.Int())`)
    - `tuple[str, ...]` :material-arrow-right: `cp.Tuple(cp.Str(), num=None)`)
- `Union[<type(s)>]` :material-arrow-right: `cp.Union(*<type(s)>)`. E.g.:
    - `str | None` :material-arrow-right: `cp.Union(cp.Str(), cp.NoneParser())`)
    - `str | bool | int` :material-arrow-right: `cp.Union(cp.Str(), cp.Bool(), cp.Int())`)
- <!-- md:version 1.2.15 --> `Optional[<type>]` :material-arrow-right: `cp.Union(<type>, cp.NoneParser())`. E.g.:
    - `Optional[str]` :material-arrow-right: `cp.Union(cp.Str(), cp.NoneParser())`)
- <!-- md:version 1.2.17 --> `Literal[<value(s)>]` :material-arrow-right: `cp.Literal(*<value(s)>)`. E.g.:
    - `Literal[1, "foo"]` :material-arrow-right: `cp.Literal(1, "foo")`)
