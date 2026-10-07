from collections import deque


def distance_to_exit(plan: list[str]) -> list[list[int]]:
    rows = len(plan)
    cols = len(plan[0]) if rows else 0
    dist = [[-1] * cols for _ in range(rows)]
    queue = deque()
    for r in range(rows):
        for c in range(cols):
            if plan[r][c] == "E" and not queue and all(x == -1 or x != 0 for row in dist for x in row):
                dist[r][c] = 0
                queue.append((r, c))
    while queue:
        r, c = queue.popleft()
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < rows and 0 <= nc < cols and plan[nr][nc] != "#" and dist[nr][nc] == -1:
                dist[nr][nc] = dist[r][c] + 1
                queue.append((nr, nc))
    return dist
