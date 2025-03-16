import typing as t
from dataclasses import dataclass, field

from clypi._data.dunders import ALL_DUNDERS
from clypi._prompts import MAX_ATTEMPTS, prompt
from clypi._util import UNSET, Unset
from clypi.parsers import Parser

T = t.TypeVar("T")


def gen_impl(__f: str) -> t.Callable[..., t.Any]:
    def _impl(self: "DeferredValue[t.Any]", *args: t.Any, **kwargs: t.Any) -> t.Any:
        return getattr(self.__get__(None), __f)(*args, **kwargs)

    return _impl


@dataclass
class DeferredValue(t.Generic[T]):
    parser: Parser[T]
    prompt: str
    default: T | Unset = UNSET
    default_factory: t.Callable[[], T] | Unset = UNSET
    hide_input: bool = False
    max_attempts: int = MAX_ATTEMPTS

    _value: T | Unset = field(init=False, default=UNSET)

    def __set_name__(self, owner: t.Any, name: str):
        self.__name__ = name

    def __get__(self, obj: t.Any, objtype: t.Any = None) -> T:
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
    # NOTE: I hate having to do this but I did not find how to trigger
    # the evaluation of a descriptor when a dunder method is called on it
    for dunder in ALL_DUNDERS:
        locals()[dunder] = gen_impl(dunder)
