def drains_to_both(heights: list[list[int]]) -> list[tuple[int, int]]:
    rows = len(heights)
    cols = len(heights[0]) if rows else 0

    def uphill_from(starts):
        seen = set(starts)
        stack = list(starts)
        while stack:
            r, c = stack.pop()
            for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in seen and heights[nr][nc] >= heights[r][c]:
                    seen.add((nr, nc))
                    stack.append((nr, nc))
        return seen

    west = uphill_from([(r, 0) for r in range(rows)])
    east = uphill_from([(r, cols - 1) for r in range(rows)])
    return sorted(west & east)
