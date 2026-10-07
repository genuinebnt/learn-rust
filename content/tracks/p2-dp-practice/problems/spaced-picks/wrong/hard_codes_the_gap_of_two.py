def best_picks(values: list[int], gap: int) -> int:
    best = [0] * (len(values) + 1)
    for i in range(1, len(values) + 1):
        best[i] = max(best[i - 1], values[i - 1] + best[max(0, i - 2)])
    return best[-1]
