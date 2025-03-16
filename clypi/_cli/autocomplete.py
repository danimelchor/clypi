from __future__ import annotations

import os
import shlex
import sys
import typing as t
from abc import ABC, abstractmethod
from pathlib import Path
from textwrap import dedent

from clypi import _colors
from clypi._cli import arg_parser

if t.TYPE_CHECKING:
    from clypi._cli.main import Command

_CLYPI_CURRENT_ARGS = "_CLYPI_CURRENT_ARGS"


class AutocompleteInstaller(ABC):
    """
    The basic idea for autocomplete with clypi is that we'll configure
    the shell to call the users' CLI with whatever the user has typed so far. Then,
    we will try to parse as much as we can from what the user gave us, and when we can't
    anymore we just list the options the user has. At that point, we will have traversed
    enough into the right subcommand the user wants to autocomplete
    """

    def __init__(self, command: type[Command]) -> None:
        self.name = command.prog()
        self._options = list(command.options().values())
        self._subcommands = list(command.subcommands().values())

    @abstractmethod
    def path(self) -> Path: ...

    @abstractmethod
    def script(self) -> str: ...

    def list_arguments(self) -> None:
        sys.stdout.write(
            "\n".join(
                [
                    *[s.prog() for s in self._subcommands if s],
                    *[p.display_name for p in self._options],
                ]
            ),
        )
        sys.stdout.flush()
        sys.exit(0)

    @property
    def gen_args(self) -> str:
        # We use get_current_args to pass in what the user has typed so far
        get_current_args = f"{_CLYPI_CURRENT_ARGS}=(commandline -cp)"
        return f"env {get_current_args} {self.name}"

    def install(self) -> None:
        p = self.path()
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w") as f:
            f.write(self.script())
        self.post_install(p)
        _colors.cprint(
            "Successfully installed autocomplete for fish", fg="green", bold=True
        )
        _colors.cprint(f"  󰘍 {self.path()}")
        sys.exit(0)

    def post_install(self, path: Path):
        return None


class FishInstaller(AutocompleteInstaller):
    def path(self) -> Path:
        return Path.home() / ".config" / "fish" / "completions" / f"{self.name}.fish"

    def script(self) -> str:
        return f'complete -c {self.name} --no-files -a "({self.gen_args})" -n "{self.gen_args}"'


class BashInstaller(AutocompleteInstaller):
    def path(self) -> Path:
        base = Path("/etc/bash_completion.d/")
        if Path("/usr/local/etc/bash_completion.d").exists():
            base = Path("/usr/local/etc/bash_completion.d")
        return base / self.name

    def post_install(self, path: Path):
        bashrc = Path.home() / ".bashrc"
        with open(bashrc, "a+") as f:
            for line in f.readline():
                if str(path) in line:
                    return

            f.write(f"source '{path}'")

    def script(self) -> str:
        return dedent(
            """
            _complete_%(name)s() {
                _script_commands=$(env %(env_var)s="${COMP_WORDS[*]}" $1)
                local cur="${COMP_WORDS[COMP_CWORD]}"
                COMPREPLY=( $(compgen -W "${_script_commands}" -- ${cur}) )
            }

            complete -o default -F _complete_%(name)s %(name)s
            """
            % dict(name=self.name, env_var=_CLYPI_CURRENT_ARGS)
        ).strip()


class ZshInstaller(AutocompleteInstaller):
    def path(self) -> Path:
        return Path.home() / ".zfunc" / f"_{self.name}"

    def post_install(self, path: Path):
        autoload_comp = "fpath+=~/.zfunc; autoload -Uz compinit; compinit"
        zshrc = Path.home() / ".zshrc"
        with open(zshrc, "a+") as f:
            for line in f.readline():
                if autoload_comp in line:
                    return

            f.write(autoload_comp)

    def script(self) -> str:
        return dedent(
            """
            #compdef %(name)s

            _complete_%(name)s() {
              IFS=$'\\n' completions=( $(env %(env_var)s="${words[1,$CURRENT]}" %(name)s) )

              local -a filtered
              for item in "${completions[@]}"; do
                if [[ $item == ${words[$CURRENT]}* ]]; then
                  filtered+=("$item")
                fi
              done
              compadd -U -V unsorted -a filtered
            }

            compdef _complete_%(name)s %(name)s
            """
            % dict(name=self.name, env_var=_CLYPI_CURRENT_ARGS)
        ).strip()


def get_installer(command: type[Command]) -> AutocompleteInstaller:
    shell = Path(os.environ["SHELL"]).name
    if shell == "fish":
        return FishInstaller(command)
    if shell == "bash":
        return BashInstaller(command)
    if shell == "zsh":
        return ZshInstaller(command)
    raise ValueError(f"Autocomplete is not supported for shell '{shell}'")


def get_autocomplete_args() -> list[str] | None:
    if args := os.environ.get(_CLYPI_CURRENT_ARGS):
        return shlex.split(args)[1:]
    return None


def list_arguments(command: type[Command]):
    get_installer(command).list_arguments()


def requested_autocomplete_install(args: t.Sequence[str]) -> bool:
    if not args:
        return False
    parsed = arg_parser.parse_as_attr(args[-1])
    return parsed.is_long_opt() and parsed.value == "install_autocomplete"


def install_autocomplete(command: type[Command]):
    get_installer(command).install()
