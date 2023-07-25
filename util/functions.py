from collections.abc import Callable
from typing import Iterable, TypeVar

T = TypeVar('T')


def safe_reduce(fn: Callable[[T, T], T], iterable: Iterable[T], start: T = None) -> int:
    iterator = iter(iterable)

    accumulator = start
    for current in iterator:
        if current is None:
            continue
        if accumulator is None:
            accumulator = current
        else:
            accumulator = fn(accumulator, current)

    return accumulator
