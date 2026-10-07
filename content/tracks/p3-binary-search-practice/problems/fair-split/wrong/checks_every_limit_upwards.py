def fair_split(values: list[int], parts: int) -> int:
    limit = max(values)
    while True:
        pieces, total = 1, 0
        for v in values:
            if total + v > limit:
                pieces += 1
                total = 0
            total += v
        if pieces <= parts:
            return limit
        limit += 1
