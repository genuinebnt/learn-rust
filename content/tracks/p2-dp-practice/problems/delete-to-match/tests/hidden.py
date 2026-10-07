import random

from anneal_prelude import check, ensure
from solution import deletions_to_match


def test_subsequence_of_the_other():
    check('deletions_to_match("ace", "abcde")', deletions_to_match("ace", "abcde"), 2)


def test_repeated_letters():
    check('deletions_to_match("aab", "aba")', deletions_to_match("aab", "aba"), 2)


def test_same_letters_different_order():
    check('deletions_to_match("abcd", "dcba")', deletions_to_match("abcd", "dcba"), 6)


def test_long_common_part():
    check('deletions_to_match("algorithm", "altruistic")', deletions_to_match("algorithm", "altruistic"), 9)


def test_single_letters_equal():
    check('deletions_to_match("a", "a")', deletions_to_match("a", "a"), 0)


def test_single_letters_different():
    check('deletions_to_match("a", "b")', deletions_to_match("a", "b"), 2)


def reference(a, b):
    def common(x, y):
        if not x or not y:
            return 0
        if x[0] == y[0]:
            return 1 + common(x[1:], y[1:])
        return max(common(x[1:], y), common(x, y[1:]))

    return len(a) + len(b) - 2 * common(a, b)


def test_random_strings_against_a_recursive_reference():
    rng = random.Random(19)
    for _ in range(300):
        a = "".join(rng.choice("abc") for _ in range(rng.randint(0, 7)))
        b = "".join(rng.choice("abc") for _ in range(rng.randint(0, 7)))
        check(f"deletions_to_match({a!r}, {b!r})", deletions_to_match(a, b), reference(a, b))


def test_long_strings_are_fast():
    a = "ab" * 500
    b = "ba" * 500
    check("deletions_to_match of two 1000-character strings", deletions_to_match(a, b), 2)
