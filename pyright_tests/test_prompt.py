import typing as t
from pathlib import Path

import clypi

t.assert_type(clypi.prompt("A", parser=int), int)
t.assert_type(clypi.prompt("A", parser=lambda x: Path(x)), Path)
t.assert_type(clypi.prompt("A", parser=lambda x: Path(x) if x else None), Path | None)
