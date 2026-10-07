def count_splits(digits: str, biggest: int) -> int:
    ways = [1] + [0] * len(digits)
    for i in range(1, len(digits) + 1):
        for j in (i - 1, i - 2):
            if j >= 0 and digits[j] != "0" and int(digits[j:i]) <= biggest:
                ways[i] += ways[j]
    return ways[-1]
