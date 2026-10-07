from anneal_prelude import check
from solution import pair_sum


def test_negative():
    check("pair_sum([-3, -1, 2], -4)", pair_sum([-3, -1, 2], -4), (0, 1))


def test_ends():
    check("pair_sum([1, 5, 9], 10)", pair_sum([1, 5, 9], 10), (0, 2))


def test_none_in_the_middle():
    check("pair_sum([1, 3, 5, 7], 6)", pair_sum([1, 3, 5, 7], 6), (0, 2))


def test_single():
    check("pair_sum([5], 5)", pair_sum([5], 5), None)


def test_large():
    n = list(range(100000))
    check("pair_sum(range(100000), 199997)", pair_sum(n, 199997), (99998, 99999))


def test_zero_target():
    check("pair_sum([-2, 0, 2], 0)", pair_sum([-2, 0, 2], 0), (0, 2))


def test_adjacent():
    check("pair_sum([1, 2, 3], 5)", pair_sum([1, 2, 3], 5), (1, 2))


def test_first_pair():
    check("pair_sum([1, 1, 1, 1], 2)", pair_sum([1, 1, 1, 1], 2), (0, 3))
