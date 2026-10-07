def count_splits(digits: str, biggest: int) -> int:
    longest = len(str(biggest))
    ways = [1] + [0] * len(digits)
    for i in range(1, len(digits) + 1):
        for j in range(max(0, i - longest), i):
            piece = digits[j:i]
            if piece[0] != "0" and int(piece) <= biggest:
                ways[i] += ways[j]
    return ways[-1]
