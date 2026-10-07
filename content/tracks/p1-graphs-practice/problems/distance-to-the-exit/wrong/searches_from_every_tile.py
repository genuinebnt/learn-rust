from collections import deque


def distance_to_exit(plan: list[str]) -> list[list[int]]:
    rows = len(plan)
    cols = len(plan[0]) if rows else 0
    out = [[-1] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if plan[r][c] == "#":
                continue
            queue, seen = deque([(r, c, 0)]), {(r, c)}
            while queue:
                x, y, d = queue.popleft()
                if plan[x][y] == "E":
                    out[r][c] = d
                    break
                for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= n[0] < rows and 0 <= n[1] < cols and plan[n[0]][n[1]] != "#" and n not in seen:
                        seen.add(n)
                        queue.append((n[0], n[1], d + 1))
    return out
