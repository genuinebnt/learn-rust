from anneal_prelude import check, ensure
from solution import kth_of_two


def test_interleaved():
    check('kth_of_two([1, 3, 5], [2, 4, 6], 4)', kth_of_two([1, 3, 5], [2, 4, 6], 4), 4)


def test_one_list_empty():
    check('kth_of_two([], [7, 8], 2)', kth_of_two([], [7, 8], 2), 8)


def test_all_equal():
    check('kth_of_two([1, 1, 1], [1, 1], 5)', kth_of_two([1, 1, 1], [1, 1], 5), 1)


def test_smallest():
    check('kth_of_two([5, 6], [1, 2], 1)', kth_of_two([5, 6], [1, 2], 1), 1)


def test_largest():
    check('kth_of_two([5, 6], [1, 2], 4)', kth_of_two([5, 6], [1, 2], 4), 6)


def test_the_other_list_empty():
    check('kth_of_two([3, 9], [], 1)', kth_of_two([3, 9], [], 1), 3)
