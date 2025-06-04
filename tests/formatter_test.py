from contextlib import suppress
from io import StringIO
from textwrap import dedent

from clypi import Command, Positional, arg, get_config
from tests.prompt_test import replace_stdout


def _assert_stdout_matches(stdout: StringIO, expected: str):
    __tracebackhide__ = True
    stdout_str = stdout.getvalue()
    assert stdout_str.strip() == expected.strip()


def _get_help(
    cmd: type[Command], subcmds: list[str] = [], error: bool = False
) -> StringIO:
    with replace_stdout() as stdout:
        with suppress(SystemExit):
            cmd.parse(
                ["--sdasdasjkdasd"]
                if error
                else [
                    *subcmds,
                    "--help",
                ]
            )

        return stdout


class TestCase:
    def setup_method(self):
        conf = get_config()
        conf.disable_colors = True
        conf.fallback_term_width = 50

    def test_basic_example(self):
        class Main(Command):
            pass

        stdout = _get_help(Main)
        _assert_stdout_matches(
            stdout,
            dedent(
                """
                Usage: main
                """
            ),
        )

    def test_basic_example_with_error(self):
        class Main(Command):
            pass

        stdout = _get_help(Main, error=True)
        _assert_stdout_matches(
            stdout,
            dedent(
                """
                Usage: main

                ┏━ Error ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                ┃ Unknown option '--sdasdasjkdasd'               ┃
                ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                """
            ),
        )

    def test_basic_example_with_all_args(self):
        class Subcmd(Command):
            pass

        class Main(Command):
            subcommand: Subcmd
            positional: Positional[str]
            flag: bool = False
            option: int = 5

        stdout = _get_help(Main)
        _assert_stdout_matches(
            stdout,
            dedent(
                """
                Usage: main [POSITIONAL] [OPTIONS] COMMAND
                
                ┏━ Subcommands ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                ┃ subcmd                                         ┃
                ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                
                ┏━ Arguments ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                ┃ [POSITIONAL]                                   ┃
                ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                
                ┏━ Options ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                ┃ --flag                                         ┃
                ┃ --option <OPTION>                              ┃
                ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                """
            ),
        )

    def test_basic_example_with_all_args_and_help(self):
        class Subcmd(Command):
            pass

        class Main(Command):
            subcommand: Subcmd
            positional: Positional[str] = arg(help="Some positional arg")
            flag: bool = arg(False, help="Some flag")
            option: int = arg(5, help="Some option")

        stdout = _get_help(Main)
        _assert_stdout_matches(
            stdout,
            dedent(
                """
                Usage: main [POSITIONAL] [OPTIONS] COMMAND
                
                ┏━ Subcommands ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                ┃ subcmd                                         ┃
                ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                
                ┏━ Arguments ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                ┃ [POSITIONAL]  Some positional arg              ┃
                ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                
                ┏━ Options ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                ┃ --flag             Some flag                   ┃
                ┃ --option <OPTION>  Some option                 ┃
                ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                """
            ),
        )

    def test_basic_example_for_subcommand(self):
        class Subcmd(Command):
            pass

        class Main(Command):
            subcommand: Subcmd
            positional: Positional[str] = arg(help="Some positional arg")
            flag: bool = arg(False, help="Some flag")
            option: int = arg(5, help="Some option")

        stdout = _get_help(Main, subcmds=["subcmd"])
        _assert_stdout_matches(
            stdout,
            dedent(
                """
                Usage: main subcmd
                """
            ),
        )

    def test_basic_example_group_option(self):
        class Main(Command):
            option: int = arg(5)
            option2: int = arg(5, group="foo")

        stdout = _get_help(Main)
        _assert_stdout_matches(
            stdout,
            dedent(
                """
                Usage: main [OPTIONS]
               
                ┏━ Options ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                ┃ --option <OPTION>                              ┃
                ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
               
                ┏━ Foo options ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                ┃ --option2 <OPTION2>                            ┃
                ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                """
            ),
        )

    def test_basic_example_flag_extras(self):
        class Main(Command):
            option: bool = arg(False, short="o", negative="no_option")

        stdout = _get_help(Main)
        _assert_stdout_matches(
            stdout,
            dedent(
                """
                Usage: main [OPTIONS]
               
                ┏━ Options ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                ┃ -o, --option/--no-option                       ┃
                ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                """
            ),
        )

    def test_basic_example_hidden_option(self):
        class Main(Command):
            option: int = arg(5, hidden=True)

        stdout = _get_help(Main)
        _assert_stdout_matches(
            stdout,
            dedent(
                """
                Usage: main [OPTIONS]
                """
            ),
        )

    def test_basic_example_with_long_help(self):
        class Main(Command):
            positional: Positional[str] = arg(
                help="Some positional arg with an insanely long description that will definitely not fit!"
            )

        stdout = _get_help(Main)
        print(stdout.getvalue())
        _assert_stdout_matches(
            stdout,
            dedent(
                """
                Usage: main [POSITIONAL]
                
                ┏━ Arguments ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                ┃ [POSITIONAL]  Some positional arg with an      ┃
                ┃               insanely long description that   ┃
                ┃               will definitely not fit!         ┃
                ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                """
            ),
        )

    def test_basic_example_with_inherited_fields(self):
        class Subcmd(Command):
            positional: Positional[str] = arg(inherited=True)
            option: int = arg(inherited=True)

        class Main(Command):
            subcommand: Subcmd
            positional: Positional[str] = arg(help="Some positional arg")
            option: int = arg(5, help="Some option")

        stdout = _get_help(Main, subcmds=["subcmd"])
        print(stdout.getvalue())
        _assert_stdout_matches(
            stdout,
            dedent(
                """
                Usage: main subcmd [POSITIONAL] [OPTIONS]
                
                ┏━ Arguments ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                ┃ [POSITIONAL]  Some positional arg              ┃
                ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                
                ┏━ Options ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                ┃ --option <OPTION>  Some option                 ┃
                ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                """
            ),
        )
