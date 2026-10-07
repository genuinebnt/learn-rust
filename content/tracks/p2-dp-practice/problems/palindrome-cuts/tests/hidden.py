import random

from anneal_prelude import check, ensure
from solution import fewest_cuts


def test_greedy_longest_prefix_fails():
    check('fewest_cuts("abbab")', fewest_cuts("abbab"), 1)


def test_all_the_same():
    check('fewest_cuts("aaaaaa")', fewest_cuts("aaaaaa"), 0)


def test_two_palindromes():
    check('fewest_cuts("abbaxyx")', fewest_cuts("abbaxyx"), 1)


def test_alternating():
    check('fewest_cuts("ababab")', fewest_cuts("ababab"), 1)


def test_needs_three_pieces():
    check('fewest_cuts("aabcb")', fewest_cuts("aabcb"), 1)


def test_long_without_repeats():
    check('fewest_cuts("abcdefgh")', fewest_cuts("abcdefgh"), 7)


def reference(s):
    if s == s[::-1]:
        return 0
    return min(1 + reference(s[i:]) for i in range(1, len(s)) if s[:i] == s[:i][::-1])


def test_random_strings_against_trying_every_cut():
    rng = random.Random(20)
    for _ in range(300):
        s = "".join(rng.choice("abc") for _ in range(rng.randint(0, 9)))
        check(f"fewest_cuts({s!r})", fewest_cuts(s), reference(s) if s else 0)


def test_a_long_string_is_fast_enough():
    check("fewest_cuts('ab' * 400)", fewest_cuts("ab" * 400), 1)
