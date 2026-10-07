def paint_region(picture: list[list[int]], row: int, col: int, colour: int) -> list[list[int]]:
    result = [line[:] for line in picture]
    old = result[row][col]
    rows, cols = len(result), len(result[0])
    stack = [(row, col)]
    steps = 0
    while stack:
        r, c = stack.pop()
        result[r][c] = colour
        steps += 1
        if steps > 10_000_000:
            raise RuntimeError("never ends")
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < rows and 0 <= nc < cols and picture[nr][nc] == old and (nr, nc) not in stack:
                stack.append((nr, nc))
    return result
