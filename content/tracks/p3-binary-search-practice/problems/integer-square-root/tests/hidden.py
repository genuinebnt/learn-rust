import random

from anneal_prelude import check, ensure
from solution import integer_sqrt


def test_just_below_a_square():
    check('integer_sqrt(99)', integer_sqrt(99), 9)


def test_just_above_a_square():
    check('integer_sqrt(101)', integer_sqrt(101), 10)


def test_huge_perfect_square():
    check('integer_sqrt((10**18 + 7) ** 2)', integer_sqrt((10**18 + 7) ** 2), 10**18 + 7)


def test_huge_one_below_a_square():
    check('integer_sqrt((10**18 + 7) ** 2 - 1)', integer_sqrt((10**18 + 7) ** 2 - 1), 10**18 + 6)


def test_three():
    check('integer_sqrt(3)', integer_sqrt(3), 1)


def test_four():
    check('integer_sqrt(4)', integer_sqrt(4), 2)


def test_every_value_up_to_a_thousand():
    for n in range(0, 1001):
        r = integer_sqrt(n)
        ensure(r * r <= n < (r + 1) * (r + 1), f"integer_sqrt({n}) returned {r}")


def test_random_huge_values():
    rng = random.Random(40)
    for _ in range(100):
        n = rng.randint(0, 10**36)
        r = integer_sqrt(n)
        ensure(r * r <= n < (r + 1) * (r + 1), f"integer_sqrt({n}) returned {r}")
