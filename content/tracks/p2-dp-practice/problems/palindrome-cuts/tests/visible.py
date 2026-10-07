from anneal_prelude import check, ensure
from solution import fewest_cuts


def test_one_cut():
    check('fewest_cuts("aab")', fewest_cuts("aab"), 1)


def test_already_a_palindrome():
    check('fewest_cuts("racecar")', fewest_cuts("racecar"), 0)


def test_all_different():
    check('fewest_cuts("abc")', fewest_cuts("abc"), 2)


def test_empty():
    check('fewest_cuts("")', fewest_cuts(""), 0)


def test_single_letter():
    check('fewest_cuts("x")', fewest_cuts("x"), 0)


def test_two_letters():
    check('fewest_cuts("ab")', fewest_cuts("ab"), 1)
