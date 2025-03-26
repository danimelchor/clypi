I've been working with Python-based CLIs for several years with many users and strict quality requirements and always run into the sames problems with the go-to packages:

- [Argparse](https://docs.python.org/3/library/argparse.html) is the builtin solution for CLIs, but, as expected, it's functionality is very restrictive. It is not very extensible, it's UI is not pretty and very hard to change, lacks type checking and type parsers, and does not offer any modern UI components that we all love.

- [Rich](https://rich.readthedocs.io/en/stable/) is too complex and threaded. The vast catalog of UI components they offer is amazing, but it is both easy to get wrong and break the UI, and too complicated/verbose to onboard coworkers to. It's prompting functionality is also quite limited and it does not offer command-line arguments parsing.

- [Click](https://click.palletsprojects.com/en/stable/) is too restrictive. It enforces you to use decorators, which is great for locality of behavior but not so much if you're trying to reuse arguments across your application. It is also painful to deal with the way arguments are injected into functions and very easy to miss one, misspell, or get the wrong type. Click is also fully untyped for the core CLI functionality and hard to test.

- [Typer](https://github.com/fastapi/typer) seems great! I haven't personally tried it, but I have spent time looking through their docs and code. I think the overall experience is a step up from click's but, at the end of the day, it's built on top of it. Hence, many of the issues are the same: testing is hard, shared contexts are untyped, their built-in type parsing is quite limited, and it does not offer modern features like suggestions on typos. Using `Annotated` types is also very verbose inside function definitions.

> [!WARNING]
> This section is my ([danimelchor](https://github.com/danimelchor)'s) personal opinion I've gathered during my time
> working with Python CLIs. If you do not agree, please feel free to reach out and I'm
> open to discussing / trying out new tools.
