from bisect import bisect_left


def longest_nesting(boxes: list[tuple[int, int]]) -> int:
    tails = []
    for _, height in sorted(boxes):
        i = bisect_left(tails, height)
        if i == len(tails):
            tails.append(height)
        else:
            tails[i] = height
    return len(tails)
