def count_rooms(plan: list[str]) -> int:
    rows = len(plan)
    cols = len(plan[0]) if rows else 0
    seen = set()
    rooms = 0
    for r in range(rows):
        for c in range(cols):
            if plan[r][c] != "." or (r, c) in seen:
                continue
            rooms += 1
            stack = [(r, c)]
            seen.add((r, c))
            while stack:
                row, col = stack.pop()
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < rows and 0 <= nc < cols and plan[nr][nc] == "." and (nr, nc) not in seen:
                            seen.add((nr, nc))
                            stack.append((nr, nc))
    return rooms
