import asyncio
import re
import shutil
import time
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent

import anyio
import tomllib

import clypi.parsers as cp
from clypi import Command, Positional, Spinner, arg, boxed, cprint, style

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
    base_name = file.as_posix().replace("/", "-").replace(".md", "").lower()

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
                current_test.append(line.removeprefix("> ").removeprefix(">").rstrip())

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
    cprint(style("✔", fg="green") + f" Collected {len(tests)} tests for {file}")
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
    def __init__(self, parallel: int, timeout: int) -> None:
        self.sm = asyncio.Semaphore(parallel)
        self.timeout = timeout

    async def run_test(self, test: Test) -> tuple[str, list[str]]:
        # Save test to temp file
        test_file = MDTEST_DIR / f"{test.name}.py"
        test_file.write_text(test.code)

        commands = [f"uv run --all-extras {test_file}"]
        if test.args:
            commands[0] += f" {test.args}"
        commands.append(f"uv run --all-extras pyright {test_file}")

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
            async with asyncio.timeout(self.timeout):
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

    files: Positional[list[Path] | None] = arg(
        help="The list of markdown files to test",
        default=None,
    )
    parallel: int | None = arg(None, parser=cp.Int(positive=True))
    timeout: int = arg(4, parser=cp.Int(positive=True))
    config: Path = Path("./pyproject.toml")

    def load_config(self):
        if not self.config.exists():
            return Mdtest()

        with open(self.config, "rb") as f:
            conf = tomllib.load(f)

        with suppress(KeyError):
            data = conf["tool"]["mdtest"]
            parallel = int(data["parallel"]) if "parallel" in data else None
            files = [p for f in data["include"] for p in Path().glob(f)]
            return Mdtest(files, parallel)

        return Mdtest()

    async def run(self) -> None:
        conf = self.load_config()
        files = self.files or conf.files
        parallel = self.parallel or conf.parallel or 1
        if files is None:
            cprint("No files to run!", fg="yellow")
            return

        # Setup test dir
        MDTEST_DIR.mkdir(exist_ok=True)

        # Assert each file exists
        for file in files:
            assert file.exists(), f"File {file} does not exist!"

        try:
            # Collect tests
            async with Spinner("Collecting Markdown Tests", capture=True):
                sm = asyncio.Semaphore(parallel)
                per_file = await asyncio.gather(
                    *(
                        parse_file(sm, file)
                        for file in files
                        if not file.parents[-1].name.startswith(".")
                    )
                )
                all_tests = [test for file in per_file for test in file]

            # Run each file
            print()
            code = await Runner(parallel, self.timeout).run_mdtests(all_tests)
        finally:
            # Cleanup
            shutil.rmtree(MDTEST_DIR)

        raise SystemExit(code)


if __name__ == "__main__":
    mdtest = Mdtest.parse()
    mdtest.start()
