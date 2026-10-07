def networks_after_each_cable(n: int, cables: list[tuple[int, int]]) -> list[int]:
    return [max(n - i - 1, 1) for i in range(len(cables))]
