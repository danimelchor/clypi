import typing as t
from dataclasses import dataclass, field

from clypi._prompts import MAX_ATTEMPTS, prompt
from clypi._util import UNSET, Unset
from clypi.parsers import Parser

T = t.TypeVar("T")


def gen_impl(__f: str) -> t.Callable[..., t.Any]:
    def _impl(self: "DeferredValue[t.Any]", *args: t.Any, **kwargs: t.Any) -> t.Any:
        return getattr(self.__get__(None), __f)(*args, **kwargs)

    return _impl


ALL_DUNDERS = (
    "__add__",
    "__eq__",
    "__gt__",
    "__gte__",
    "__len__",
    "__lt__",
    "__lte__",
    "__ne__",
    "__or__",
    "__repr__",
    "__set__",
    "__str__",
    "__sub__",
)


@dataclass
class DeferredValue(t.Generic[T]):
    parser: Parser[T]
    prompt: str
    default: T | Unset = UNSET
    default_factory: t.Callable[[], T] | Unset = UNSET
    hide_input: bool = False
    max_attempts: int = MAX_ATTEMPTS

    _value: T | Unset = field(init=False, default=UNSET)

    def __get__(self, instance: t.Any, owner: t.Any = None) -> T:
        if self._value is UNSET:
            self._value = prompt(
                self.prompt,
                default=self.default,
                default_factory=self.default_factory,
                hide_input=self.hide_input,
                max_attempts=self.max_attempts,
                parser=self.parser,
            )
        return self._value

    # Autogen all dunder methods to trigger __get__
    for dunder in ALL_DUNDERS:
        locals()[dunder] = gen_impl(dunder)
