### Accessing and changing the configuration

```python
from clypi import ClypiConfig, configure, get_config

# Gets the current config (or a default)
conf = get_config()

# Change the configuration
config = ClypiConfig(help_on_fail=False)
configure(config)
```

### Default config

<!-- mdtest -->
```python
ClypiConfig(
    help_formatter=ClypiFormatter(
        boxed=True,
        show_option_types=True,
    ),
    help_on_fail=True,
    nice_errors=(ClypiException,),
    theme=Theme(
        usage=Styler(fg="yellow"),
        usage_command=Styler(bold=True),
        usage_args=Styler(),
        section_title=Styler(),
        subcommand=Styler(fg="blue", bold=True),
        long_option=Styler(fg="blue", bold=True),
        short_option=Styler(fg="green", bold=True),
        positional=Styler(fg="blue", bold=True),
        placeholder=Styler(fg="blue"),
        type_str=Styler(fg="yellow", bold=True),
        prompts=Styler(fg="blue", bold=True),
    ),
    overflow_style="wrap",
    disable_colors=False,
    fallback_term_width=100,
)
```

Parameters:

- `help_formatter`: the formatter class to use to display the help pages (see [Formatter](./cli.md#formatter))
- `help_on_fail`: whether the help page should be displayed if a user doesn't pass the right params
- `nice_errors`: a list of errors clypi will catch and display neatly
- `theme`: a `Theme` object used to format different styles and colors for help pages, prompts, tracebacks, etc.
- `overflow_style`: either `wrap` or `ellipsis`. If wrap, text that is too long will get wrapped into the next line. If ellipsis, the text will be truncated with an `…` at the end
- <!-- md:version 1.2.11 --> `disable_colors`: whether we should disable all colors and text styles
- <!-- md:version 1.2.11 --> `fallback_term_width`: if we cannot get the current terminal width (e.g.: subprocesses, non-tty devices, etc.), what should the fallback terminal width be (mostly used for displaying errors)
