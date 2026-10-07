def smallest_difference(items: list[int]) -> int:
    return abs(sum(items[::2]) - sum(items[1::2]))
