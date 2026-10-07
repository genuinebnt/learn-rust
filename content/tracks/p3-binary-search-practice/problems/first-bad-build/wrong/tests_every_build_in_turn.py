from typing import Callable


def first_bad_build(n: int, is_bad: Callable[[int], bool]) -> int:
    for build in range(1, n + 1):
        if is_bad(build):
            return build
    return -1
