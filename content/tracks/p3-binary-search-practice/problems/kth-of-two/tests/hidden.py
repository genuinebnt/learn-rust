import random

from anneal_prelude import check, ensure
from solution import kth_of_two


def test_different_lengths():
    check('kth_of_two([1], [2, 3, 4, 5, 6, 7], 5)', kth_of_two([1], [2, 3, 4, 5, 6, 7], 5), 5)


def test_all_of_a_before_b():
    check('kth_of_two([1, 2], [3, 4], 3)', kth_of_two([1, 2], [3, 4], 3), 3)


def test_all_of_b_before_a():
    check('kth_of_two([3, 4], [1, 2], 3)', kth_of_two([3, 4], [1, 2], 3), 3)


def test_negatives():
    check('kth_of_two([-5, -1], [-3, 0], 2)', kth_of_two([-5, -1], [-3, 0], 2), -3)


def test_duplicates_across():
    check('kth_of_two([2, 2, 4], [2, 3], 3)', kth_of_two([2, 2, 4], [2, 3], 3), 2)


def test_single_items():
    check('kth_of_two([8], [4], 2)', kth_of_two([8], [4], 2), 8)


def test_random_lists_against_sorting_everything():
    rng = random.Random(48)
    for _ in range(500):
        a = sorted(rng.randint(-15, 15) for _ in range(rng.randint(0, 9)))
        b = sorted(rng.randint(-15, 15) for _ in range(rng.randint(0, 9)))
        if not a and not b:
            continue
        for k in range(1, len(a) + len(b) + 1):
            check(f"kth_of_two({a}, {b}, {k})", kth_of_two(a, b, k), sorted(a + b)[k - 1])


def test_tens_of_millions_of_items_are_not_walked():
    a = range(0, 800_000_000, 2)   # the 400 million even numbers
    b = range(1, 800_000_001, 2)   # the 400 million odd numbers
    check("kth_of_two(evens, odds, 300_000_000)", kth_of_two(a, b, 300_000_000), 299_999_999)
    check("kth_of_two(evens, odds, 800_000_000)", kth_of_two(a, b, 800_000_000), 799_999_999)


def test_one_list_far_longer_than_the_other():
    a = [10, 20, 30]
    b = range(0, 50_000_000)
    check("kth_of_two([10, 20, 30], range(50_000_000), 7)", kth_of_two(a, b, 7), 6)
