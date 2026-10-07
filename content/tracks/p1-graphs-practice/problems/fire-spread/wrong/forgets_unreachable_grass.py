from collections import deque


def minutes_to_burn(plan: list[str]) -> int:
    rows = len(plan)
    cols = len(plan[0]) if rows else 0
    grass = {(r, c) for r in range(rows) for c in range(cols) if plan[r][c] == "."}
    queue = deque((r, c) for r in range(rows) for c in range(cols) if plan[r][c] == "F")
    minutes = 0
    while queue and grass:
        minutes += 1
        for _ in range(len(queue)):
            r, c = queue.popleft()
            for n in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if n in grass:
                    grass.remove(n)
                    queue.append(n)
    return minutes
