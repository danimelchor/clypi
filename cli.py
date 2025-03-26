from clypi import Command, arg


class Cli(Command):
    single_threaded: bool = arg(False)
    num_cores: int = arg(defer=True, prompt="How many CPU cores do you want to use")

    async def run(self):
        print(
            "Running single theaded:", self.single_threaded
        )  # << will not prompt yet...
        if self.single_threaded:
            # if we never access num_threads in this if condition, we will
            # never prompt!
            print("Running single threaded...")
        else:
            threads = self.num_cores // 4  # << we prompt here!
            print("Running with threads: ", threads)


if __name__ == "__main__":
    cmd = Cli.parse()  # << will not prompt yet...
    cmd.start()  # << will not prompt yet...
