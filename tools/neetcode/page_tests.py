"""Behavioural checks for the solutions in content/dsa/pages. run(slug, namespace) raises on a wrong answer.

Each check compares against a brute-force reference on the problem's examples and on random inputs, so a page can't
ship a solution that only passes the sample.
"""
import random
from collections import Counter, defaultdict


def rng(seed=1):
    return random.Random(seed)


def contains_duplicate(ns):
    f = ns["Solution"]().containsDuplicate
    assert f([1, 2, 3, 1]) is True and f([1, 2, 3, 4]) is False and f([]) is False and f([5]) is False
    r = rng()
    for _ in range(300):
        a = [r.randint(0, 12) for _ in range(r.randint(0, 10))]
        assert f(list(a)) == (len(set(a)) != len(a)), a


def valid_anagram(ns):
    f = ns["Solution"]().isAnagram
    assert f("anagram", "nagaram") and not f("rat", "car") and not f("a", "ab") and f("", "")
    r = rng()
    for _ in range(300):
        s = "".join(r.choice("abc") for _ in range(r.randint(0, 6)))
        t = "".join(r.choice("abc") for _ in range(r.randint(0, 6)))
        assert f(s, t) == (sorted(s) == sorted(t)), (s, t)


def two_sum(ns):
    f = ns["Solution"]().twoSum
    assert sorted(f([2, 7, 11, 15], 9)) == [0, 1] and sorted(f([3, 2, 4], 6)) == [1, 2] and sorted(f([3, 3], 6)) == [0, 1]
    r = rng()
    for _ in range(300):
        a = [r.randint(-10, 10) for _ in range(r.randint(2, 8))]
        i, j = r.sample(range(len(a)), 2)
        target = a[i] + a[j]
        got = f(list(a), target)
        assert len(got) == 2 and got[0] != got[1] and a[got[0]] + a[got[1]] == target, (a, target, got)


def group_anagrams(ns):
    f = ns["Solution"]().groupAnagrams
    norm = lambda g: sorted(sorted(x) for x in g)
    assert norm(f(["eat", "tea", "tan", "ate", "nat", "bat"])) == norm([["bat"], ["nat", "tan"], ["ate", "eat", "tea"]])
    assert norm(f([""])) == [[""]] and norm(f(["a"])) == [["a"]]
    r = rng()
    for _ in range(200):
        words = ["".join(r.choice("abc") for _ in range(r.randint(0, 4))) for _ in range(r.randint(0, 8))]
        want = defaultdict(list)
        for w in words:
            want["".join(sorted(w))].append(w)
        assert norm(f(list(words))) == norm(want.values()), words


def top_k(ns):
    f = ns["Solution"]().topKFrequent
    assert sorted(f([1, 1, 1, 2, 2, 3], 2)) == [1, 2] and f([1], 1) == [1]
    r = rng()
    for _ in range(300):
        a = [r.randint(0, 6) for _ in range(r.randint(1, 20))]
        c = Counter(a)
        k = r.randint(1, len(c))
        freqs = sorted(c.values(), reverse=True)
        if k < len(freqs) and freqs[k - 1] == freqs[k]:
            continue  # ties at the boundary: the answer isn't unique (the problem guarantees it is)
        assert sorted(f(list(a), k)) == sorted(v for v, _ in c.most_common(k)), (a, k)


def codec(ns):
    c = ns["Codec"]()
    cases = [[], [""], ["", ""], ["a"], ["Hello", "World"], ["4#abcd", "#", "12#", "0#"], ["x" * 30, "1", "#9#"], ["é", "日本語"]]
    for strs in cases:
        assert c.decode(c.encode(list(strs))) == strs, strs
    r = rng()
    for _ in range(300):
        strs = ["".join(r.choice("#0123456789ab ") for _ in range(r.randint(0, 6))) for _ in range(r.randint(0, 5))]
        assert c.decode(c.encode(list(strs))) == strs, strs


def product_except_self(ns):
    f = ns["Solution"]().productExceptSelf
    assert f([1, 2, 3, 4]) == [24, 12, 8, 6] and f([-1, 1, 0, -3, 3]) == [0, 0, 9, 0, 0]
    r = rng()
    for _ in range(300):
        a = [r.randint(-3, 3) for _ in range(r.randint(2, 7))]
        want = []
        for i in range(len(a)):
            p = 1
            for j, x in enumerate(a):
                if j != i:
                    p *= x
            want.append(p)
        assert f(list(a)) == want, a


def valid_sudoku(ns):
    f = ns["Solution"]().isValidSudoku
    rows = ["53..7....", "6..195...", ".98....6.", "8...6...3", "4..8.3..1", "7...2...6", ".6....28.", "...419..5", "....8..79"]
    good = [list(r) for r in rows]
    assert f([list(r) for r in good]) is True
    bad = [list(r) for r in good]
    bad[0][0] = "8"  # 8 again in the first column and box
    assert f(bad) is False
    row_dup = [["."] * 9 for _ in range(9)]
    row_dup[4][0] = row_dup[4][8] = "7"
    assert f(row_dup) is False
    col_dup = [["."] * 9 for _ in range(9)]
    col_dup[0][3] = col_dup[8][3] = "2"
    assert f(col_dup) is False
    box_dup = [["."] * 9 for _ in range(9)]
    box_dup[3][3] = box_dup[5][5] = "9"
    assert f(box_dup) is False
    assert f([["."] * 9 for _ in range(9)]) is True


def longest_consecutive(ns):
    f = ns["Solution"]().longestConsecutive
    assert f([100, 4, 200, 1, 3, 2]) == 4 and f([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]) == 9 and f([]) == 0 and f([1, 0, 1, 2]) == 3
    r = rng()
    for _ in range(300):
        a = [r.randint(-8, 8) for _ in range(r.randint(0, 12))]
        s = set(a)
        want = 0
        for x in s:
            n = 0
            while x + n in s:
                n += 1
            want = max(want, n)
        assert f(list(a)) == want, a


CHECKS = {
    "contains-duplicate": contains_duplicate,
    "valid-anagram": valid_anagram,
    "two-sum": two_sum,
    "group-anagrams": group_anagrams,
    "top-k-frequent-elements": top_k,
    "encode-and-decode-strings": codec,
    "product-of-array-except-self": product_except_self,
    "valid-sudoku": valid_sudoku,
    "longest-consecutive-sequence": longest_consecutive,
}


def run(slug, ns):
    if slug not in CHECKS:
        raise AssertionError(f"no checks for {slug} in page_tests.py")
    CHECKS[slug](ns)
