# 🦄 clypi

[![PyPI version](https://badge.fury.io/py/clypi.svg)](https://badge.fury.io/py/clypi)
[![License](https://img.shields.io/badge/license-MIT-blue)](https://opensource.org/license/mit)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/clypi.svg)](https://pypi.org/project/clypi/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/clypi)](https://pypi.org/project/clypi/)
[![Contributors](https://img.shields.io/github/contributors/danimelchor/clypi)](https://github.com/danimelchor/clypi/graphs/contributors)

Type-safe Python CLI prompts with validations, retries, custom messages, etc.

### Examples

Check out the examples in `./examples`! You can run them locally with:
```
uv run --all-extras -m examples.cli
uv run --all-extras -m examples.colors
uv run --all-extras -m examples.spinner
uv run --all-extras -m examples.prompts
```

## CLI

```python
# examples/basic_cli.py
from clypi import Command

class Lint(Command):
    files: tuple[str, ...]

    async def run(self):
        print(f"Linting {', '.join(self.files)}")

class MyCli(Command):
    subcommand: Lint | None = None
    verbose: bool = False

    async def run(self):
        print(f"Running the main command with {self.verbose}")

if __name__ == "__main__":
    cli: MyCli = MyCli.parse()
    cli.start()
```

<details>
    <summary><code>uv run -m examples.basic_cli -h</code> (Main help page)</summary>
    <p align="center">
        <img width="1694" alt="image" src="https://github.com/user-attachments/assets/91279a3e-cecd-4ac3-a1e7-38507b1d8ddb" />
    </p>
</details>

<details>
    <summary><code>uv run -m examples.basic_cli lint</code> (Subcommand help page)</summary>
    <p align="center">
        <img width="1694" alt="image" src="https://github.com/user-attachments/assets/e1222650-2d5b-44c6-a0ef-b085adcab30e" />
    </p>
</details>

<details>
    <summary><code>uv run -m examples.basic_cli</code> (Normal run)</summary>
    <p align="center">
        <img width="609" alt="image" src="https://github.com/user-attachments/assets/d085ba81-f9fd-472e-9bb7-1a788d918b16" />
    </p>
</details>

<details>
    <summary><code>uv run -m examples.basic_cli lint</code> (Missing args error)</summary>
    <p align="center">
        <img width="1692" alt="image" src="https://github.com/user-attachments/assets/f4e08d8f-affd-4e74-9dc2-d4baa7be0f62" />
    </p>
</details>

<details>
    <summary><code>uv run -m examples.basic_cli lin</code> (Typo)</summary>
    <p align="center">
        <img width="1696" alt="image" src="https://github.com/user-attachments/assets/c75b2cb0-2f2e-4907-86cb-2f62122c0c70" />
    </p>
</details>


## ❓ Prompting

First, you'll need to import the `clypi` module:
```python
import clypi

answer = clypi.prompt("Are you going to use clypi?", default=True, parser=bool)
```

## 🌈 Colors



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

<details>
    <summary><code>uv run demo.py</code></summary>
    <p align="center">
      <img width="487" alt="image" src="https://github.com/user-attachments/assets/0ee3b49d-0358-4d8c-8704-2da89529b4f5" />
    </p>
</details>

<details>
    <summary><code>uv run -m examples.colors</code></summary>
    <p align="center">
        <img width="974" alt="image" src="https://github.com/user-attachments/assets/9340d828-f7ce-491c-b0a8-6a666f7b7caf" />
    </p>
</details>


## 🌀 Spinners

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

<details>
    <summary><code>uv run demo.py</code></summary>
    <p align="center">
      <video src="https://github.com/user-attachments/assets/c0b4dc28-f6d4-4891-a9fa-be410119bd83" />
    </p>
</details>

<details>
    <summary><code>uv run -m examples.spinner</code></summary>
    <p align="center">
      <video src="https://github.com/user-attachments/assets/f641a4fe-59fa-4bc1-b31a-bb642c507a20" />
    </p>
</details>


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

### Why do I care?

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
