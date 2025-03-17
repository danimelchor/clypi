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
- `nonpostive`: The integer must be less than or equal to 0
- `negative`: The integer must be less than 0
- `nonnegative`: The integer must be greater than or equal to 0

Examples:
<!--- mdtest -->
> ```python
> # 3 (OK), 10 (OK), 2 (not OK), 11 (not OK)
> cp.Int(lte=10, gt=2)
> ```

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
- `nonpostive`: The float must be less than or equal to 0
- `negative`: The float must be less than 0
- `nonnegative`: The float must be greater than or equal to 0

Examples:
<!--- mdtest -->
> ```python
> # 3 (OK), 10 (OK), 2 (not OK), 11 (not OK)
> cp.Float(lte=10, gt=2)
> ```

### `Bool`

The `Bool` parser converts string input into a boolean.

```python
Bool()
```

Accepted values:
- `true`, `yes`, `y` → `True`
- `false`, `no`, `n` → `False`

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

<!--- mdtest -->
> ```python
> cp.Str(regex=r"[a-z]([0-9])", regex_group=1) # f1 -> 1
> ```

### `DateTime`

The `DateTime` parser converts string input into a `datetime` object.

```python
DateTime(
    tz: timezone | None = None,
)
```
Parameters:

- `tz`: the timezone to convert the date to

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
<!--- mdtest -->
> ```python
> # 1 day (OK), 2 weeks (OK), 1 second (not OK)
> cp.TimeDelta(gte=timedelta(days=1))
> ```

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
<!--- mdtest -->
> ```python
> cp.Path(exists=True)
> ```

### `List`

The `List` parser parses comma-separated values into a list of parsed elements.

```python
List(inner: Parser[T])
```

Examples:
<!--- mdtest -->
> ```python
> cp.List(cp.Int())
> ```

Parameters:

- `inner`: The parser used to convert each list element.

### `Tuple`

The `Tuple` parser parses a string input into a tuple of values.

```python
Tuple(*inner: Parser, num: int | None = None)
```

Examples:
<!--- mdtest -->
> ```python
> # tuple[str, ...]
> cp.Tuple(cp.Str())
>
> # tuple[str, int]
> cp.Tuple(cp.Str(), cp.Int(), num=2)
> ```

Parameters:

- `inner`: List of parsers for each tuple element.
- `num`: Expected tuple length (optional).

### `Union`

The `Union` parser attempts to parse input using multiple parsers.

```python
Union(left: Parser[X], right: Parser[Y])
```

You can also use the short hand `|` syntax for two parsers, e.g.:
<!--- mdtest -->
> ```python
> cp.Union(cp.Path(exists=True), cp.Str())
> cp.Path(exists=True) | cp.Str()
> ```

### `Literal`

The `Literal` parser ensures that input matches one of the predefined values.

```python
Literal(*values: t.Any)
```

Examples:
<!--- mdtest -->
> ```python
> cp.Literal(1, "foo")
> ```

### `Enum`

The `Enum` parser maps string input to a valid enum value.

```python
Enum(enum: type[enum.Enum])
```

Examples:
<!--- mdtest -->
> ```python
> class Color(Enum):
>     RED = 1
>     BLUE = 2
>
> cp.Enum(Color)
> ```

### `from_type`

The `from_type` function returns the appropriate parser for a given type.

```python
@tu.ignore_annotated
def from_type(_type: type) -> Parser: ...
```

Examples:
<!--- mdtest -->
> ```python
> assert cp.from_type(bool) == cp.Bool()
> ```
