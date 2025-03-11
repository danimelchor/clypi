import asyncio
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent

from clypi import Command, Positional, Spinner, arg, boxed, print
from clypi.colors import style

MDTEST_DIR = Path.cwd() / "mdtest"
PREAMBLE = """\
import clypi
import v6e
from pathlib import Path
from typing import reveal_type
from clypi import *
"""


class TestFailed(Exception):
    pass


@dataclass
class Test:
    code: str
    args: str
    stdin: str


def normalize_code(code: str) -> str:
    code = dedent(code)
    code = PREAMBLE + code
    return code


def parse_file(text: str) -> list[Test]:
    tests: list[Test] = []

    in_test, current_test, args, stdin = False, [], "", ""
    for line in text.split("\n"):
        # End of a code block
        if "```" in line and current_test:
            tests.append(
                Test(
                    code=normalize_code("\n".join(current_test[1:])),
                    args=args,
                    stdin=stdin + "\n",
                )
            )
            in_test, current_test, args, stdin = False, [], "", ""

        # We're in a test, accumulate all lines
        elif in_test:
            current_test.append(line.removeprefix("> "))

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


async def run_test(test: Test, idx: int):
    # Save test to temp file
    test_file = MDTEST_DIR / f"md_test_{idx}.py"
    test_file.write_text(test.code)

    # Run the test
    file_rel = test_file.relative_to(Path.cwd())
    command = f"uv run --all-extras {file_rel}"
    if test.args:
        command += f" {test.args}"

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
        return idx, True

    # If there was an error, pretty print it
    print(f"\n\nError running '{command}'\n", fg="red", bold=True)
    print(boxed(test.code, title="Code"))

    if stdout.decode():
        print()
        print(boxed(stdout.decode(), title="Stdout"))

    if stderr.decode():
        print()
        print(boxed(stderr.decode(), title="Stderr"))

    return idx, False


async def run_mdtest(file: Path) -> bool:
    text = file.read_text()
    tests = parse_file(text)

    # Run all tests
    async with Spinner(f"Running {file.name} mdtest") as s:
        coros = [run_test(test, idx=idx) for idx, test in enumerate(tests, 1)]

        any_err = False
        for task in asyncio.as_completed(coros):
            idx, ok = await task
            if ok:
                s.log(style("✔", fg="green") + f" Finished test {idx}")
            else:
                any_err = True
                s.log(style("×", fg="red") + f" Finished test {idx}")

        if any_err:
            await s.fail()
            return False

    return True


class MdTest(Command):
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

        # Run each file
        for file in self.files:
            ok = await run_mdtest(file.resolve())
            if not ok:
                break

            print()

        # Cleanup
        shutil.rmtree(MDTEST_DIR)


if __name__ == "__main__":
    mdtest = MdTest.parse()
    mdtest.start()
