import asyncio

from term.spinner import Spinner


async def long_running_task(
    spinner: Spinner,
    num_seconds: int,
    title: str,
    done_after: int | None = None,
    raise_after: int | None = None,
):
    sleep = 0.1
    for i in range(round(num_seconds / sleep)):
        await asyncio.sleep(sleep)
        done = (i + 1) * sleep
        if done % 1 == 0:
            spinner.log(f"It's been {done:.1f} seconds")
        spinner.title = title + f" ({num_seconds-done:.1f} left)"

        if done_after is not None and done > done_after:
            spinner.done(title + "- Done early :)")
            break

        if raise_after is not None and done > raise_after:
            raise RuntimeError("Woops something went wrong")


async def main2():
    # Basic example
    title = "EX1 - Running for 4 seconds"
    async with Spinner(title) as s:
        await long_running_task(spinner=s, num_seconds=4, title=title)

    # Success exit manually example
    print()
    title = "EX2 - Running for 4 seconds"
    async with Spinner(title) as s:
        await long_running_task(
            spinner=s,
            num_seconds=4,
            title=title,
            done_after=2,
        )

    # Failure exit example
    print()
    title = "EX3 - Running for 4 seconds"
    try:
        async with Spinner(title) as s:
            await long_running_task(
                spinner=s,
                num_seconds=4,
                title=title,
                raise_after=2,
            )
    except RuntimeError as e:
        print(f"Caught {e}")


async def main():
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

        await asyncio.gather(
            s.pipe(proc.stdout, color="red"),
            s.pipe(proc2.stdout, prefix="(rand)"),
        )


if __name__ == "__main__":
    asyncio.run(main())
