from anneal_prelude import check
from solution import pair_sum


def test_found():
    check("pair_sum([1, 2, 4, 7], 9)", pair_sum([1, 2, 4, 7], 9), (1, 3))


def test_missing():
    check("pair_sum([1, 2], 10)", pair_sum([1, 2], 10), None)


def test_two_items():
    check("pair_sum([3, 4], 7)", pair_sum([3, 4], 7), (0, 1))


def test_empty():
    check("pair_sum([], 1)", pair_sum([], 1), None)


def test_repeats():
    check("pair_sum([2, 2, 2], 4)", pair_sum([2, 2, 2], 4), (0, 2))
