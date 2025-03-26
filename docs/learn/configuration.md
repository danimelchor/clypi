Clypi lets you configure the app globally. This means that all the styling will be easy,
uniform across your entire app, and incredibly maintainable.

For example, this is how you'd achieve a UI like `uv`'s CLI:

<!-- mdtest -->
```python
from clypi import ClypiConfig, ClypiFormatter, Styler, Theme, configure

theme: Theme = Theme(
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
)

config = ClypiConfig(
    theme=theme,
    help_formatter=ClypiFormatter(
        boxed=False,
        show_option_types=False,
    ),
)

configure(config)
```

`uv run -m examples.uv add -c`

<img width="1699" alt="image" src="https://github.com/user-attachments/assets/dbf73404-1913-4315-81b6-1b690746680e" />

!!! tip
    Read the [Configuration API reference](../api/config.md) docs for more information into the available options.
