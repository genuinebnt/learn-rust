from anneal_prelude import check, ensure
from solution import deletions_to_match


def test_sea_and_eat():
    check('deletions_to_match("sea", "eat")', deletions_to_match("sea", "eat"), 2)


def test_equal():
    check('deletions_to_match("abc", "abc")', deletions_to_match("abc", "abc"), 0)


def test_nothing_in_common():
    check('deletions_to_match("abc", "xyz")', deletions_to_match("abc", "xyz"), 6)


def test_one_empty():
    check('deletions_to_match("", "abc")', deletions_to_match("", "abc"), 3)


def test_both_empty():
    check('deletions_to_match("", "")', deletions_to_match("", ""), 0)


def test_order_matters():
    check('deletions_to_match("ab", "ba")', deletions_to_match("ab", "ba"), 2)
