from anneal_prelude import check, ensure
from solution import smallest_difference


def test_mixed():
    check('smallest_difference([3, 1, 4, 2, 2, 1])', smallest_difference([3, 1, 4, 2, 2, 1]), 1)


def test_greedy_fails():
    check('smallest_difference([3, 3, 2, 2, 2])', smallest_difference([3, 3, 2, 2, 2]), 0)


def test_empty():
    check('smallest_difference([])', smallest_difference([]), 0)


def test_one_item():
    check('smallest_difference([9])', smallest_difference([9]), 9)


def test_two_equal():
    check('smallest_difference([5, 5])', smallest_difference([5, 5]), 0)


def test_odd_total():
    check('smallest_difference([1, 2, 4])', smallest_difference([1, 2, 4]), 1)
