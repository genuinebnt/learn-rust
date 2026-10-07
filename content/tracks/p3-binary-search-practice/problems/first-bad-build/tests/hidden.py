from anneal_prelude import check, ensure
from solution import first_bad_build

def counting(bad_from):
    """An is_bad function that remembers how often it was called."""
    calls = []

    def is_bad(build):
        calls.append(build)
        return build >= bad_from

    return is_bad, calls


def test_a_billion_builds_in_about_thirty_tests():
    is_bad, calls = counting(123_456_789)
    check("first_bad_build(10**9, ...)", first_bad_build(10**9, is_bad), 123_456_789)
    ensure(len(calls) <= 32, f"is_bad was called {len(calls)} times; binary search needs about 31")


def test_a_single_build_that_is_bad():
    check("first_bad_build(1, lambda b: True)", first_bad_build(1, lambda b: True), 1)


def test_a_single_build_that_is_good():
    check("first_bad_build(1, lambda b: False)", first_bad_build(1, lambda b: False), -1)


def test_the_flip_at_the_second_build():
    check("first_bad_build(2, lambda b: b >= 2)", first_bad_build(2, lambda b: b >= 2), 2)


def test_every_possible_flip_for_small_n():
    for n in range(1, 40):
        for flip in range(1, n + 2):
            want = flip if flip <= n else -1
            check(f"first_bad_build({n}, lambda b: b >= {flip})", first_bad_build(n, lambda b, f=flip: b >= f), want)


def test_the_call_count_stays_logarithmic_for_every_flip():
    for flip in (1, 2, 500, 999, 1000, 1001):
        is_bad, calls = counting(flip)
        first_bad_build(1000, is_bad)
        ensure(len(calls) <= 12, f"flip at {flip}: is_bad was called {len(calls)} times for 1000 builds")


def test_the_flip_at_the_very_last_of_many_builds():
    is_bad, calls = counting(10**6)
    check("first_bad_build(10**6, lambda b: b >= 10**6)", first_bad_build(10**6, is_bad), 10**6)
    ensure(len(calls) <= 23, f"is_bad was called {len(calls)} times for a million builds")


def test_is_not_called_with_builds_outside_the_range():
    seen = []
    first_bad_build(50, lambda b: seen.append(b) or b >= 20)
    ensure(all(1 <= b <= 50 for b in seen), "is_bad must only be called with builds 1 to n")
