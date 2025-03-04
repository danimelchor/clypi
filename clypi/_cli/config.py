import typing as t
from dataclasses import asdict, dataclass

from clypi._util import _UNSET, Unset
from clypi.prompts import MAX_ATTEMPTS, Parser

T = t.TypeVar("T")


@dataclass
class PartialConfig(t.Generic[T]):
    parser: Parser[T] | None = None
    default: T | Unset = _UNSET
    default_factory: t.Callable[[], T] | Unset = _UNSET
    help: str | None = None
    short: str | None = None
    prompt: str | None = None
    hide_input: bool = False
    max_attempts: int = MAX_ATTEMPTS

    def has_default(self) -> bool:
        return self.default is not _UNSET or self.default_factory is not _UNSET

    def get_default(self) -> T:
        if not isinstance(self.default, Unset):
            return self.default

        if t.TYPE_CHECKING:
            assert not isinstance(self.default_factory, Unset)

        return self.default_factory()


@dataclass
class Config(t.Generic[T]):
    parser: Parser[T]
    arg_type: t.Any
    default: T | Unset = _UNSET
    default_factory: t.Callable[[], T] | Unset = _UNSET
    help: str | None = None
    short: str | None = None
    prompt: str | None = None
    hide_input: bool = False
    max_attempts: int = MAX_ATTEMPTS

    def has_default(self) -> bool:
        return not isinstance(self.default, Unset) or not isinstance(
            self.default_factory, Unset
        )

    def get_default(self) -> T | Unset:
        if not isinstance(self.default, Unset):
            return self.default
        if not isinstance(self.default_factory, Unset):
            return self.default_factory()
        return _UNSET

    @classmethod
    def from_partial(
        cls, partial: PartialConfig[T], parser: Parser[T], arg_type: t.Any
    ):
        kwargs = asdict(partial)
        kwargs.update(parser=parser, arg_type=arg_type)
        return cls(**kwargs)


def config(
    parser: Parser[T] | None = None,
    default: T | Unset = _UNSET,
    default_factory: t.Callable[[], T] | Unset = _UNSET,
    help: str | None = None,
    short: str | None = None,
    prompt: str | None = None,
    hide_input: bool = False,
    max_attempts: int = MAX_ATTEMPTS,
) -> T:
    return PartialConfig(
        parser=parser,
        default=default,
        default_factory=default_factory,
        help=help,
        short=short,
        prompt=prompt,
        hide_input=hide_input,
        max_attempts=max_attempts,
    )  # type: ignore
