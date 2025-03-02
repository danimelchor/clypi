from pathlib import Path

import tomllib

f = open(Path.home() / ".pypirc", "rb")
data = tomllib.load(f)["pypi"]["password"]
print(data)
