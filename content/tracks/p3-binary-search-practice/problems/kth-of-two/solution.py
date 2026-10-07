def kth_of_two(a: list[int], b: list[int], k: int) -> int:
    if len(a) > len(b):
        a, b = b, a
    low, high = max(0, k - len(b)), min(k, len(a))
    while low <= high:
        i = (low + high) // 2  # items taken from a
        j = k - i  # items taken from b
        a_last = a[i - 1] if i > 0 else float("-inf")
        a_next = a[i] if i < len(a) else float("inf")
        b_last = b[j - 1] if j > 0 else float("-inf")
        b_next = b[j] if j < len(b) else float("inf")
        if a_last > b_next:
            high = i - 1
        elif b_last > a_next:
            low = i + 1
        else:
            return max(a_last, b_last)
    raise ValueError("k is out of range or the lists are not sorted")
