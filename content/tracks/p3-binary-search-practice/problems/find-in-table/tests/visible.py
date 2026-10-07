from anneal_prelude import check, ensure
from solution import find_in_table


def test_found():
    check('find_in_table([[1, 3, 5], [7, 9, 11]], 9)', find_in_table([[1, 3, 5], [7, 9, 11]], 9), (1, 1))


def test_missing_between_values():
    check('find_in_table([[1, 3, 5], [7, 9, 11]], 4)', find_in_table([[1, 3, 5], [7, 9, 11]], 4), None)


def test_first_cell():
    check('find_in_table([[2, 4], [6, 8]], 2)', find_in_table([[2, 4], [6, 8]], 2), (0, 0))


def test_last_cell():
    check('find_in_table([[2, 4], [6, 8]], 8)', find_in_table([[2, 4], [6, 8]], 8), (1, 1))


def test_empty_table():
    check('find_in_table([], 1)', find_in_table([], 1), None)


def test_empty_rows():
    check('find_in_table([[]], 1)', find_in_table([[]], 1), None)
