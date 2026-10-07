from typing import Callable


def first_bad_build(n: int, is_bad: Callable[[int], bool]) -> int:
    low, high = 1, n - 1
    while low < high:
        mid = (low + high) // 2
        if is_bad(mid):
            high = mid
        else:
            low = mid + 1
    return low if n >= 2 and is_bad(low) else -1
