def dice_ways(dice: int, faces: int, total: int) -> int:
    ways = [1] + [0] * total
    for face in range(1, faces + 1):
        for t in range(face, total + 1):
            ways[t] += ways[t - face]
    return ways[total] if dice else int(total == 0)
