import asyncio
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent

import anyio

from clypi import Command, Positional, Spinner, arg, boxed, print
from clypi.colors import style

MDTEST_DIR = Path.cwd() / ".mdtest"
PREAMBLE = """\
import clypi
import clypi.parsers as cp
from pathlib import Path
from typing import reveal_type
from clypi import *
from enum import Enum
import asyncio
from datetime import datetime, timedelta
"""


class TestFailed(Exception):
    pass


@dataclass
class Test:
    name: str
    orig: str
    code: str
    args: str
    stdin: str


async def parse_file(file: Path) -> list[Test]:
    tests: list[Test] = []
    base_name = (
        file.relative_to(Path.cwd())
        .as_posix()
        .replace("/", "-")
        .replace(".md", "")
        .lower()
    )

    async with await anyio.open_file(file, "r") as f:
        in_test, current_test, args, stdin = False, [], "", ""
        async for line in f:
            # End of a code block
            if "```" in line and current_test:
                code = "\n".join(current_test[1:])
                tests.append(
                    Test(
                        name=f"{base_name}-{len(tests)}",
                        orig=dedent(code),
                        code=PREAMBLE + dedent(code),
                        args=args,
                        stdin=stdin + "\n",
                    )
                )
                in_test, current_test, args, stdin = False, [], "", ""

            # We're in a test, accumulate all lines
            elif in_test:
                current_test.append(line.removeprefix("> ").rstrip())

            # Mdtest arg definition
            elif g := re.search("<!--- mdtest-args (.*) -->", line):
                args = g.group(1)
                in_test = True

            # Mdtest stdin definition
            elif g := re.search("<!--- mdtest-stdin (.*) -->", line):
                stdin = g.group(1)
                in_test = True

            # Mdtest generic definition
            elif g := re.search("<!--- mdtest -->", line):
                in_test = True

    return tests


async def run_test(test: Test) -> tuple[str, str]:
    # Save test to temp file
    test_file = MDTEST_DIR / f"{test.name}.py"
    test_file.write_text(test.code)

    file_rel = test_file.relative_to(Path.cwd())
    commands = [f"uv run --all-extras {file_rel}"]
    if test.args:
        commands[0] += f" {test.args}"
    commands.append(f"uv run --all-extras pyright {file_rel}")

    # Run the test
    errors = []
    for command in commands:
        # Await the subprocess to run it
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate(test.stdin.encode())

        # If no errors, return
        if proc.returncode == 0:
            continue

        # If there was an error, pretty print it
        error = []
        error.append(
            style(f"\n\nError running test {test.name!r}\n", fg="red", bold=True)
        )
        error.append(boxed(test.orig, title="Code", width="max"))

        if stdout.decode():
            error.append("")
            error.append(boxed(stdout.decode().strip(), title="Stdout", width="max"))

        if stderr.decode():
            error.append("")
            error.append(boxed(stderr.decode().strip(), title="Stderr", width="max"))

        errors.append(error)

    if not errors:
        return test.name, ""
    return test.name, "\n\n".join("\n".join(err) for err in errors)


async def run_mdtests(tests: list[Test]) -> int:
    errors = []
    async with Spinner("Running Markdown Tests") as s:
        coros = [run_test(test) for test in tests]
        for task in asyncio.as_completed(coros):
            idx, err = await task
            if not err:
                s.log(style("✔", fg="green") + f" Finished test {idx}")
            else:
                errors.append(err)
                s.log(style("×", fg="red") + f" Finished test {idx}")

        if errors:
            await s.fail()

    for err in errors:
        print(err)

    return 1 if errors else 0


class Mdtest(Command):
    """
    Run python code embedded in markdown files to ensure it's
    runnable.
    """

    files: Positional[list[Path]] = arg(
        help="The list of markdown files to test",
        default_factory=lambda: list(Path.cwd().glob("**/*.md")),
    )

    async def run(self) -> None:
        # Setup test dir
        MDTEST_DIR.mkdir(exist_ok=True)

        # Assert each file exists
        for file in self.files:
            assert file.exists(), f"File {file} does not exist!"

        # Collect tests
        async with Spinner("Collecting Markdown Tests"):
            per_file = await asyncio.gather(*(parse_file(file) for file in self.files))
            all_tests = [test for file in per_file for test in file]

        # Run each file
        code = await run_mdtests(all_tests)

        # Cleanup
        shutil.rmtree(MDTEST_DIR)

        raise SystemExit(code)


if __name__ == "__main__":
    mdtest = Mdtest.parse()
    mdtest.start()
