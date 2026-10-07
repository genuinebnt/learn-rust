import random
from collections import deque

from anneal_prelude import check, ensure
from solution import distance_to_exit


def test_nearest_of_two():
    check('distance_to_exit(["E.....E"])', distance_to_exit(["E.....E"]), [[0, 1, 2, 3, 2, 1, 0]])


def test_detour_around_a_wall():
    check('distance_to_exit(["E.#", "..#", "..."])', distance_to_exit(["E.#", "..#", "..."]), [[0, 1, -1], [1, 2, -1], [2, 3, 4]])


def test_exit_surrounded_by_walls():
    check('distance_to_exit(["#E#", "###"])', distance_to_exit(["#E#", "###"]), [[-1, 0, -1], [-1, -1, -1]])


def test_column():
    check('distance_to_exit([".", ".", "E", "."])', distance_to_exit([".", ".", "E", "."]), [[2], [1], [0], [1]])


def test_exit_in_a_corner():
    check('distance_to_exit(["E.", ".."])', distance_to_exit(["E.", ".."]), [[0, 1], [1, 2]])


def test_a_wall_splits_the_plan():
    check('distance_to_exit(["E#.", "E#."])', distance_to_exit(["E#.", "E#."]), [[0, -1, -1], [0, -1, -1]])


def reference(plan):
    rows, cols = len(plan), len(plan[0]) if plan else 0
    out = [[-1] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if plan[r][c] == "#":
                continue
            best, queue, seen = -1, deque([(r, c, 0)]), {(r, c)}
            while queue:
                x, y, d = queue.popleft()
                if plan[x][y] == "E":
                    best = d
                    break
                for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= n[0] < rows and 0 <= n[1] < cols and plan[n[0]][n[1]] != "#" and n not in seen:
                        seen.add(n)
                        queue.append((n[0], n[1], d + 1))
            out[r][c] = best
    return out


def test_random_plans_against_a_search_from_every_tile():
    rng = random.Random(5)
    for _ in range(150):
        rows, cols = rng.randint(1, 6), rng.randint(1, 6)
        plan = ["".join(rng.choice("..#E") for _ in range(cols)) for _ in range(rows)]
        check(f"distance_to_exit({plan})", distance_to_exit(plan), reference(plan))


def test_a_large_plan_needs_one_search_not_many():
    plan = ["E" + "." * 149] + ["." * 150 for _ in range(149)]
    out = distance_to_exit(plan)
    check("distance to the far corner of a 150 x 150 plan", out[149][149], 298)
