import random

from anneal_prelude import check, ensure
from solution import smallest_difference


def test_one_heavy_item():
    check('smallest_difference([100, 1, 1, 1])', smallest_difference([100, 1, 1, 1]), 97)


def test_many_ones():
    check('smallest_difference([1] * 7)', smallest_difference([1] * 7), 1)


def test_three_items():
    check('smallest_difference([8, 6, 5])', smallest_difference([8, 6, 5]), 3)


def test_zeros():
    check('smallest_difference([0, 0, 4])', smallest_difference([0, 0, 4]), 4)


def test_powers_of_two():
    check('smallest_difference([1, 2, 4, 8, 16])', smallest_difference([1, 2, 4, 8, 16]), 1)


def test_two_big_and_small():
    check('smallest_difference([10, 10, 3])', smallest_difference([10, 10, 3]), 3)


def reference(items):
    total = sum(items)
    return min(abs(total - 2 * sum(items[i] for i in range(len(items)) if m >> i & 1)) for m in range(1 << len(items)))


def test_random_items_against_trying_every_split():
    rng = random.Random(18)
    for _ in range(400):
        items = [rng.randint(0, 12) for _ in range(rng.randint(0, 10))]
        check(f"smallest_difference({items})", smallest_difference(list(items)), reference(items))


def test_many_items_is_fast():
    items = [(i * 37) % 91 + 1 for i in range(100)]
    ensure(0 <= smallest_difference(items) <= 91, "a hundred small items can nearly always be split evenly")
