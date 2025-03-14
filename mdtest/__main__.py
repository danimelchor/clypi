import asyncio
import re
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent

import anyio

from clypi import Command, Positional, Spinner, arg, boxed, cprint
from clypi._colors import style

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


async def parse_file(sm: asyncio.Semaphore, file: Path) -> list[Test]:
    tests: list[Test] = []
    base_name = (
        file.relative_to(Path.cwd())
        .as_posix()
        .replace("/", "-")
        .replace(".md", "")
        .lower()
    )

    # Wait for turn
    await sm.acquire()

    async with await anyio.open_file(file, "r") as f:
        current_test: list[str] = []
        in_test, args, stdin = False, "", ""
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

    sm.release()
    return tests


def error_msg(test: Test, stdout: str | None = None, stderr: str | None = None) -> str:
    error: list[str] = []
    error.append(style(f"\n\nError running test {test.name!r}\n", fg="red", bold=True))
    error.append(boxed(test.orig, title="Code", width="max"))

    if stdout:
        error.append("")
        error.append(boxed(stdout.strip(), title="Stdout", width="max"))

    if stderr:
        error.append("")
        error.append(boxed(stderr.strip(), title="Stderr", width="max"))

    return "\n".join(error)


class Runner:
    def __init__(self) -> None:
        self.sm = asyncio.Semaphore(5)

    async def run_test(self, test: Test) -> tuple[str, list[str]]:
        # Save test to temp file
        test_file = MDTEST_DIR / f"{test.name}.py"
        test_file.write_text(test.code)

        file_rel = test_file.relative_to(Path.cwd())
        commands = [f"uv run --all-extras {file_rel}"]
        if test.args:
            commands[0] += f" {test.args}"
        commands.append(f"uv run --all-extras pyright {file_rel}")

        # Run the test
        errors: list[str] = []
        for command in commands:
            # Await the subprocess to run it
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await proc.communicate(test.stdin.encode())
            except:
                proc.terminate()
                raise

            # If no errors, return
            if proc.returncode == 0:
                continue

            # If there was an error, pretty print it
            errors.append(error_msg(test, stdout.decode(), stderr.decode()))

        if not errors:
            return test.name, []
        return test.name, errors

    async def run_test_with_timeout(self, test: Test) -> tuple[str, list[str]]:
        await self.sm.acquire()
        start = time.perf_counter()
        try:
            async with asyncio.timeout(4):
                return await self.run_test(test)
        except TimeoutError:
            error = error_msg(
                test,
                stderr=f"Test timed out after {time.perf_counter() - start:.3f}s",
            )
            return test.name, [error]
        finally:
            self.sm.release()

    async def run_mdtests(self, tests: list[Test]) -> int:
        errors: list[str] = []
        async with Spinner("Running Markdown Tests", capture=True) as s:
            coros = [self.run_test_with_timeout(test) for test in tests]
            for task in asyncio.as_completed(coros):
                idx, err = await task
                if not err:
                    cprint(style("✔", fg="green") + f" Finished test {idx}")
                else:
                    errors.extend(err)
                    cprint(style("×", fg="red") + f" Finished test {idx}")

            if errors:
                await s.fail()

        for err in errors:
            cprint(err)

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

        try:
            # Collect tests
            async with Spinner("Collecting Markdown Tests"):
                sm = asyncio.Semaphore(5)
                per_file = await asyncio.gather(
                    *(parse_file(sm, file) for file in self.files)
                )
                all_tests = [test for file in per_file for test in file]

            # Run each file
            code = await Runner().run_mdtests(all_tests)
        finally:
            # Cleanup
            shutil.rmtree(MDTEST_DIR)

        raise SystemExit(code)


if __name__ == "__main__":
    mdtest = Mdtest.parse()
    mdtest.start()
