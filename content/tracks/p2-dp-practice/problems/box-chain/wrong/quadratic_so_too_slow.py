def longest_nesting(boxes: list[tuple[int, int]]) -> int:
    order = sorted(boxes, key=lambda b: (b[0], -b[1]))
    best = [1] * len(order)
    for i in range(len(order)):
        for j in range(i):
            if order[j][0] < order[i][0] and order[j][1] < order[i][1]:
                best[i] = max(best[i], best[j] + 1)
    return max(best, default=0)
