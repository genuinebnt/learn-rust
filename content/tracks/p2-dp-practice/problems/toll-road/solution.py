def cheapest_trip(tolls: list[int]) -> int:
    n = len(tolls)
    if n == 0:
        return 0
    cost = [0] * n
    cost[0] = tolls[0]
    for i in range(1, n):
        cost[i] = tolls[i] + min(cost[j] for j in range(max(0, i - 3), i))
    return min(cost[max(0, n - 3):])
