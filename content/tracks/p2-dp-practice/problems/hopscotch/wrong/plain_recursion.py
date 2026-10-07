def hop_ways(stones: int) -> int:
    if stones < 0:
        return 0
    if stones == 0:
        return 1
    return hop_ways(stones - 1) + hop_ways(stones - 2) + hop_ways(stones - 3)
