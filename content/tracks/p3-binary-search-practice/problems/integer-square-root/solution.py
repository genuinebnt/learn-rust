def integer_sqrt(n: int) -> int:
    low, high = 0, n
    while low < high:
        mid = (low + high + 1) // 2
        if mid * mid <= n:
            low = mid
        else:
            high = mid - 1
    return low
