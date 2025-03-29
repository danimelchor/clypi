# Based on squidfunk/mkdocs-material badges
# https://github.com/squidfunk/mkdocs-material/blob/master/material/overrides/hooks/shortcodes.py


from __future__ import annotations

import re
import typing as t
from re import Match

VERSION_ICON = "material-tag-outline"


def on_page_markdown(markdown: str, **kwargs: t.Any):
    return re.sub(r"<!-- md:(\w+)(.*?) -->", _gen_badge, markdown, flags=re.I | re.M)


def _gen_badge(match: Match[t.Any]):
    name, arg_ls = match.groups()
    args: list[str] = [a for a in arg_ls.strip().split(" ")]
    if name == "version":
        return _version_badge(args[0])

    raise Exception(f"Unknown name for helper badge: {name}")


def _badge(icon: str, text: str = "", icon_tooltip: str | None = None):
    tooltip = f'{{ title="{icon_tooltip}" }}' if icon_tooltip else ""
    return "".join(
        [
            '<span class="clypi-badge">',
            *(
                [f'<span class="clypi-badge-icon">:{icon}:{tooltip}</span>']
                if icon
                else []
            ),
            *([f'<span class="clypi-badge-text">{text}</span>'] if text else []),
            "</span>",
        ]
    )


def _version_badge(version: str):
    assert re.match(r"^\d+\.\d+\.\d+$", version), f"Unexpected version {version}"
    return _badge(icon=VERSION_ICON, text=f"{version}", icon_tooltip="Minimum version")
