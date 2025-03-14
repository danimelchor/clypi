import asyncio
import sys

from clypi import Spin, Spinner, cprint, spinner


async def all_spinners():
    cprint(
        "Displaying all spinner animations." + "\n ↳ Press ctrl+c to skip all examples",
        fg="blue",
        bold=True,
    )

    for i, anim in enumerate(Spin, 1):
        async with Spinner(
            f"{anim.human_name()} spinning animation [{i}/{len(Spin)}]",
            animation=anim,
        ):
            await asyncio.sleep(1.2)


async def subprocess():
    # Example with subprocess
    title = "Example with subprocess"
    async with Spinner(title) as s:
        # Fist subprocess
        proc = await asyncio.create_subprocess_shell(
            "for i in $(seq 1 10); do date && sleep 0.2; done;",
            stdout=asyncio.subprocess.PIPE,
        )

        # Second subprocess
        proc2 = await asyncio.create_subprocess_shell(
            "for i in $(seq 1 20); do echo $RANDOM && sleep 0.1; done;",
            stdout=asyncio.subprocess.PIPE,
        )

        coros = (
            s.pipe(proc.stdout, color="red"),
            s.pipe(proc2.stdout, prefix="(rand)"),
        )
        await asyncio.gather(*coros)


@spinner("Example that captures stdout/stderr", capture=True)
async def captured_with_decorator():
    # Example with subprocess
    for i in range(10):
        if i % 2 == 0:
            cprint("Stdout output", fg="blue")
        else:
            cprint("Stderr output", fg="red", file=sys.stderr)
        await asyncio.sleep(0.3)


async def main():
    # Run all of the spinner animations
    try:
        await all_spinners()
    except asyncio.CancelledError:
        pass

    # Display a subprocess example
    print()
    try:
        await subprocess()
    except asyncio.CancelledError:
        pass

    # Show an example decorator usage with stdout capture
    print()
    await captured_with_decorator()


if __name__ == "__main__":
    asyncio.run(main())
