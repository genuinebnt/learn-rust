def integer_sqrt(n: int) -> int:
    r = 0
    while (r + 1) * (r + 1) <= n:
        r += 1
    return r
