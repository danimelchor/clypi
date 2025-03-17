### `Parser[T]`

```python
Parser: TypeAlias = Callable[[Any], T] | type[T]
```
A function taking in any value and returns a value of type `T`. This parser
can be a user defined function, a built-in type like `str`, `int`, etc., or a parser
from a library.

### `confirm`

```python
def confirm(
    text: str,
    *,
    default: bool | Unset = UNSET,
    max_attempts: int = MAX_ATTEMPTS,
    abort: bool = False,
) -> bool:
```
Prompts the user for a yes/no value.

Parameters:

- `text`: the text to display to the user when asking for input
- `default`: optionally set a default value that the user can immediately accept
- `max_attempts`: how many times to ask the user before giving up and raising
- `abort`: if a user answers "no", it will raise a `AbortException`


### `prompt`

```python
def prompt(
    text: str,
    default: T | Unset = UNSET,
    parser: Parser[T] = str,
    hide_input: bool = False,
    max_attempts: int = MAX_ATTEMPTS,
) -> T:
```
Prompts the user for a value and uses the provided parser to validate and parse the input

Parameters:

- `text`: the text to display to the user when asking for input
- `default`: optionally set a default value that the user can immediately accept
- `parser`: a function that parses in the user input as a string and returns the parsed value or raises
- `hide_input`: whether the input shouldn't be displayed as the user types (for passwords, API keys, etc.)
- `max_attempts`: how many times to ask the user before giving up and raising
