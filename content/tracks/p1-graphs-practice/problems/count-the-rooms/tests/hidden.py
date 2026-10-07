import random

from anneal_prelude import check, ensure
from solution import count_rooms


def test_border_rooms():
    check('count_rooms([".#.", "###", ".#."])', count_rooms([".#.", "###", ".#."]), 4)


def test_snake():
    check('count_rooms(["...", "##.", "...", ".##", "..."])', count_rooms(["...", "##.", "...", ".##", "..."]), 1)


def test_checkerboard():
    check('count_rooms(["#.#.", ".#.#", "#.#.", ".#.#"])', count_rooms(["#.#.", ".#.#", "#.#.", ".#.#"]), 8)


def test_rows_of_walls():
    check('count_rooms(["...", "###", "..."])', count_rooms(["...", "###", "..."]), 2)


def test_column_of_walls():
    check('count_rooms([".#.", ".#.", ".#."])', count_rooms([".#.", ".#.", ".#."]), 2)


def test_empty_rows():
    check('count_rooms(["", ""])', count_rooms(["", ""]), 0)


def reference(plan):
    cells = {(r, c) for r, row in enumerate(plan) for c, ch in enumerate(row) if ch == "."}
    parent = {x: x for x in cells}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for r, c in cells:
        for n in ((r + 1, c), (r, c + 1)):
            if n in cells:
                parent[find(n)] = find((r, c))
    return len({find(x) for x in cells})


def test_random_plans_against_a_union_find_reference():
    rng = random.Random(7)
    for _ in range(200):
        rows, cols = rng.randint(1, 7), rng.randint(1, 7)
        plan = ["".join(rng.choice("..#") for _ in range(cols)) for _ in range(rows)]
        check(f"count_rooms({plan})", count_rooms(plan), reference(plan))


def test_a_big_room_does_not_overflow_the_stack():
    plan = ["." * 300] * 300
    check("count_rooms(300 x 300 of floor)", count_rooms(plan), 1)
