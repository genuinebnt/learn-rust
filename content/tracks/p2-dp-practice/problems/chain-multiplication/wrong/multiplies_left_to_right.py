def cheapest_multiplication(dims: list[int]) -> int:
    n = len(dims) - 1
    if n < 2:
        return 0
    return sum(dims[0] * dims[k] * dims[k + 1] for k in range(1, n))
