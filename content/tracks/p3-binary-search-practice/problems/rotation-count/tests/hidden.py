import random

from anneal_prelude import check, ensure
from solution import rotation_count


def test_rotated_by_one():
    check('rotation_count([5, 1, 2, 3, 4])', rotation_count([5, 1, 2, 3, 4]), 1)


def test_rotated_by_n_minus_one():
    check('rotation_count([2, 3, 4, 5, 1])', rotation_count([2, 3, 4, 5, 1]), 4)


def test_negative_numbers():
    check('rotation_count([0, 3, -9, -4])', rotation_count([0, 3, -9, -4]), 2)


def test_two_values_sorted():
    check('rotation_count([1, 9])', rotation_count([1, 9]), 0)


def test_long_rotation():
    check('rotation_count([6, 7, 8, 9, 10, 1, 2, 3, 4, 5])', rotation_count([6, 7, 8, 9, 10, 1, 2, 3, 4, 5]), 5)


def test_every_rotation_of_random_lists():
    rng = random.Random(44)
    for _ in range(100):
        base = sorted(rng.sample(range(-50, 50), rng.randint(1, 12)))
        n = len(base)
        for k in range(n):
            rotated = base[n - k:] + base[:n - k]
            check(f"rotation_count({rotated})", rotation_count(list(rotated)), k)


def test_a_million_items():
    n = 1_000_000
    base = list(range(n))
    for k in (0, 1, 500_000, 999_999):
        rotated = base[n - k:] + base[:n - k]
        check(f"rotation_count(rotated by {k})", rotation_count(rotated), k)


def test_a_huge_range_that_cannot_be_walked():
    class Rotated:
        """Behaves like a sorted list of 10**12 numbers whose last item was moved to the front 123456789012 times."""

        def __init__(self, n, k):
            self.n, self.k = n, k

        def __len__(self):
            return self.n

        def __getitem__(self, i):
            return (i - self.k) % self.n

    check("rotation_count of a 10**12 list", rotation_count(Rotated(10**12, 123456789012)), 123456789012)
