import typing as t
from dataclasses import asdict, dataclass

T = t.TypeVar("T")


class _MISSING_TYPE:
    pass


MISSING = _MISSING_TYPE()


@dataclass
class _PartialConfig(t.Generic[T]):
    parser: t.Callable[[t.Any], T] | None = None
    default: T | _MISSING_TYPE = MISSING
    default_factory: t.Callable[[], T] | _MISSING_TYPE = MISSING
    help: str | None = None
    short: str | None = None

    def has_default(self) -> bool:
        return self.default is not MISSING or self.default_factory is not MISSING

    def get_default(self) -> T:
        if not isinstance(self.default, _MISSING_TYPE):
            return self.default

        if t.TYPE_CHECKING:
            assert not isinstance(self.default_factory, _MISSING_TYPE)

        return self.default_factory()


@dataclass
class _Config(t.Generic[T]):
    parser: t.Callable[[t.Any], T]
    _type: t.Any
    default: T | _MISSING_TYPE = MISSING
    default_factory: t.Callable[[], T] | _MISSING_TYPE = MISSING
    help: str | None = None
    short: str | None = None

    def has_default(self) -> bool:
        return self.default is not MISSING or self.default_factory is not MISSING

    def get_default(self) -> T:
        if not isinstance(self.default, _MISSING_TYPE):
            return self.default

        if t.TYPE_CHECKING:
            assert not isinstance(self.default_factory, _MISSING_TYPE)

        return self.default_factory()

    @classmethod
    def from_partial(
        cls, partial: _PartialConfig, parser: t.Callable[[t.Any], T], _type: t.Any
    ):
        kwargs = asdict(partial)
        kwargs.update(parser=parser, _type=_type)
        return cls(**kwargs)


def config(
    parser: t.Callable[[t.Any], T] | None = None,
    default: T | _MISSING_TYPE = MISSING,
    default_factory: t.Callable[[], T] | _MISSING_TYPE = MISSING,
    help: str | None = None,
    short: str | None = None,
) -> T:
    return _PartialConfig(
        parser=parser,
        default=default,
        default_factory=default_factory,
        help=help,
        short=short,
    )  # type: ignore
