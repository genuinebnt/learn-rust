import random

from anneal_prelude import check, ensure
from solution import cheapest_multiplication


def test_a_good_bracketing_matters():
    check('cheapest_multiplication([30, 35, 15, 5, 10, 20, 25])', cheapest_multiplication([30, 35, 15, 5, 10, 20, 25]), 15125)


def test_left_to_right_is_worse():
    check('cheapest_multiplication([10, 100, 5, 50])', cheapest_multiplication([10, 100, 5, 50]), 7500)


def test_same_sizes():
    check('cheapest_multiplication([4, 4, 4, 4, 4])', cheapest_multiplication([4, 4, 4, 4, 4]), 192)


def test_tall_and_thin():
    check('cheapest_multiplication([100, 1, 100, 1])', cheapest_multiplication([100, 1, 100, 1]), 200)


def test_single_dimension():
    check('cheapest_multiplication([8])', cheapest_multiplication([8]), 0)


def test_five_small():
    check('cheapest_multiplication([1, 2, 3, 4, 5, 6])', cheapest_multiplication([1, 2, 3, 4, 5, 6]), 68)


def reference(dims, i=None, j=None):
    if i is None:
        n = len(dims) - 1
        return 0 if n < 2 else reference(dims, 0, n - 1)
    if i == j:
        return 0
    return min(reference(dims, i, k) + reference(dims, k + 1, j) + dims[i] * dims[k + 1] * dims[j + 1] for k in range(i, j))


def test_random_chains_against_trying_every_bracketing():
    rng = random.Random(24)
    for _ in range(300):
        dims = [rng.randint(1, 9) for _ in range(rng.randint(0, 8))]
        check(f"cheapest_multiplication({dims})", cheapest_multiplication(list(dims)), reference(dims))


def test_a_long_chain_is_fast():
    ensure(cheapest_multiplication([(i * 7) % 13 + 1 for i in range(120)]) > 0, "a chain of 119 matrices has a positive cost")
