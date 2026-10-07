from anneal_prelude import check, ensure
from solution import first_bad_build

def counting(bad_from):
    """An is_bad function that remembers how often it was called."""
    calls = []

    def is_bad(build):
        calls.append(build)
        return build >= bad_from

    return is_bad, calls


def test_a_flip_in_the_middle():
    check("first_bad_build(10, lambda b: b >= 7)", first_bad_build(10, lambda b: b >= 7), 7)


def test_no_bad_build():
    check("first_bad_build(5, lambda b: False)", first_bad_build(5, lambda b: False), -1)


def test_every_build_is_bad():
    check("first_bad_build(6, lambda b: True)", first_bad_build(6, lambda b: True), 1)


def test_the_last_build_is_the_first_bad_one():
    check("first_bad_build(9, lambda b: b >= 9)", first_bad_build(9, lambda b: b >= 9), 9)


def test_no_builds():
    check("first_bad_build(0, lambda b: True)", first_bad_build(0, lambda b: True), -1)
