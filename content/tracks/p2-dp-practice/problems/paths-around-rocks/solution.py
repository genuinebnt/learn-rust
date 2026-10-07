def count_paths(plan: list[str]) -> int:
    if not plan or not plan[0]:
        return 0
    cols = len(plan[0])
    row = [0] * cols
    for r, line in enumerate(plan):
        for c, cell in enumerate(line):
            if cell == "#":
                row[c] = 0
            elif r == 0 and c == 0:
                row[c] = 1
            elif c > 0:
                row[c] += row[c - 1]
    return row[-1]
