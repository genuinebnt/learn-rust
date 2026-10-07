def best_picks(values: list[int], gap: int) -> int:
    best = [0] * (len(values) + 1)  # best[i]: most value from the first i items
    for i in range(1, len(values) + 1):
        take = values[i - 1] + best[max(0, i - gap)]
        best[i] = max(best[i - 1], take)
    return best[-1]
