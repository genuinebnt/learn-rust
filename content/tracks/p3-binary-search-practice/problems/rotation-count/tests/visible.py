from anneal_prelude import check, ensure
from solution import rotation_count


def test_rotated_three():
    check('rotation_count([4, 5, 6, 1, 2, 3])', rotation_count([4, 5, 6, 1, 2, 3]), 3)


def test_not_rotated():
    check('rotation_count([1, 2, 3])', rotation_count([1, 2, 3]), 0)


def test_rotated_two():
    check('rotation_count([2, 3, 1])', rotation_count([2, 3, 1]), 2)


def test_single():
    check('rotation_count([7])', rotation_count([7]), 0)


def test_two_values_rotated():
    check('rotation_count([9, 4])', rotation_count([9, 4]), 1)


def test_empty():
    check('rotation_count([])', rotation_count([]), 0)
