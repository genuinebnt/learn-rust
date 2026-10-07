def rotation_count(values: list[int]) -> int:
    if not values:
        return 0
    low, high = 0, len(values) - 1
    while low < high:
        mid = (low + high) // 2
        if values[mid] > values[high]:
            low = mid + 1
        else:
            high = mid
    return low
