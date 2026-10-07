from anneal_prelude import check, ensure
from solution import fewest_bills


def test_mixed_bills():
    check('fewest_bills([(1, 5), (5, 2), (10, 1)], 18)', fewest_bills([(1, 5), (5, 2), (10, 1)], 18), 5)


def test_not_enough_of_a_kind():
    check('fewest_bills([(5, 1)], 10)', fewest_bills([(5, 1)], 10), -1)


def test_greedy_would_fail():
    check('fewest_bills([(4, 3), (3, 3)], 6)', fewest_bills([(4, 3), (3, 3)], 6), 2)


def test_zero_amount():
    check('fewest_bills([(1, 1)], 0)', fewest_bills([(1, 1)], 0), 0)


def test_no_bills():
    check('fewest_bills([], 5)', fewest_bills([], 5), -1)


def test_only_ones():
    check('fewest_bills([(1, 10)], 7)', fewest_bills([(1, 10)], 7), 7)
