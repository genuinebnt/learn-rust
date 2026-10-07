def smallest_difference(items: list[int]) -> int:
    a = b = 0
    for item in sorted(items, reverse=True):
        if a <= b:
            a += item
        else:
            b += item
    return abs(a - b)
