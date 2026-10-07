def paint_region(picture: list[list[int]], row: int, col: int, colour: int) -> list[list[int]]:
    result = [line[:] for line in picture]
    old = result[row][col]
    if old == colour:
        return result
    rows, cols = len(result), len(result[0])
    result[row][col] = colour
    stack = [(row, col)]
    while stack:
        r, c = stack.pop()
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < rows and 0 <= nc < cols and result[nr][nc] == old:
                result[nr][nc] = colour
                stack.append((nr, nc))
    return result
