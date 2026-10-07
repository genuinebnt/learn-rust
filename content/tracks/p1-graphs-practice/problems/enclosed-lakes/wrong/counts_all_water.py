def enclosed_lake_tiles(land_map: list[str]) -> int:
    return sum(row.count("~") for row in land_map)
