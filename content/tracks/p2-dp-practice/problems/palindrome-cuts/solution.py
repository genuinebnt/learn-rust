def fewest_cuts(s: str) -> int:
    n = len(s)
    if n == 0:
        return 0
    is_pal = [[False] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        for j in range(i, n):
            if s[i] == s[j] and (j - i < 2 or is_pal[i + 1][j - 1]):
                is_pal[i][j] = True
    cuts = [0] * n  # fewest cuts for s[: i + 1]
    for i in range(n):
        if is_pal[0][i]:
            cuts[i] = 0
        else:
            cuts[i] = min(cuts[j - 1] + 1 for j in range(1, i + 1) if is_pal[j][i])
    return cuts[-1]
