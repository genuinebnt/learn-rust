def find_in_table(table: list[list[int]], target: int) -> tuple[int, int] | None:
    for r, row in enumerate(table):
        for c, value in enumerate(row):
            if value == target:
                return (r, c)
    return None
