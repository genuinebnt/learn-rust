import heapq


def kth_of_two(a: list[int], b: list[int], k: int) -> int:
    for index, value in enumerate(heapq.merge(a, b), start=1):
        if index == k:
            return value
    raise ValueError("k is out of range")
