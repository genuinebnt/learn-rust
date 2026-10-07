def count_in_range(values: list[int], low: int, high: int) -> int:
    return sum(1 for v in values if low <= v <= high)
