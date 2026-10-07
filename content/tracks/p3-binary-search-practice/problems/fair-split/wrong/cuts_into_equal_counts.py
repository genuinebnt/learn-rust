def fair_split(values: list[int], parts: int) -> int:
    n = len(values)
    size = -(-n // parts)
    return max(sum(values[i:i + size]) for i in range(0, n, size))
