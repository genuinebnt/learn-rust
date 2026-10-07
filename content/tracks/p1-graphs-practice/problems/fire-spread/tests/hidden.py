import random

from anneal_prelude import check, ensure
from solution import minutes_to_burn


def test_fire_in_the_middle():
    check('minutes_to_burn(["...", ".F.", "..."])', minutes_to_burn(["...", ".F.", "..."]), 2)


def test_already_all_fire():
    check('minutes_to_burn(["FF", "FF"])', minutes_to_burn(["FF", "FF"]), 0)


def test_two_fires_meet():
    check('minutes_to_burn(["F...F"])', minutes_to_burn(["F...F"]), 2)


def test_empty_plan():
    check('minutes_to_burn([])', minutes_to_burn([]), 0)


def test_snake():
    check('minutes_to_burn(["F.#", "#.#", "#.."])', minutes_to_burn(["F.#", "#.#", "#.."]), 4)


def test_fire_in_a_corner():
    check('minutes_to_burn(["F..", "...", "..."])', minutes_to_burn(["F..", "...", "..."]), 4)


def test_grass_between_two_fires():
    check('minutes_to_burn(["F.F"])', minutes_to_burn(["F.F"]), 1)


def reference(plan):
    rows, cols = len(plan), len(plan[0]) if plan else 0
    burning = {(r, c) for r in range(rows) for c in range(cols) if plan[r][c] == "F"}
    grass = {(r, c) for r in range(rows) for c in range(cols) if plan[r][c] == "."}
    minutes = 0
    while grass:
        spread = {n for (r, c) in burning for n in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)) if n in grass}
        if not spread:
            return -1
        grass -= spread
        burning |= spread
        minutes += 1
    return minutes


def test_random_forests_against_a_round_by_round_simulation():
    rng = random.Random(9)
    for _ in range(250):
        rows, cols = rng.randint(1, 6), rng.randint(1, 6)
        plan = ["".join(rng.choice("..#F") for _ in range(cols)) for _ in range(rows)]
        check(f"minutes_to_burn({plan})", minutes_to_burn(plan), reference(plan))
