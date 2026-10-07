def dice_ways(dice: int, faces: int, total: int) -> int:
    ways = [1] + [0] * total
    for _ in range(dice):
        updated = [0] * (total + 1)
        for t in range(total + 1):
            for face in range(0, faces):
                if face > t:
                    break
                updated[t] += ways[t - face]
        ways = updated
    return ways[total]
