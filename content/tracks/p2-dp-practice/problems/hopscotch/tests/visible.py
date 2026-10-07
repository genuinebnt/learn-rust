from anneal_prelude import check, ensure
from solution import hop_ways


def test_three_stones():
    check('hop_ways(3)', hop_ways(3), 4)


def test_four_stones():
    check('hop_ways(4)', hop_ways(4), 7)


def test_no_stones():
    check('hop_ways(0)', hop_ways(0), 1)


def test_one_stone():
    check('hop_ways(1)', hop_ways(1), 1)


def test_two_stones():
    check('hop_ways(2)', hop_ways(2), 2)


def test_five_stones():
    check('hop_ways(5)', hop_ways(5), 13)
