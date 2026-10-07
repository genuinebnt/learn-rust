from anneal_prelude import check, ensure
from solution import min_capacity


def test_ten_packages():
    check('min_capacity([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5)', min_capacity([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5), 15)


def test_six_packages():
    check('min_capacity([3, 2, 2, 4, 1, 4], 3)', min_capacity([3, 2, 2, 4, 1, 4], 3), 6)


def test_one_day():
    check('min_capacity([1, 2, 3], 1)', min_capacity([1, 2, 3], 1), 6)


def test_one_package():
    check('min_capacity([9], 4)', min_capacity([9], 4), 9)


def test_more_days_than_packages():
    check('min_capacity([5, 1, 7], 10)', min_capacity([5, 1, 7], 10), 7)


def test_every_package_alone():
    check('min_capacity([4, 4, 4], 3)', min_capacity([4, 4, 4], 3), 4)
