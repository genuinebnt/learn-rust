def find_in_table(table: list[list[int]], target: int) -> tuple[int, int] | None:
    if not table or not table[0]:
        return None
    cols = len(table[0])
    low, high = 0, len(table) * cols - 1
    while low <= high:
        mid = (low + high) // 2
        row, col = divmod(mid, cols)
        if table[row][col] == target:
            return (row, col)
        if table[row][col] < target:
            low = mid + 1
        else:
            high = mid - 1
    return None
