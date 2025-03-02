import typing as t
from dataclasses import dataclass

T = t.TypeVar("T")


class _MISSING_TYPE:
    pass


MISSING = _MISSING_TYPE()


@dataclass
class _Config(t.Generic[T]):
    default: T | _MISSING_TYPE = MISSING
    default_factory: t.Callable[[], T] | _MISSING_TYPE = MISSING
    help: str | None = None

    def get_default(self) -> T:
        if not isinstance(self.default, _MISSING_TYPE):
            return self.default
        if not isinstance(self.default_factory, _MISSING_TYPE):
            return self.default_factory()
        raise ValueError("No default provided for field")

    def has_default(self) -> bool:
        return self.default is not MISSING or self.default_factory is not MISSING


def config(
    default: T | _MISSING_TYPE = MISSING,
    default_factory: t.Callable[[], T] | _MISSING_TYPE = MISSING,
    help: str | None = None,
) -> T:
    return _Config(default, default_factory, help)  # type: ignore
