## Colorful outputs

You can easily print colorful text using clypi's `cprint` (for "Colored Print") function.

<!-- mdtest -->
```python title="colors.py"
from clypi import cprint

cprint("Some colorful text", fg="green", bold=True)
cprint("Some more colorful text", fg="red", strikethrough=True)
```

<div class="termy">
    <span data-ty="input">python colors.py</span>
    <span data-ty><b><font color="#40a02b">Some colorful text</font></b></span>
    <span data-ty><s><font color="#d20f39">Some more colorful text</font></s></span>
</div>

You can also style individual pieces of text:

<!-- mdtest -->
```python title="colors.py"
import clypi

print(clypi.style("This is blue", fg="blue"), "and", clypi.style("this is red", fg="red"))
```

<div class="termy">
    <span data-ty="input">python colors.py</span>
    <span data-ty><font color="#1e66f5">This is blue</font> and <font color="#d20f39">this is red</font></span>
</div>

And also create a reusable styler:

<!-- mdtest -->
```python title="colors.py"
import clypi

wrong = clypi.Styler(fg="red", strikethrough=True)
print("The old version said", wrong("Pluto was a planet"))
print("The old version said", wrong("the Earth was flat"))
```

<div class="termy">
    <span data-ty="input">python colors.py</span>
    <span data-ty>The old version said <s><font color="#d20f39">Pluto was a planet</font></s></span>
    <span data-ty>The old version said <s><font color="#d20f39">the Earth was flat</font></s></span>
</div>

## Boxed outputs

<!-- mdtest -->
```python title="boxed.py"
import clypi

print(clypi.boxed("Some boxed text", width=30, align="center"))
```

<div class="termy">
    <span data-ty="input">python boxed.py</span>
<span data-ty>┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃       Some boxed text      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛</span>
</div>

## Stacks


<!-- mdtest -->
```python title="stacks.py"
import clypi

names = clypi.boxed(["Daniel", "Pedro", "Paul"], title="Names", width=15)
colors = clypi.boxed(["Blue", "Red", "Green"], title="Colors", width=15)
print(clypi.stack(names, colors))
```

<div class="termy">
    <span data-ty="input">python stacks.py</span>
<span data-ty>┏━ Names ━━━━━┓  ┏━ Colors ━━━━┓
┃ Daniel      ┃  ┃ Blue        ┃
┃ Pedro       ┃  ┃ Red         ┃
┃ Paul        ┃  ┃ Green       ┃
┗━━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━━┛</span>
</div>

## Separators

<!-- mdtest -->
```python title="separator.py"
import clypi

print(clypi.separator(title="Some title", color="red", width=30))
```

<div class="termy">
    <span data-ty="input">python separator.py</span>
<span data-ty><font color="#d20f39">━━━━━━━━━ Some title ━━━━━━━━━</font></span>
</div>


## Spinners

!!! tip
    Read the [Spinner API docs](../api/components.md#spinner) for more detail into how to use
    this component.

<!-- mdtest -->
```python title="spinner.py" hl_lines="4"
import asyncio
from clypi import spinner

@spinner("Doing work")
async def do_some_work():
    await asyncio.sleep(2)

asyncio.run(do_some_work())
```

<div class="termy">
<span data-ty="input">python spinner.py</span>
<span data-ty><span class="clypi-spinner"></span> Doing work</span>
</div>


You can also use it as a context manager:
<!-- mdtest -->
```python title="spinner.py" hl_lines="5"
import asyncio
from clypi import Spinner

async def main():
    async with Spinner("Doing something", capture=True):
        await asyncio.sleep(2)

asyncio.run(main())
```
<div class="termy">
<span data-ty="input">python spinner.py</span>
<span data-ty><span class="clypi-spinner"></span> Doing something</span>
</div>
