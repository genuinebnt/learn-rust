def cheapest_trip(tolls: list[int]) -> int:
    n = len(tolls)
    if n == 0:
        return 0
    i, paid = 0, tolls[0]
    while i < n - 3:
        step = min(range(1, 4), key=lambda k: tolls[i + k])
        i += step
        paid += tolls[i]
    return paid
