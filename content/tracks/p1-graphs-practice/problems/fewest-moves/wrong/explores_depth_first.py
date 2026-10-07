def fewest_knight_moves(start: tuple[int, int], goal: tuple[int, int], size: int = 8) -> int:
    if start == goal:
        return 0
    jumps = ((1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1))
    seen = {start}
    stack = [(start, 0)]
    while stack:
        (r, c), moves = stack.pop()
        for dr, dc in jumps:
            nxt = (r + dr, c + dc)
            if 0 <= nxt[0] < size and 0 <= nxt[1] < size and nxt not in seen:
                if nxt == goal:
                    return moves + 1
                seen.add(nxt)
                stack.append((nxt, moves + 1))
    return -1
