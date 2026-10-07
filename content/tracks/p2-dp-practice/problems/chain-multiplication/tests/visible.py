from anneal_prelude import check, ensure
from solution import cheapest_multiplication


def test_three_matrices():
    check('cheapest_multiplication([10, 30, 5, 60])', cheapest_multiplication([10, 30, 5, 60]), 4500)


def test_four_matrices():
    check('cheapest_multiplication([40, 20, 30, 10, 30])', cheapest_multiplication([40, 20, 30, 10, 30]), 26000)


def test_one_matrix():
    check('cheapest_multiplication([5, 7])', cheapest_multiplication([5, 7]), 0)


def test_no_matrices():
    check('cheapest_multiplication([])', cheapest_multiplication([]), 0)


def test_two_matrices():
    check('cheapest_multiplication([2, 3, 4])', cheapest_multiplication([2, 3, 4]), 24)


def test_all_ones():
    check('cheapest_multiplication([1, 1, 1, 1])', cheapest_multiplication([1, 1, 1, 1]), 2)
