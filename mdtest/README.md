# mdtest

I want to make sure almost every code block in the clypi repository is runnable and has no typos. For that,
 I've created a tiny CLI I called `md-test` (using clypi obviously). The idea is simple, any Python code block annotated as an `mdtest` (see below) can be run to ensure it's correctly defined.


 <img width="1055" alt="image" src="https://github.com/user-attachments/assets/0265b00c-9958-4561-a3a8-7c59b9665b73" />



## Creating Markdown Tests


### Non-input tests
````
<!--- mdtest -->
```python
assert 1 + 1 == 2, f"Expected 1 + 1 to equal 2"
```
````

### Command-line tests
````
<!--- mdtest-args --foo 2 -->
```python
import sys
assert sys.argv[1] == '--foo', f"Expected the first arg to be 'foo'"
```
````

### User input tests
````
<!--- mdtest-stdin hello world -->
```python
import sys
assert input() == 'hello world', f"Expected the stdin to be 'hello world'"
```
````

## Running Markdown Tests

```
uv run mdtest
```

