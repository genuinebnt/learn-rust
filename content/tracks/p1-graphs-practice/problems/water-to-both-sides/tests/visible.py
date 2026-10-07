from anneal_prelude import check, ensure
from solution import drains_to_both


def test_small_map():
    check('drains_to_both([[1, 2, 1], [3, 1, 3]])', drains_to_both([[1, 2, 1], [3, 1, 3]]), [(0, 1)])


def test_one_cell():
    check('drains_to_both([[5]])', drains_to_both([[5]]), [(0, 0)])


def test_one_column():
    check('drains_to_both([[1], [2], [3]])', drains_to_both([[1], [2], [3]]), [(0, 0), (1, 0), (2, 0)])


def test_a_slope_down_to_the_west():
    check('drains_to_both([[1, 2, 3]])', drains_to_both([[1, 2, 3]]), [(0, 2)])


def test_flat_map():
    check('drains_to_both([[2, 2], [2, 2]])', drains_to_both([[2, 2], [2, 2]]), [(0, 0), (0, 1), (1, 0), (1, 1)])
