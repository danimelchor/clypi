from dataclasses import dataclass, field

from clypi._cli.arg_config import Nargs


@dataclass
class CurrentCtx:
    name: str = ""
    nargs: Nargs = 0
    max_nargs: Nargs = 0

    _collected: list[str] = field(init=False, default_factory=list)

    def has_more(self) -> bool:
        if isinstance(self.nargs, float | int):
            return self.nargs > 0
        return True

    def needs_more(self) -> bool:
        if isinstance(self.nargs, float | int):
            return self.nargs > 0
        elif self.nargs == "+":
            return True
        return False

    def collect(self, item: str) -> None:
        if isinstance(self.nargs, float | int):
            self.nargs -= 1
        elif self.nargs == "+":
            self.nargs = "*"

        self._collected.append(item)

    @property
    def collected(self) -> str | list[str]:
        if self.max_nargs == 1:
            return self._collected[0]
        return self._collected

    def __bool__(self) -> bool:
        return bool(self.name)
