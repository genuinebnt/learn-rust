def min_capacity(weights: list[int], days: int) -> int:
    def days_needed(capacity: int) -> int:
        used, load = 1, 0
        for w in weights:
            if load + w > capacity:
                used += 1
                load = 0
            load += w
        return used

    low, high = max(weights), sum(weights)
    while low < high:
        mid = (low + high) // 2
        if days_needed(mid) <= days:
            high = mid
        else:
            low = mid + 1
    return low
