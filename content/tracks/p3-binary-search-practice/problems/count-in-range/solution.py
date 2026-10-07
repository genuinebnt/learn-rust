def count_in_range(values: list[int], low: int, high: int) -> int:
    def first_where(condition) -> int:
        lo, hi = 0, len(values)
        while lo < hi:
            mid = (lo + hi) // 2
            if condition(values[mid]):
                hi = mid
            else:
                lo = mid + 1
        return lo

    start = first_where(lambda v: v >= low)
    end = first_where(lambda v: v > high)
    return max(0, end - start)
