from anneal_prelude import check, ensure
from solution import integer_sqrt


def test_perfect_square():
    check('integer_sqrt(16)', integer_sqrt(16), 4)


def test_not_a_perfect_square():
    check('integer_sqrt(24)', integer_sqrt(24), 4)


def test_zero():
    check('integer_sqrt(0)', integer_sqrt(0), 0)


def test_one():
    check('integer_sqrt(1)', integer_sqrt(1), 1)


def test_two():
    check('integer_sqrt(2)', integer_sqrt(2), 1)


def test_a_larger_one():
    check('integer_sqrt(10**12)', integer_sqrt(10**12), 10**6)
