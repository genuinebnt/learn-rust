def hop_ways(stones: int) -> int:
    if stones < 0:
        return 0
    three_back, two_back, one_back = 0, 0, 1  # ways to reach stones -2, -1 and 0
    for _ in range(stones):
        three_back, two_back, one_back = two_back, one_back, three_back + two_back + one_back
    return one_back
