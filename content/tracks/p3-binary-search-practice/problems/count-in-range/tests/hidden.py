import random

from anneal_prelude import check, ensure
from solution import count_in_range


def test_all_above():
    check('count_in_range([5, 6], 1, 4)', count_in_range([5, 6], 1, 4), 0)


def test_range_between_values():
    check('count_in_range([1, 10], 2, 9)', count_in_range([1, 10], 2, 9), 0)


def test_negative_numbers():
    check('count_in_range([-9, -5, -5, 0, 4], -6, 0)', count_in_range([-9, -5, -5, 0, 4], -6, 0), 3)


def test_one_element_inside():
    check('count_in_range([7], 7, 7)', count_in_range([7], 7, 7), 1)


def test_one_element_outside():
    check('count_in_range([7], 8, 9)', count_in_range([7], 8, 9), 0)


def test_low_equals_the_smallest():
    check('count_in_range([2, 3, 4], 2, 3)', count_in_range([2, 3, 4], 2, 3), 2)


def test_random_lists_against_a_linear_count():
    rng = random.Random(41)
    for _ in range(300):
        values = sorted(rng.randint(-10, 10) for _ in range(rng.randint(0, 15)))
        low, high = rng.randint(-12, 12), rng.randint(-12, 12)
        want = sum(1 for v in values if low <= v <= high)
        check(f"count_in_range({values}, {low}, {high})", count_in_range(values, low, high), want)


def test_a_range_of_a_billion_numbers():
    values = range(0, 10**9)  # supports len() and indexing, but looking at every item would take far too long
    check("count_in_range(range(10**9), 100, 199)", count_in_range(values, 100, 199), 100)
    check("count_in_range(range(10**9), -5, 4)", count_in_range(values, -5, 4), 5)


def test_a_huge_list_with_repeats():
    values = [v // 3 for v in range(0, 3_000_000)]  # every number appears three times
    check("count_in_range(three of each number, 10, 11)", count_in_range(values, 10, 11), 6)
