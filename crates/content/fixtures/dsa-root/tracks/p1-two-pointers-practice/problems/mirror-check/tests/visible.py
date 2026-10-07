from anneal_prelude import check
from solution import is_mirror


def test_yes():
    check("is_mirror([1, 2, 1])", is_mirror([1, 2, 1]), True)


def test_no():
    check("is_mirror([1, 2])", is_mirror([1, 2]), False)


def test_empty():
    check("is_mirror([])", is_mirror([]), True)


def test_one():
    check("is_mirror([7])", is_mirror([7]), True)


def test_even():
    check("is_mirror([1, 2, 2, 1])", is_mirror([1, 2, 2, 1]), True)
