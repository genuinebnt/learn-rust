def fewest_bills(bills: list[tuple[int, int]], amount: int) -> int:
    INF = float("inf")
    fewest = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for value, _ in bills:
            if value <= a and fewest[a - value] + 1 < fewest[a]:
                fewest[a] = fewest[a - value] + 1
    return -1 if fewest[amount] == INF else fewest[amount]
