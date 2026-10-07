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
            seen.add((r, c))
            stack = [(r, c)]
            while stack:
                row, col = stack.pop()
                for nr, nc in ((row + 1, col), (row - 1, col), (row, col + 1), (row, col - 1)):
                    if 0 <= nr < rows and 0 <= nc < cols and plan[nr][nc] == "." and (nr, nc) not in seen:
                        seen.add((nr, nc))
                        stack.append((nr, nc))
    return rooms
