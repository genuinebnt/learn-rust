def fewest_knight_moves(start: tuple[int, int], goal: tuple[int, int], size: int = 8) -> int:
    dr, dc = abs(start[0] - goal[0]), abs(start[1] - goal[1])
    return (dr + dc + 2) // 3
