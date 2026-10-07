from math import comb


def count_paths(plan: list[str]) -> int:
    if not plan or not plan[0]:
        return 0
    if plan[0][0] == "#" or plan[-1][-1] == "#":
        return 0
    return comb(len(plan) + len(plan[0]) - 2, len(plan) - 1)
