def find_a_peak(values: list[int]) -> int:
    low, high = 0, len(values) - 1
    while low < high:
        mid = (low + high) // 2
        if values[mid] < values[mid + 1]:
            low = mid + 1
        else:
            high = mid
    return low
