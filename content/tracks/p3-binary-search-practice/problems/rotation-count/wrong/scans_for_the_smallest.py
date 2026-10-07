def rotation_count(values: list[int]) -> int:
    return values.index(min(values)) if values else 0
