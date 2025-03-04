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

Check out the examples in `./examples`! You can run them locally with `uv run --all-extras -m examples.<example>`. E.g.:
```bash
uv run --all-extras -m examples.cli

# Or:
pip install .[examples]
python -m examples.cli
```

## Docs

Read [the API docs](https://github.com/danimelchor/clypi/blob/master/docs/index.md) for examples and a full API reference.

> [!IMPORTANT]
> This project is still in development. Expect frequent and (some) breaking changes. For upcoming
> releases, you can follow [the planned work section](https://github.com/danimelchor/clypi/blob/master/docs/planned_work.md).


## CLI

Read the [docs](https://github.com/danimelchor/clypi/blob/master/docs/index.md#cli)

```python
# examples/basic_cli.py
from clypi import Command, config

class Lint(Command):
    files: tuple[str, ...]
    verbose = config(...)  # Comes from MyCli but I want to use it too

    async def run(self):
        print(f"Linting {', '.join(self.files)} and {self.verbose=}")

class MyCli(Command):
    """
    my-cli is a very nifty demo CLI tool
    """
    subcommand: Lint | None = None
    verbose: bool = config(
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

<details open>
    <summary><code>uv run -m examples.basic_cli lin</code> (Typo)</summary>
    <p align="center">
        <img width="1695" alt="image" src="https://github.com/user-attachments/assets/f57f6518-7d22-4320-a0fe-ec95c1c0579b" />
    </p>
</details>

<details>
    <summary><code>uv run -m examples.basic_cli -h</code> (Main help page)</summary>
    <p align="center">
        <img width="1692" alt="image" src="https://github.com/user-attachments/assets/cc939eab-c9db-4021-8374-a25b892a434c" />
    </p>
</details>

<details>
    <summary><code>uv run -m examples.basic_cli lint -h</code> (Subcommand help page)</summary>
    <p align="center">
        <img width="1692" alt="image" src="https://github.com/user-attachments/assets/52eb16a2-7edc-4563-ab3f-0bbe3ab05b14" />
    </p>
</details>

<details>
    <summary><code>uv run -m examples.basic_cli</code> (Normal run)</summary>
    <p align="center">
        <img width="836" alt="image" src="https://github.com/user-attachments/assets/030f4e2e-5046-4fa6-948a-c9ab80070ef7" />
    </p>
</details>

<details>
    <summary><code>uv run -m examples.basic_cli lint</code> (Missing args error)</summary>
    <p align="center">
        <img width="1692" alt="image" src="https://github.com/user-attachments/assets/4d42bed1-53a3-483f-8d34-fddb2ffec7c6" />
    </p>
</details>


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
wrong = clypi.styler(fg="red", strikethrough=True)
print("The old version said", wrong("Pluto was a planet"))
print("The old version said", wrong("the Earth was flat"))
```

<details open>
    <summary><code>uv run -m examples.colors</code></summary>
    <p align="center">
        <img width="974" alt="image" src="https://github.com/user-attachments/assets/9340d828-f7ce-491c-b0a8-6a666f7b7caf" />
    </p>
</details>


<details>
    <summary><code>uv run demo.py</code></summary>
    <p align="center">
      <img width="487" alt="image" src="https://github.com/user-attachments/assets/0ee3b49d-0358-4d8c-8704-2da89529b4f5" />
    </p>
</details>


## 🌀 Spinners

Read the [docs](https://github.com/danimelchor/clypi/blob/master/docs/index.md#spinners)

```python
# demo.py
import asyncio
from clypi import Spinner

async def main():
    async with Spinner("Downloading assets") as s:
        for i in range(1, 6):
            await asyncio.sleep(0.5)
            s.title = f"Downloading assets [{i}/5]"

asyncio.run(main())
```
<details open>
    <summary><code>uv run -m examples.spinner</code></summary>
    <p align="center">
      <video src="https://github.com/user-attachments/assets/3af51391-1ab4-4b41-86f1-1e08e01be7b9" />
    </p>
</details>

<details>
    <summary><code>uv run demo.py</code></summary>
    <p align="center">
      <video src="https://github.com/user-attachments/assets/c0b4dc28-f6d4-4891-a9fa-be410119bd83" />
    </p>
</details>

## ❓ Prompting

Read the [docs](https://github.com/danimelchor/clypi/blob/master/docs/index.md#prompt)

First, you'll need to import the `clypi` module:
```python
import clypi

answer = clypi.prompt("Are you going to use clypi?", default=True, parser=bool)
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

## Integrations

### Parsers ([v6e](https://github.com/danimelchor/v6e), [pydantic](https://github.com/pydantic/pydantic), etc.)

CLIPy can be integrated with many parsers. The default recommended parser is [v6e](https://github.com/danimelchor/v6e), which is automatically used if installed in your local environment to parse types more accurately. If you wish you specify any parser (from `v6e` or elsewhere) manually, you can do so quite easily:

**CLI**
```python
import v6e
from clypi import Command, config

class MyCli(Command):
    files: list[Path] = config(parser=v6e.path().exists().list())

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
