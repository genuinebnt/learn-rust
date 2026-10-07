def enclosed_lake_tiles(land_map: list[str]) -> int:
    rows = len(land_map)
    cols = len(land_map[0]) if rows else 0
    return sum(
        1
        for r in range(1, rows - 1)
        for c in range(1, cols - 1)
        if land_map[r][c] == "~"
    )
