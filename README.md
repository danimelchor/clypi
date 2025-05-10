<div align="center">
    <p>
        <img width="50%" src="http://danimelchor.github.io/clypi/assets/logo.png" alt="Clypi logo" />
    <p/>
    <p>Your all-in-one for beautiful, lightweight, prod-ready CLIs</p>
    <a href="https://pypi.org/project/clypi/" target="_blank">
        <img src="https://badge.fury.io/py/clypi.svg" alt="pypi project" />
    </a>
    <a href="https://github.com/danimelchor/clypi?tab=MIT-1-ov-file">
        <img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT license" />
    </a>
    <a href="https://danimelchor.github.io/clypi/learn/getting_started/" target="_blank">
        <img src="https://img.shields.io/badge/docs-latest-purple" alt="docs" />
    </a>
    <a href="https://pypi.org/project/clypi/" target="_blank">
        <img src="https://img.shields.io/pypi/dm/clypi" alt="pypi monthly downloads" />
    </a>
    <img src="https://img.shields.io/github/contributors/danimelchor/clypi" alt="contributors" />
</div>

## 📖 Docs

Read [our docs](https://danimelchor.github.io/clypi/learn/getting_started/) to get started. You can also look at [the API reference](https://danimelchor.github.io/clypi/api/cli/) for examples and a full API reference. Otherwise, feel free to browse the source code in the [GitHub repository](https://github.com/danimelchor/clypi).


## What is clypi?

I've been working with Python-based CLIs for several years with many users and strict quality requirements and always run into the sames problems with the go-to packages. Therefore, I decided to embark on a journey to build a lightweight, intuitive, pretty, and production ready framework. Here are the key features:

- **Type safe**: making use of dataclass-like commands, you can easily specify the types you want for each argument and clypi automatically parses and validates them.
- **Asynchronous**: clypi is built to run asynchronously to provide the best performance possible when re-rendering.
- **Easily testable**: thanks to being type checked and to using it's own parser, clypi let's you test each individual step. From from parsing command-line arguments to running your commands in tests just like a user would.
- **Composable**: clypi lets you easily reuse arguments across subcommands without having to specify them again.
- **Configurable**: clypi lets you configure almost everything you'd like to configure. You can create your own themes, help pages, error messages, and more!

### Define Arguments with Type Annotations
Just like you do with [dataclasses](https://docs.python.org/3/library/dataclasses.html), clypi CLI arguments can defined as class-level type annotations.

<!-- mdtest-args --name foo -->
```python hl_lines="5"
from clypi import Command
from typing_extensions import override

class MyCli(Command):
    name: str  # Automatically parsed as `--name <NAME>`.

    @override
    async def run(self):
        print(f"Hi {self.name}!")

cli = MyCli.parse()
cli.start()
```

### Need more control?

Use our `arg` helper and built-in parsers to define defaults, parsers,
groups, and more!

<!-- mdtest -->
```python hl_lines="5-8"
from clypi import Command, arg
import clypi.parsers as cp

class MyCli(Command):
    threads: int = arg(
        default=4,
        parser=cp.Int(min=1, max=10),  # Restrict to values 1-10
    )

cli = MyCli.parse()
cli.start()
```

### Easily document your CLIs

Using docstrings automatically applies them to your CLI's `--help` page

<!-- mdtest -->
```python hl_lines="4 7"
from clypi import Command, arg

class MyCli(Command):
    """A simple CLI"""
    threads: int = arg(
        default=4,
        help="The number of threads to run the tool with",
    )

cli = MyCli.parse()
cli.start()
```

### Intuitive subcommands (groups of commands)

Just create and compose more clypi commands!

<!-- mdtest-args run -->
```python hl_lines="12"
from clypi import Command, arg

class Lint(Command):
    """Lint a set of files"""
    verbose: bool = arg(inherited=True)  # Inherits the argument def from `MyCli`

class Run(Command):
    """Run a set of files"""

class MyCli(Command):
    """A simple CLI to lint and run files"""
    subcommand: Lint | Run
    verbose: bool = arg(False, help="Whether to show more output")

cli = MyCli.parse()
cli.start()
```

### Getting started

```bash
uv add clypi  # or `pip install clypi`
```

## 🪐 Beautiful by default

Clypi comes with pre-defined themes and modern features like suggestions on typos:

```
$ uv run -m examples.cli run run-seria
```

<img width="1696" alt="image" src="https://github.com/user-attachments/assets/3170874d-d120-4b1a-968a-f121e9b8ee53" />


## 🛠️ Configurable

Clypi lets you configure the app globally. This means that all the styling will be easy,
uniform across your entire app, and incredibly maintainable.

For example, this is how you'd achieve a UI like `uv`'s CLI:

<!-- mdtest -->
```python title="examples/uv/__main__.py"
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

```
$ uv run -m examples.uv add -c
```

<img width="1699" alt="image" src="https://github.com/user-attachments/assets/dbf73404-1913-4315-81b6-1b690746680e" />

Read the [docs](https://danimelchor.github.io/clypi/learn/configuration/) and [API reference](https://danimelchor.github.io/clypi/api/config/).


## 🌈 Colors

Clypi let's you easily print colorful formatted output full:

<!-- mdtest -->
```python title="examples/colors.py"
# demo.py
import clypi

# Print with colors directly
clypi.cprint("Some colorful text", fg="green", reverse=True, bold=True, italic=True)

# Style text
print(clypi.style("This is blue", fg="blue"), "and", clypi.style("this is red", fg="red"))

# Store a styler and reuse it
wrong = clypi.Styler(fg="red", strikethrough=True)
print("The old version said", wrong("Pluto was a planet"))
print("The old version said", wrong("the Earth was flat"))
```

```
$ uv run -m examples.colors
```

<img width="974" alt="image" src="https://github.com/user-attachments/assets/9340d828-f7ce-491c-b0a8-6a666f7b7caf" />

Read the [docs](https://danimelchor.github.io/clypi/learn/beautiful_uis/)


## 🌀 Spinners

You can easily use spinners to indicate progress on long-running tasks:

<!-- mdtest -->
```python title="examples/spinner.py"
import asyncio
from clypi import spinner

@spinner("Doing work", capture=True)
async def do_some_work():
    await asyncio.sleep(2)

asyncio.run(do_some_work())
```

`uv run -m examples.spinner`

https://github.com/user-attachments/assets/2065b3dd-c73c-4e21-b698-8bf853e8e520

Read the [docs](https://danimelchor.github.io/clypi/learn/beautiful_uis/#spinners)


## 🔀 Async by default

`clypi` was built with an async-first mentality. Asynchronous code execution is incredibly
valuable for applications like CLIs where we want to update the UI as we take certain actions behind the scenes.
Most often, these actions can be made asynchronous since they involve things like file manipulation, network requests, subprocesses, etc.

## 🐍 Type-checking

This library is fully type-checked. This means that all types will be correctly inferred
from the arguments you pass in.

In this example your editor will correctly infer the type:

<!-- mdtest-stdin 23 -->
```python
import clypi

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
> This section is my ([danimelchor](https://github.com/danimelchor)'s) personal opinion I've gathered during my time
> working with Python CLIs. If you do not agree, please feel free to reach out and I'm
> open to discussing / trying out new tools.

[Argparse](https://docs.python.org/3/library/argparse.html) is the builtin solution for CLIs, but, as expected, it's functionality is very restrictive. It is not very extensible, it's UI is not pretty and very hard to change, lacks type checking and type parsers, and does not offer any modern UI components that we all love.

[Rich](https://rich.readthedocs.io/en/stable/) is too complex and threaded. The vast catalog of UI components they offer is amazing, but it is both easy to get wrong and break the UI, and too complicated/verbose to onboard coworkers to. It's prompting functionality is also quite limited and it does not offer command-line arguments parsing.

[Click](https://click.palletsprojects.com/en/stable/) is too restrictive. It enforces you to use decorators, which is great for locality of behavior but not so much if you're trying to reuse arguments across your application. It is also painful to deal with the way arguments are injected into functions and very easy to miss one, misspell, or get the wrong type. Click is also fully untyped for the core CLI functionality and hard to test.

[Typer](https://github.com/fastapi/typer) seems great! I haven't personally tried it, but I have spent time looking through their docs and code. I think the overall experience is a step up from click's but, at the end of the day, it's built on top of it. Hence, many of the issues are the same: testing is hard, shared contexts are untyped, their built-in type parsing is quite limited, and it does not offer modern features like suggestions on typos. Using `Annotated` types is also very verbose inside function definitions.
