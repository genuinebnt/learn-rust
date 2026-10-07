def fewest_bills(bills: list[tuple[int, int]], amount: int) -> int:
    INF = float("inf")
    fewest = [0] + [INF] * amount
    for value, count in bills:
        updated = fewest[:]
        for a in range(amount + 1):
            for k in range(1, count + 1):
                if k * value > a:
                    break
                if fewest[a - k * value] + k < updated[a]:
                    updated[a] = fewest[a - k * value] + k
        fewest = updated
    return -1 if fewest[amount] == INF else fewest[amount]
