from anneal_prelude import check
from solution import is_mirror


def test_a():
    check("x", is_mirror([1, 2, 3]), False)


def test_b():
    check("x", is_mirror([3, 2, 3]), True)


def test_c():
    check("x", is_mirror([1, 1]), True)


def test_d():
    check("x", is_mirror([1, 2, 3, 2, 1]), True)


def test_e():
    check("x", is_mirror([1, 2, 3, 3, 1]), False)


def test_f():
    check("x", is_mirror([0, 0, 0]), True)


def test_g():
    check("x", is_mirror([5, 4]), False)


def test_h():
    check("x", is_mirror(list(range(10)) + list(range(9, -1, -1))), True)
