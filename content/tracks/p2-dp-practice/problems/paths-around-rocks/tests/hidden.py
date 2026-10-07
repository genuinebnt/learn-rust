import random

from anneal_prelude import check, ensure
from solution import count_paths


def test_rock_blocks_a_row():
    check('count_paths(["...", "###", "..."])', count_paths(["...", "###", "..."]), 0)


def test_one_row():
    check('count_paths(["....."])', count_paths(["....."]), 1)


def test_rock_in_the_first_row():
    check('count_paths([".#.", "..."])', count_paths([".#.", "..."]), 1)


def test_rock_in_the_first_column():
    check('count_paths(["..", "#.", ".."])', count_paths(["..", "#.", ".."]), 1)


def test_one_column_with_a_rock():
    check('count_paths([".", "#", "."])', count_paths([".", "#", "."]), 0)


def test_bigger_open_grid():
    check('count_paths(["...." for _ in range(4)])', count_paths(["...." for _ in range(4)]), 20)


def reference(plan):
    rows, cols = len(plan), len(plan[0]) if plan else 0
    if rows == 0 or cols == 0:
        return 0

    def go(r, c):
        if r >= rows or c >= cols or plan[r][c] == "#":
            return 0
        if (r, c) == (rows - 1, cols - 1):
            return 1
        return go(r + 1, c) + go(r, c + 1)

    return go(0, 0)


def test_random_maps_against_trying_every_route():
    rng = random.Random(8)
    for _ in range(300):
        rows, cols = rng.randint(1, 5), rng.randint(1, 5)
        plan = ["".join(rng.choice("...#") for _ in range(cols)) for _ in range(rows)]
        check(f"count_paths({plan})", count_paths(plan), reference(plan))


def test_a_large_open_map_is_exact():
    from math import comb
    check("count_paths(30 x 30 of open ground)", count_paths(["." * 30] * 30), comb(58, 29))
