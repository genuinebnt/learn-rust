import random

from anneal_prelude import check, ensure
from solution import best_picks


def test_greedy_fails():
    check('best_picks([2, 7, 9, 3, 1], 2)', best_picks([2, 7, 9, 3, 1], 2), 12)


def test_gap_three_picks_every_third():
    check('best_picks([5, 1, 1, 5, 1, 1, 5], 3)', best_picks([5, 1, 1, 5, 1, 1, 5], 3), 15)


def test_zeros():
    check('best_picks([0, 0, 0], 2)', best_picks([0, 0, 0], 2), 0)


def test_two_items_close():
    check('best_picks([6, 7], 2)', best_picks([6, 7], 2), 7)


def test_two_items_far_enough():
    check('best_picks([6, 7, 1], 2)', best_picks([6, 7, 1], 2), 7)


def test_equal_values():
    check('best_picks([4, 4, 4, 4, 4], 2)', best_picks([4, 4, 4, 4, 4], 2), 12)


def test_gap_two_alternate_big():
    check('best_picks([1, 100, 1, 100, 1], 2)', best_picks([1, 100, 1, 100, 1], 2), 200)


def reference(values, gap):
    n = len(values)
    best = 0
    for mask in range(1 << n):
        picked = [i for i in range(n) if mask >> i & 1]
        if all(b - a >= gap for a, b in zip(picked, picked[1:])):
            best = max(best, sum(values[i] for i in picked))
    return best


def test_random_prizes_against_trying_every_subset():
    rng = random.Random(6)
    for _ in range(400):
        values = [rng.randint(0, 9) for _ in range(rng.randint(0, 9))]
        gap = rng.randint(1, 5)
        check(f"best_picks({values}, {gap})", best_picks(values, gap), reference(values, gap))
