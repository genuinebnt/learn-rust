from anneal_prelude import check, ensure
from solution import fair_split


def test_two_parts():
    check('fair_split([7, 2, 5, 10, 8], 2)', fair_split([7, 2, 5, 10, 8], 2), 18)


def test_three_parts():
    check('fair_split([1, 2, 3, 4, 5], 3)', fair_split([1, 2, 3, 4, 5], 3), 6)


def test_every_value_alone():
    check('fair_split([4, 4, 4], 3)', fair_split([4, 4, 4], 3), 4)


def test_one_part():
    check('fair_split([3, 1, 4, 1, 5], 1)', fair_split([3, 1, 4, 1, 5], 1), 14)


def test_single_value():
    check('fair_split([9], 1)', fair_split([9], 1), 9)


def test_two_values_two_parts():
    check('fair_split([6, 2], 2)', fair_split([6, 2], 2), 6)
