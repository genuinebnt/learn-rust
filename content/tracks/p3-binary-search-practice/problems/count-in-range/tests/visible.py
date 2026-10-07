from anneal_prelude import check, ensure
from solution import count_in_range


def test_duplicates_at_the_edge():
    check('count_in_range([1, 2, 2, 2, 5, 9], 2, 5)', count_in_range([1, 2, 2, 2, 5, 9], 2, 5), 4)


def test_all_below():
    check('count_in_range([1, 2, 3], 10, 20)', count_in_range([1, 2, 3], 10, 20), 0)


def test_empty_range():
    check('count_in_range([1, 2, 3], 3, 1)', count_in_range([1, 2, 3], 3, 1), 0)


def test_empty_list():
    check('count_in_range([], 0, 10)', count_in_range([], 0, 10), 0)


def test_everything():
    check('count_in_range([4, 5, 6], 0, 100)', count_in_range([4, 5, 6], 0, 100), 3)


def test_single_value_range():
    check('count_in_range([1, 3, 3, 3, 7], 3, 3)', count_in_range([1, 3, 3, 3, 7], 3, 3), 3)
