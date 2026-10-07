def paint_region(picture: list[list[int]], row: int, col: int, colour: int) -> list[list[int]]:
    old = picture[row][col]
    if old == colour:
        return picture
    rows, cols = len(picture), len(picture[0])
    picture[row][col] = colour
    stack = [(row, col)]
    while stack:
        r, c = stack.pop()
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < rows and 0 <= nc < cols and picture[nr][nc] == old:
                picture[nr][nc] = colour
                stack.append((nr, nc))
    return picture
