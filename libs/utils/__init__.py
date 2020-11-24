from typing import Iterator, Sized


def batch(iterable: Sized, n: int = 1) -> Iterator:
    length = len(iterable)
    for ndx in range(0, length, n):
        yield iterable[ndx:min(ndx + n, length)]
