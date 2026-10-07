from bisect import bisect_left


def count_in_range(values: list[int], low: int, high: int) -> int:
    return max(0, bisect_left(values, high) - bisect_left(values, low))
