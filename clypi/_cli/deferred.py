import typing as t
from dataclasses import dataclass, field

from clypi._prompts import MAX_ATTEMPTS, prompt
from clypi._util import UNSET, Unset
from clypi.parsers import Parser

T = t.TypeVar("T")


@dataclass
class DeferredValue(t.Generic[T]):
    parser: Parser[T]
    prompt: str
    default: T | Unset = UNSET
    default_factory: t.Callable[[], T] | Unset = UNSET
    hide_input: bool = False
    max_attempts: int = MAX_ATTEMPTS

    _value: T | Unset = field(init=False, default=UNSET)

    def get_default_or_missing(self) -> T | Unset:
        if not isinstance(self.default, Unset):
            return self.default
        if not isinstance(self.default_factory, Unset):
            return self.default_factory()
        return UNSET

    def __get__(self, instance: t.Any, owner: t.Any = None) -> T:
        if self._value is UNSET:
            self._value = prompt(
                self.prompt,
                default=self.get_default_or_missing(),
                hide_input=self.hide_input,
                max_attempts=self.max_attempts,
                parser=self.parser,
            )
        return self._value

    def __set__(self, instance: t.Any, value: T):
        self._value = value

    def __repr__(self) -> str:
        return self.__get__(self).__repr__()
