# Building and distributing your CLIs

To build and distribute you own CLI I recommend you use [uv](https://docs.astral.sh/uv/)..

In this quick walkthrough we'll be creating a CLI called `zit`, a basic clone of git.


## Creating a new CLI

First, you'll want to create a project. For that, follow uv's most up to date documentation
about [creating a new project](https://docs.astral.sh/uv/guides/projects/#project-structure).

A quick summary at the time of writing is:

1. Create a project directory:

    <!-- termynal -->
    ```
    $ mkdir zit
    $ cd zit
    ```

2. Initialize a project:

    <!-- termynal -->
    ```
    $ uv init
    ```
3. Install clypi:

    <!-- termynal -->
    ```
    $ uv add clypi
    ```

4. Code your CLI. `uv` created a `main.py` file but you should create your own python package inside a subdirectory called `zit`. Inside that subdirectory create an empty file called `__init__.py` and a file called `main.py` with the following content:

    <!-- termynal -->
    ```
    $ tree
    .
    ├── README.md
    ├── pyproject.toml
    ├── uv.lock
    └── zit
        ├── __init__.py
        └── main.py
    ```

    ```python
    # zit/main.py
    import clypi
    from clypi import Command, arg

    class Zit(Command):
        """
        A git clone, but much slower ;)
        """
        verbose: bool = arg(False, short="v")

        async def run(self):
            clypi.cprint("Sorry I don't know how to use git, it's too hard!", fg="yellow")
            if self.verbose:
                clypi.cprint("asdkjnbsvaeusbvkajhfnuehfvousadhvuashfqei" * 100)

    def main():
        """
        This will be the entrypoint for our CLI
        """
        zit = Zit.parse()
        zit.start()

    if __name__ == "__main__":
        main()
    ```

5. Test out your new CLI. You can run it locally with:

    <!-- termynal -->
    ```
    $ uv run ./zit/main.py
    ```

6. You'll need to add a build system so that `uv` understands this is a package you want to distribute and people to install. Add the following to your `pyproject.toml`

    ```diff
    + [build-system]
    + requires = ["hatchling"]
    + build-backend = "hatchling.build"
    ```

7. Add an entrypoint to your Python package. This tells Python how to execute your program. Add the following lines to your `pyproject.toml`

    ```diff
    + [project.scripts]
    + zit = "zit.main:main"
    ```

8. Install your package locally and run it

    <!-- termynal -->
   ```
   $ uv pip install -e .
   $ zit --verbose
   Sorry I don't know how to use git, it's too hard! ...
   ```

## Building and distributing your CLI

I highly recommend you follow uv's guide on [building an publishing packages](https://docs.astral.sh/uv/guides/package/#publishing-your-package).

The TLDR is `uv build` then `uv publish`, but you'll want to set up your project with the right metadata. The [official packaging Python guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/) is really good to configure all you'll need for distributing a quality package.


## [Advanced] Pre-built binaries (Shivs 🔪)

[Shiv](https://shiv.readthedocs.io/en/latest/)'s provide an easy way to bundle Python code into an executable file. Shiv's are, essentially, an executable zip file with Python files inside.

To build a shiv with uv and clypi given the above `zit` example, run:

```
$ uvx shiv -c zit -o zit-bin .
$ ./zit-bin --verbose
```

You now have a binary (`zit-bin`) that you can distribute and run like any other binary. You'll have to manually add it to a `$PATH` location though ([What is $PATH?](https://askubuntu.com/a/551993)).
