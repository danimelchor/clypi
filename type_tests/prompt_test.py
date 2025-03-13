import typing as t
from pathlib import Path

import clypi
import clypi.parsers as cp

t.assert_type(clypi.confirm("A"), bool)
t.assert_type(clypi.prompt("A"), str)
t.assert_type(clypi.prompt("A", parser=int), int)
t.assert_type(clypi.prompt("A", parser=cp.Path()), Path)
t.assert_type(
    clypi.prompt("A", parser=cp.Union(cp.Path(), cp.Int())),
    Path | int,
)
