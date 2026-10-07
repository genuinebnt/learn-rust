def fewest_cuts(s: str) -> int:
    n = len(s)
    if n == 0:
        return 0
    is_pal = [[False] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        for j in range(i, n):
            if s[i] == s[j] and (j - i < 2 or is_pal[i + 1][j - 1]):
                is_pal[i][j] = True
    pieces = [0] * (n + 1)
    for i in range(1, n + 1):
        pieces[i] = min(pieces[j] + 1 for j in range(i) if is_pal[j][i - 1])
    return pieces[n]
