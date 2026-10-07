def smallest_difference(items: list[int]) -> int:
    total = sum(items)
    reachable = 1  # a bitset: bit s is set when some subset adds up to s
    for item in items:
        reachable |= reachable << item
    best = total
    for s in range(total // 2 + 1):
        if reachable >> s & 1:
            best = min(best, total - 2 * s)
    return best
