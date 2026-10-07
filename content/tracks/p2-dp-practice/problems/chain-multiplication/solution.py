def cheapest_multiplication(dims: list[int]) -> int:
    n = len(dims) - 1  # number of matrices
    if n < 2:
        return 0
    cost = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            cost[i][j] = min(
                cost[i][k] + cost[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1]
                for k in range(i, j)
            )
    return cost[0][n - 1]
