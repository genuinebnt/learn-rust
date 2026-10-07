def fair_split(values: list[int], parts: int) -> int:
    def pieces_needed(limit: int) -> int:
        pieces, total = 1, 0
        for v in values:
            if total + v > limit:
                pieces += 1
                total = 0
            total += v
        return pieces

    low, high = max(values), sum(values)
    while low < high:
        mid = (low + high) // 2
        if pieces_needed(mid) <= parts:
            high = mid
        else:
            low = mid + 1
    return low
