import typing as t
from dataclasses import dataclass

T = t.TypeVar("T")


class _MISSING_TYPE:
    pass


MISSING = _MISSING_TYPE()


@dataclass
class _PartialConfig(t.Generic[T]):
    default: T | _MISSING_TYPE = MISSING
    default_factory: t.Callable[[], T] | _MISSING_TYPE = MISSING
    help: str | None = None
    short: str | None = None


@dataclass
class _Config(_PartialConfig[T]):
    _type: t.Any = MISSING

    def has_default(self) -> bool:
        return self.default is not MISSING or self.default_factory is not MISSING

    def get_default(self) -> T:
        if not isinstance(self.default, _MISSING_TYPE):
            return self.default

        if t.TYPE_CHECKING:
            assert not isinstance(self.default_factory, _MISSING_TYPE)

        return self.default_factory()

    @classmethod
    def from_partial(cls, partial: _PartialConfig[T], _type: t.Any) -> t.Self:
        return cls(
            _type=_type,
            default=partial.default,
            default_factory=partial.default_factory,
            help=partial.help,
            short=partial.short,
        )


def config(
    default: T | _MISSING_TYPE = MISSING,
    default_factory: t.Callable[[], T] | _MISSING_TYPE = MISSING,
    help: str | None = None,
    short: str | None = None,
) -> T:
    return _PartialConfig(
        default=default,
        default_factory=default_factory,
        help=help,
        short=short,
    )  # type: ignore
