import random

from anneal_prelude import check, ensure
from solution import fair_split


def test_heavy_value_decides():
    check('fair_split([1, 1, 100, 1, 1], 3)', fair_split([1, 1, 100, 1, 1], 3), 100)


def test_zeros():
    check('fair_split([0, 0, 0, 5], 2)', fair_split([0, 0, 0, 5], 2), 5)


def test_equal_values():
    check('fair_split([5, 5, 5, 5], 2)', fair_split([5, 5, 5, 5], 2), 10)


def test_uneven():
    check('fair_split([1, 4, 4], 3)', fair_split([1, 4, 4], 3), 4)


def test_four_parts():
    check('fair_split([10, 5, 13, 4, 8, 4, 5, 11, 14, 9, 16, 10, 20, 8], 8)', fair_split([10, 5, 13, 4, 8, 4, 5, 11, 14, 9, 16, 10, 20, 8], 8), 25)


def test_last_part_big():
    check('fair_split([1, 2, 3, 100], 2)', fair_split([1, 2, 3, 100], 2), 100)


def reference(values, parts):
    n = len(values)
    best = float("inf")
    from itertools import combinations

    for cuts in combinations(range(1, n), parts - 1):
        bounds = (0, *cuts, n)
        best = min(best, max(sum(values[a:b]) for a, b in zip(bounds, bounds[1:])))
    return best


def test_random_lists_against_trying_every_cutting():
    rng = random.Random(47)
    for _ in range(300):
        values = [rng.randint(0, 15) for _ in range(rng.randint(1, 8))]
        parts = rng.randint(1, len(values))
        check(f"fair_split({values}, {parts})", fair_split(list(values), parts), reference(values, parts))


def test_a_long_list_is_fast():
    values = [(i * 7919) % 1000 for i in range(50_000)]
    ensure(fair_split(values, 100) >= sum(values) // 100, "the largest piece is at least the average piece")
