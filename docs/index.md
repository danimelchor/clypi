# 🦄 clypi

[![PyPI version](https://badge.fury.io/py/clypi.svg)](https://badge.fury.io/py/clypi)
[![License](https://img.shields.io/badge/license-MIT-blue)](https://opensource.org/license/mit)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/clypi.svg)](https://pypi.org/project/clypi/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/clypi)](https://pypi.org/project/clypi/)
[![Contributors](https://img.shields.io/github/contributors/danimelchor/clypi)](https://github.com/danimelchor/clypi/graphs/contributors)

Your all-in-one for beautiful, lightweight, prod-ready CLIs

### What is clypi?

I've been working with Python-based CLIs for several years with many users and strict quality requirements and always run into the sames problems with the go-to packages. Therefore, I decided to embark on a journey to build a lightweight, intuitive, pretty, and production ready framework. Here are the key features:

- **Type safe**: making use of dataclass-like commands, you can easily specify the types you want for each argument and clypi automatically parses and validates them.

- **Asynchronous**: clypi is built to run asynchronously to provide the best performance possible when re-rendering.

- **Easily testable**: thanks to being type checked and to using it's own parser, clypi let's you test each individual step. From from parsing command-line arguments to running your commands in tests just like a user would.

- **Composable**: clypi lets you easily reuse arguments across subcommands without having to specify them again.

- **Configurable**: clypi lets you configure almost everything you'd like to configure. You can create your own themes, help pages, error messages, and more!

### Getting started

```bash
uv add clypi  # or `pip install clypi`
```

## 📖 Docs

Read [the API docs](https://github.com/danimelchor/clypi/blob/master/docs/index.md) for examples and a full API reference. If you want a full guide on how to create and distribute your own Python CLI, check our our [tutorial](https://github.com/danimelchor/clypi/blob/master/docs/tutorial.md).

## 🧰 CLI

Read the [docs](https://github.com/danimelchor/clypi/blob/master/docs/index.md#cli)

<!--- mdtest-args -v --threads 2 -->
```python
# examples/cli_basic.py
from clypi import Command, Positional, arg

class Lint(Command):
    files: Positional[tuple[Path, ...]]
    verbose: bool = arg(...)  # Comes from MyCli but I want to use it too

    async def run(self):
        print(f"Linting {self.files=} and {self.verbose=}")

class MyCli(Command):
    """
    my-cli is a very nifty demo CLI tool
    """
    subcommand: Lint | None = None
    threads: int = arg(
        default=4,
        # Built-in parsers for useful validations
        parser=cp.Int(min=1, max=10),
    )
    verbose: bool = arg(
        False,
        help="Whether to show extra logs",
        prompt="Do you want to see extra logs?",
        short="v",  # User can pass in --verbose or -v
    )

    async def run(self):
        print(f"Running the main command with {self.verbose}")

if __name__ == "__main__":
    cli: MyCli = MyCli.parse()
    cli.start()
```

`uv run -m examples.cli run run-seria`

<img width="1696" alt="image" src="https://github.com/user-attachments/assets/3170874d-d120-4b1a-968a-f121e9b8ee53" />



## 🛠️ Configurable

Read the [docs](https://github.com/danimelchor/clypi/blob/master/docs/index.md#configuration)

Clypi lets you configure the app globally. This means that all the styling will be easy,
uniform across your entire app, and incredibly maintainable.

For example, this is how you'd achieve a UI like `uv`'s CLI:

<!--- mdtest -->
```python
from clypi import ClypiConfig, ClypiFormatter, Styler, Theme, configure

configure(
    ClypiConfig(
        theme=Theme(
            usage=Styler(fg="green", bold=True),
            usage_command=Styler(fg="cyan", bold=True),
            usage_args=Styler(fg="cyan"),
            section_title=Styler(fg="green", bold=True),
            subcommand=Styler(fg="cyan", bold=True),
            long_option=Styler(fg="cyan", bold=True),
            short_option=Styler(fg="cyan", bold=True),
            positional=Styler(fg="cyan"),
            placeholder=Styler(fg="cyan"),
            prompts=Styler(fg="green", bold=True),
        ),
        help_formatter=ClypiFormatter(
            boxed=False,
            show_option_types=False,
        ),
    )
)
```

`uv run -m examples.uv add -c`

<img width="1699" alt="image" src="https://github.com/user-attachments/assets/dbf73404-1913-4315-81b6-1b690746680e" />


## 🌈 Colors

Read the [docs](https://github.com/danimelchor/clypi/blob/master/docs/index.md#colors)

<!--- mdtest -->
```python
# demo.py
import clypi

# Style text
print(clypi.style("This is blue", fg="blue"), "and", clypi.style("this is red", fg="red"))

# Print with colors directly
clypi.cprint("Some colorful text", fg="green", reverse=True, bold=True, italic=True)

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
<!--- mdtest -->
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

<!--- mdtest -->
```python
import asyncio
from clypi import spinner

@spinner("Doing work", capture=True)
async def do_some_work():
    await asyncio.sleep(2)

asyncio.run(do_some_work())
```

`uv run -m examples.spinner`

https://github.com/user-attachments/assets/2065b3dd-c73c-4e21-b698-8bf853e8e520


## ❓ Prompting

Read the [docs](https://github.com/danimelchor/clypi/blob/master/docs/index.md#prompt)

First, you'll need to import the `clypi` module:

<!--- mdtest-stdin y -->
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

<!--- mdtest-stdin 23 -->
```python
hours = clypi.prompt(
    "How many hours are there in a year?",
    parser=lambda x: float(x) if isinstance(x, str) else timedelta(days=len(x)),
)
reveal_type(hours)  # Type of "res" is "float | timedelta"
```

#### Why should I care?

Type checking will help you catch issues way earlier in the development cycle. It will also
provide nice autocomplete features in your editor that will make you faster 󱐋.

## 📦 Comparison to other packages

> [!NOTE]
> This section is my (danimelchor's) personal opinion I've gathered during my time
> working with Python CLIs. If you do not agree, please feel free to reach out and I'm
> open to discussing / trying out new tools.

[Argparse](https://docs.python.org/3/library/argparse.html) is the builtin solution for CLIs, but, as expected, it's functionality is very restrictive. It is not very extensible, it's UI is not pretty and very hard to change, lacks type checking and type parsers, and does not offer any modern UI components that we all love.

[Rich](https://rich.readthedocs.io/en/stable/) is too complex and threaded. The vast catalog of UI components they offer is amazing, but it is both easy to get wrong and break the UI, and too complicated/verbose to onboard coworkers to. It's prompting functionality is also quite limited and it does not offer command-line arguments parsing.

[Click](https://click.palletsprojects.com/en/stable/) is too restrictive. It enforces you to use decorators, which is great for locality of behavior but not so much if you're trying to reuse arguments across your application. It is also painful to deal with the way arguments are injected into functions and very easy to miss one, misspell, or get the wrong type. Click is also fully untyped for the core CLI functionality and hard to test.

[Typer](https://github.com/fastapi/typer) seems great! I haven't personally tried it, but I have spent time looking through their docs and code. I think the overall experience is a step up from click's but, at the end of the day, it's built on top of it. Hence, many of the issues are the same: testing is hard, shared contexts are untyped, their built-in type parsing is quite limited, and it does not offer modern features like suggestions on typos. Using `Annotated` types is also very verbose inside function definitions.
