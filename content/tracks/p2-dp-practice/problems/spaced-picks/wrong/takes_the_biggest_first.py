def best_picks(values: list[int], gap: int) -> int:
    blocked = set()
    total = 0
    for i in sorted(range(len(values)), key=lambda k: -values[k]):
        if i not in blocked:
            total += values[i]
            blocked.update(range(i - gap + 1, i + gap))
    return total
