def enclosed_lake_tiles(land_map: list[str]) -> int:
    rows = len(land_map)
    cols = len(land_map[0]) if rows else 0
    water = {(r, c) for r in range(rows) for c in range(cols) if land_map[r][c] == "~"}
    stack = [(r, c) for (r, c) in water if r in (0, rows - 1) or c in (0, cols - 1)]
    draining = set(stack)
    while stack:
        r, c = stack.pop()
        for n in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if n in water and n not in draining:
                draining.add(n)
                stack.append(n)
    return len(water) - len(draining)
