def hop_ways(stones: int) -> int:
    one_back, two_back = 1, 1
    for _ in range(stones - 1):
        one_back, two_back = one_back + two_back, one_back
    return one_back if stones else 1
