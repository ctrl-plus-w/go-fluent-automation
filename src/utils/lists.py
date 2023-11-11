from typing import Callable, Iterable, TypeVar, Any, Iterator

_T = TypeVar("_T")
_S = TypeVar("_S")


def _f(__function: Callable[[_T], Any], __iterable: Iterable[_T]) -> Iterator[_T]:
    return list(filter(__function, __iterable))


def _m(
    __func: Callable[..., _S],
    *iterables: Iterable[Any],
) -> Iterator[_S]:
    return list(map(__func, *iterables))
