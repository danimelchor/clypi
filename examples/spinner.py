import asyncio

import clypi
from clypi.spinner import Spin, Spinner


async def all_spinners():
    clypi.print(
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
    print()
    title = "EX4 - Example with subprocess"
    async with Spinner(title) as s:
        # Fist subprocess
        proc = await asyncio.create_subprocess_shell(
            "for i in $(seq 1 10); do date && sleep 0.4; done;",
            stdout=asyncio.subprocess.PIPE,
        )

        # Second subprocess
        proc2 = await asyncio.create_subprocess_shell(
            "for i in $(seq 1 20); do echo $RANDOM && sleep 0.2; done;",
            stdout=asyncio.subprocess.PIPE,
        )

        coros = (
            s.pipe(proc.stdout, color="red"),
            s.pipe(proc2.stdout, prefix="(rand)"),
        )
        await asyncio.gather(*coros)


async def main():
    try:
        await all_spinners()
    except asyncio.CancelledError:
        pass

    await subprocess()


if __name__ == "__main__":
    asyncio.run(main())
