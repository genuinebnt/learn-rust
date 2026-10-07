import random

from anneal_prelude import check, ensure
from solution import min_capacity


def test_heavy_package_decides():
    check('min_capacity([1, 1, 50, 1, 1], 3)', min_capacity([1, 1, 50, 1, 1], 3), 50)


def test_two_days():
    check('min_capacity([7, 2, 5, 10, 8], 2)', min_capacity([7, 2, 5, 10, 8], 2), 18)


def test_even_split():
    check('min_capacity([5, 5, 5, 5], 2)', min_capacity([5, 5, 5, 5], 2), 10)


def test_uneven():
    check('min_capacity([1, 2, 3, 1, 1], 4)', min_capacity([1, 2, 3, 1, 1], 4), 3)


def test_days_equal_packages_minus_one():
    check('min_capacity([2, 3, 4], 2)', min_capacity([2, 3, 4], 2), 5)


def test_two_equal_packages_two_days():
    check('min_capacity([6, 6], 2)', min_capacity([6, 6], 2), 6)


def reference(weights, days):
    for capacity in range(max(weights), sum(weights) + 1):
        used, load = 1, 0
        for w in weights:
            if load + w > capacity:
                used += 1
                load = 0
            load += w
        if used <= days:
            return capacity


def test_random_shipments_against_trying_every_capacity():
    rng = random.Random(42)
    for _ in range(300):
        weights = [rng.randint(1, 12) for _ in range(rng.randint(1, 9))]
        days = rng.randint(1, len(weights) + 1)
        check(f"min_capacity({weights}, {days})", min_capacity(list(weights), days), reference(weights, days))


def test_big_numbers_are_fast():
    weights = [10**6 + i for i in range(5000)]
    ensure(min_capacity(weights, 7) >= max(weights), "the capacity is at least the heaviest package")
