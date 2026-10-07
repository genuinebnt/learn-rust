def cheapest_multiplication(dims: list[int]) -> int:
    dims = list(dims)
    total = 0
    while len(dims) > 2:
        best = min(range(1, len(dims) - 1), key=lambda k: dims[k - 1] * dims[k] * dims[k + 1])
        total += dims[best - 1] * dims[best] * dims[best + 1]
        del dims[best]
    return total
