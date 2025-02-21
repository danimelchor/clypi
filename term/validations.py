from __future__ import annotations

import re
import typing as t
from abc import ABC, ABCMeta, abstractmethod

from typing_extensions import override


T = t.TypeVar("T")


class ValidationException(Exception):
    pass


class Validation(ABC, t.Generic[T]):
    @abstractmethod
    def validate(self, x: T) -> None: ...

    def __call__(self, x: T):
        self.validate(x)

    def test(self, x: T) -> bool:
        try:
            self(x)
        except ValidationException:
            return False
        return True

    def __and__(self, other: Validation[T]) -> _Intersection[T]:
        return _Intersection(self, other)

    def __or__(self, other: Validation[T]) -> _Union[T]:
        return _Union(self, other)

    @override
    def __repr__(self):
        return self.__class__.__name__


class Custom(Validation[T]):
    def __init__(self, func: t.Callable[[T], None]):
        self.func = func
        super().__init__()

    @override
    def validate(self, x: T) -> None:
        try:
            self.func(x)
        except Exception as e:
            raise ValidationException(str(e))

    @override
    def __repr__(self):
        return f"CustomValidation({self.func})"


class _Intersection(Validation[T]):
    def __init__(self, left: Validation[T], right: Validation[T]):
        self.left = left
        self.right = right
        super().__init__()

    @override
    def validate(self, x: T) -> None:
        left_err = right_err = None

        try:
            self.left(x)
        except ValidationException as e:
            left_err = e

        try:
            self.right(x)
        except ValidationException as e:
            right_err = e

        if left_err and right_err:
            raise ValidationException(f"{left_err} and {right_err}")
        if left_err:
            raise left_err
        if right_err:
            raise right_err

    @override
    def __repr__(self):
        return f"{self.left} & {self.right}"


class _Union(Validation[T]):
    def __init__(self, left: Validation[T], right: Validation[T]):
        self.left = left
        self.right = right
        super().__init__()

    @override
    def validate(self, x: T) -> None:
        left_err = right_err = None

        try:
            self.left(x)
        except ValidationException as e:
            left_err = e

        try:
            self.right(x)
        except ValidationException as e:
            right_err = e

        if left_err and right_err:
            raise ValidationException(f"{left_err} or {right_err}")

    @override
    def __repr__(self):
        return f"{self.left} | {self.right}"


class Comparable(metaclass=ABCMeta):
    def __le__(self, other: t.Any) -> bool: ...

    def __ge__(self, other: t.Any) -> bool: ...

    def __lt__(self, other: t.Any) -> bool: ...

    def __gt__(self, other: t.Any) -> bool: ...


C = t.TypeVar("C", bound=int | float)


class Range(Validation[C]):
    def __init__(self, start: C, end: C):
        self.start = start
        self.end = end
        super().__init__()

    @override
    def validate(self, x: C) -> None:
        if not self.start <= x <= self.end:
            raise ValidationException(
                f"Value must be between {self.start} and {self.end} (got {x})"
            )

    @override
    def __repr__(self):
        return f"Range({self.start}, {self.end})"


class Lt(Validation[C]):
    def __init__(self, limit: C):
        self.limit = limit
        super().__init__()

    @override
    def validate(self, x: C) -> None:
        if not x < self.limit:
            raise ValidationException(f"Value must be less than {self.limit} (got {x})")

    @override
    def __repr__(self):
        return f"Lt({self.limit})"


class Lte(Validation[C]):
    def __init__(self, limit: C):
        self.limit = limit
        super().__init__()

    @override
    def validate(self, x: C) -> None:
        if not x <= self.limit:
            raise ValidationException(
                f"Value must be less than or equal to {self.limit} (got {x})"
            )

    @override
    def __repr__(self):
        return f"Lte({self.limit})"


class Gt(Validation[C]):
    def __init__(self, limit: C):
        self.limit = limit
        super().__init__()

    @override
    def validate(self, x: C) -> None:
        if not x > self.limit:
            raise ValidationException(f"Value must be greater than {self.limit} (got {x})")

    @override
    def __repr__(self):
        return f"Gt({self.limit})"


class Gte(Validation[C]):
    def __init__(self, limit: C):
        self.limit = limit
        super().__init__()

    @override
    def validate(self, x: C) -> None:
        if not x >= self.limit:
            raise ValidationException(
                f"Value must be greater than or equal to {self.limit} (got {x})"
            )

    @override
    def __repr__(self):
        return f"Gte({self.limit})"


class StartsWith(Validation[str]):
    def __init__(self, prefix: str):
        self.prefix = prefix
        super().__init__()

    @override
    def validate(self, x: str) -> None:
        if not x.startswith(self.prefix):
            raise ValidationException(f"Value must start with {self.prefix!r} (got {x!r})")

    @override
    def __repr__(self):
        return f"StartsWith({self.prefix!r})"


class EndsWith(Validation[str]):
    def __init__(self, suffix: str):
        self.suffix = suffix
        super().__init__()

    @override
    def validate(self, x: str) -> None:
        if not x.endswith(self.suffix):
            raise ValidationException(f"Value must end with {self.suffix!r} (got {x!r})")

    @override
    def __repr__(self):
        return f"EndsWith({self.suffix!r})"


class ReMatch(Validation[str]):
    def __init__(self, pattern: str):
        self.pattern = re.compile(pattern)
        super().__init__()

    @override
    def validate(self, x: str) -> None:
        if not self.pattern.match(x):
            raise ValidationException(f"Value must match pattern {self.pattern!r} (got {x!r})")

    @override
    def __repr__(self):
        return f"ReMatch({self.pattern!r})"


class ReSearch(Validation[str]):
    def __init__(self, pattern: str):
        self.pattern = re.compile(pattern)
        super().__init__()

    @override
    def validate(self, x: str) -> None:
        if not self.pattern.search(x):
            raise ValidationException(f"Value must contain pattern {self.pattern!r} (got {x!r})")

    @override
    def __repr__(self):
        return f"ReSearch({self.pattern!r})"


class Choices(Validation[T]):
    def __init__(self, choices: t.Sequence[T]):
        self.choices = choices
        super().__init__()

    @override
    def validate(self, x: T) -> None:
        if x not in self.choices:
            raise ValidationException(f"Value must be one of {self.choices} (got {x})")

    @override
    def __repr__(self):
        return f"Choices({self.choices})"


ValidationType: t.TypeAlias = t.Callable[[T], None] | Validation[T]


def parse_validation(validation: ValidationType[T]) -> Validation[T]:
    # NOTE: We unfortunately cannot match validation to Validation[T]
    # so we need a cast
    if isinstance(validation, Validation):
        return t.cast(Validation[T], validation)

    return Custom(validation)
