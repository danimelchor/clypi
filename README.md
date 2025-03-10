# 🦄 clypi

[![PyPI version](https://badge.fury.io/py/clypi.svg)](https://badge.fury.io/py/clypi)
[![License](https://img.shields.io/badge/license-MIT-blue)](https://opensource.org/license/mit)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/clypi.svg)](https://pypi.org/project/clypi/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/clypi)](https://pypi.org/project/clypi/)
[![Contributors](https://img.shields.io/github/contributors/danimelchor/clypi)](https://github.com/danimelchor/clypi/graphs/contributors)

Your all-in-one for beautiful, lightweight, prod-ready CLIs

#### Get started

```bash
uv add clypi  # or `pip install clypi`
```

#### Examples

You can run the examples in `./examples` locally. First, clone the repository, then use `uv run --all-extras -m examples.<example>`. E.g.:
```bash
uv run --all-extras -m examples.cli

# Or:
pip install .[examples]
python -m examples.cli
```

## 📖 Docs

Read [the API docs](https://github.com/danimelchor/clypi/blob/master/docs/index.md) for examples and a full API reference.

## 🧰 CLI

Read the [docs](https://github.com/danimelchor/clypi/blob/master/docs/index.md#cli)

```python
# examples/basic_cli.py
from clypi import Command, Positional, arg

class Lint(Command):
    files: Positional[tuple[str, ...]]
    verbose: bool = arg(...)  # Comes from MyCli but I want to use it too

    async def run(self):
        print(f"Linting {', '.join(self.files)} and {self.verbose=}")

class MyCli(Command):
    """
    my-cli is a very nifty demo CLI tool
    """
    subcommand: Lint | None = None
    verbose: bool = arg(
        help="Whether to show extra logs",
        prompt="Do you want to see extra logs?",
        default=False,
        short="v",  # User can pass in --verbose or -v
    )

    async def run(self):
        print(f"Running the main command with {self.verbose}")

if __name__ == "__main__":
    cli: MyCli = MyCli.parse()
    cli.start()
```

`uv run -m examples.basic_cli lin`

<img width="1697" alt="image" src="https://github.com/user-attachments/assets/76d2c6c4-e075-4c69-89a8-f8dac8dec367" />


## 🛠️ Configurable

Read the [docs](https://github.com/danimelchor/clypi/blob/master/docs/index.md#configuration)

Clypi lets you configure the app globally. This means that all the styling will be easy,
uniform across your entire app, and incredibly maintainable.

For example, this is how you'd achieve a UI like `uv`'s CLI:

```python
from clypi import ClypiConfig, ClypiFormatter, Styler, Theme, configure

configure(
    ClypiConfig(
        theme=Theme(
            usage=Styler(fg="green", bold=True),
            prog=Styler(fg="cyan", bold=True),
            section_title=Styler(fg="green", bold=True),
            subcommand=Styler(fg="cyan"),
            long_option=Styler(fg="cyan"),
            short_option=Styler(fg="cyan"),
            positional=Styler(fg="cyan"),
            type_str=Styler(fg="cyan"),
            prompts=Styler(fg="green", bold=True),
        ),
        help_formatter=ClypiFormatter(boxed=False),
    )
)
```

`uv run -m examples.uv ad`

<img width="1699" alt="image" src="https://github.com/user-attachments/assets/65643677-c95b-4d48-955d-28ba49797fa9" />

## 🌈 Colors

Read the [docs](https://github.com/danimelchor/clypi/blob/master/docs/index.md#colors)

```python
# demo.py
import clypi

# Style text
print(clypi.style("This is blue", fg="blue"), "and", clypi.style("this is red", fg="red"))

# Print with colors directly
clypi.print("Some colorful text", fg="green", reverse=True, bold=True, italic=True)

# Store a styler and reuse it
wrong = clypi.Styler(fg="red", strikethrough=True)
print("The old version said", wrong("Pluto was a planet"))
print("The old version said", wrong("the Earth was flat"))
```

`uv run -m examples.colors`

<img width="974" alt="image" src="https://github.com/user-attachments/assets/9340d828-f7ce-491c-b0a8-6a666f7b7caf" />

## 🌀 Spinners

Read the [docs](https://github.com/danimelchor/clypi/blob/master/docs/index.md#spinners)

You can use spinners as an async context manager:
```python
import asyncio
from clypi import Spinner

async def main():
    async with Spinner("Downloading assets") as s:
        for i in range(1, 6):
            await asyncio.sleep(0.5)
            s.title = f"Downloading assets [{i}/5]"

asyncio.run(main())
```

Or as a decorator:

```python
import asyncio
from clypi import spinner

@spinner("Doing work", capture=True)
async def do_some_work():
    await asyncio.sleep(5)

asyncio.run(do_some_work())
```

`uv run -m examples.spinner`

https://github.com/user-attachments/assets/2065b3dd-c73c-4e21-b698-8bf853e8e520


## ❓ Prompting

Read the [docs](https://github.com/danimelchor/clypi/blob/master/docs/index.md#prompt)

First, you'll need to import the `clypi` module:
```python
import clypi

answer = clypi.confirm("Are you going to use clypi?", default=True)
```


## 🔀 Async by default

`clypi` was built with an async-first mentality. Asynchronous code execution is incredibly
valuable for applications like CLIs where we want to update the UI as we take certain actions behind the scenes.
Most often, these actions can be made asynchronous since they involve things like file manipulation, network requests, subprocesses, etc.

## 🐍 Type-checking

This library is fully type-checked. This means that all types will be correctly inferred
from the arguments you pass in.

In this example your editor will correctly infer the type:
```python
hours = clypi.prompt(
    "How many hours are there in a year?",
    parser=lambda x: float(x) if x < 24 else timedelta(days=x),
)
reveal_type(hours)  # Type of "res" is "float | timedelta"
```

#### Why should I care?

Type checking will help you catch issues way earlier in the development cycle. It will also
provide nice autocomplete features in your editor that will make you faster 󱐋.

## 🔌 Integrations

### Parsers ([v6e](https://github.com/danimelchor/v6e), [pydantic](https://github.com/pydantic/pydantic), etc.)

CLIPy can be integrated with many parsers. The default recommended parser is [v6e](https://github.com/danimelchor/v6e), which is automatically used if installed in your local environment to parse types more accurately. If you wish you specify any parser (from `v6e` or elsewhere) manually, you can do so quite easily:

**CLI**
```python
import v6e
from clypi import Command, arg

class MyCli(Command):
    files: list[Path] = arg(parser=v6e.path().exists().list())

    async def run(self):
        files = [f.as_posix() for f in self.files]
        print(f"Linting {', '.join(files)}")

if __name__ == "__main__":
    cli: MyCli = MyCli.parse()
    cli.start()
```

**Prompting**

```python
import v6e

hours = clypi.prompt(
    "How many hours are there in a year?",
    parser=v6e.float().lte(24).union(v6e.timedelta()),
)
reveal_type(hours)  # Type of "res" is "float | timedelta"
```
