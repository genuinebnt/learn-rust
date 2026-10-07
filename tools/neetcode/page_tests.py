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


def valid_palindrome(ns):
    f = ns["Solution"]().isPalindrome
    assert f("A man, a plan, a canal: Panama") and not f("race a car") and f(" ") and f("")
    r = rng()
    for _ in range(400):
        s = "".join(r.choice("aAb1 ,.") for _ in range(r.randint(0, 9)))
        t = [c.lower() for c in s if c.isalnum()]
        assert f(s) == (t == t[::-1]), s


def two_sum_ii(ns):
    f = ns["Solution"]().twoSum
    assert f([2, 7, 11, 15], 9) == [1, 2] and f([2, 3, 4], 6) == [1, 3] and f([-1, 0], -1) == [1, 2]
    r = rng()
    for _ in range(300):
        a = sorted(r.randint(-10, 10) for _ in range(r.randint(2, 9)))
        i, j = sorted(r.sample(range(len(a)), 2))
        target = a[i] + a[j]
        # the problem promises one solution; skip inputs with several
        pairs = [(x, y) for x in range(len(a)) for y in range(x + 1, len(a)) if a[x] + a[y] == target]
        if len(pairs) != 1:
            continue
        assert f(list(a), target) == [i + 1, j + 1], (a, target)


def three_sum(ns):
    f = ns["Solution"]().threeSum
    norm = lambda g: sorted(sorted(x) for x in g)
    assert norm(f([-1, 0, 1, 2, -1, -4])) == [[-1, -1, 2], [-1, 0, 1]] and f([0, 1, 1]) == [] and norm(f([0, 0, 0])) == [[0, 0, 0]]
    r = rng()
    for _ in range(300):
        a = [r.randint(-5, 5) for _ in range(r.randint(0, 10))]
        want = set()
        for i in range(len(a)):
            for j in range(i + 1, len(a)):
                for k in range(j + 1, len(a)):
                    if a[i] + a[j] + a[k] == 0:
                        want.add(tuple(sorted((a[i], a[j], a[k]))))
        got = norm(f(list(a)))
        assert got == sorted(sorted(t) for t in want) and len(got) == len({tuple(x) for x in got}), a


def container(ns):
    f = ns["Solution"]().maxArea
    assert f([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49 and f([1, 1]) == 1
    r = rng()
    for _ in range(300):
        a = [r.randint(0, 12) for _ in range(r.randint(2, 10))]
        want = max((j - i) * min(a[i], a[j]) for i in range(len(a)) for j in range(i + 1, len(a)))
        assert f(list(a)) == want, a


def trap(ns):
    f = ns["Solution"]().trap
    assert f([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6 and f([4, 2, 0, 3, 2, 5]) == 9 and f([]) == 0 and f([3]) == 0
    r = rng()
    for _ in range(300):
        a = [r.randint(0, 6) for _ in range(r.randint(0, 12))]
        want = sum(max(0, min(max(a[: i + 1]), max(a[i:])) - a[i]) for i in range(len(a)))
        assert f(list(a)) == want, a


def best_time(ns):
    f = ns["Solution"]().maxProfit
    assert f([7, 1, 5, 3, 6, 4]) == 5 and f([7, 6, 4, 3, 1]) == 0 and f([5]) == 0
    r = rng()
    for _ in range(300):
        a = [r.randint(0, 10) for _ in range(r.randint(1, 10))]
        want = max([0] + [a[j] - a[i] for i in range(len(a)) for j in range(i + 1, len(a))])
        assert f(list(a)) == want, a


def longest_substring(ns):
    f = ns["Solution"]().lengthOfLongestSubstring
    assert f("abcabcbb") == 3 and f("bbbbb") == 1 and f("pwwkew") == 3 and f("") == 0 and f(" ") == 1 and f("abba") == 2
    r = rng()
    for _ in range(400):
        s = "".join(r.choice("abcd") for _ in range(r.randint(0, 10)))
        want = max([len(s[i:j]) for i in range(len(s)) for j in range(i, len(s) + 1) if len(set(s[i:j])) == j - i] + [0])
        assert f(s) == want, s


def char_replacement(ns):
    f = ns["Solution"]().characterReplacement
    assert f("ABAB", 2) == 4 and f("AABABBA", 1) == 4 and f("A", 0) == 1
    r = rng()
    for _ in range(400):
        s = "".join(r.choice("ABC") for _ in range(r.randint(1, 10)))
        k = r.randint(0, 3)
        want = 0
        for i in range(len(s)):
            for j in range(i, len(s)):
                w = s[i : j + 1]
                if len(w) - max(w.count(c) for c in set(w)) <= k:
                    want = max(want, len(w))
        assert f(s, k) == want, (s, k)


def permutation_in_string(ns):
    f = ns["Solution"]().checkInclusion
    assert f("ab", "eidbaooo") is True and f("ab", "eidboaoo") is False and f("abc", "ab") is False
    r = rng()
    for _ in range(400):
        a = "".join(r.choice("abc") for _ in range(r.randint(1, 4)))
        b = "".join(r.choice("abc") for _ in range(r.randint(0, 9)))
        want = any(sorted(b[i : i + len(a)]) == sorted(a) for i in range(len(b) - len(a) + 1))
        assert f(a, b) == want, (a, b)


def min_window(ns):
    f = ns["Solution"]().minWindow
    assert f("ADOBECODEBANC", "ABC") == "BANC" and f("a", "a") == "a" and f("a", "aa") == "" and f("ab", "b") == "b"
    r = rng()
    for _ in range(300):
        s = "".join(r.choice("abc") for _ in range(r.randint(1, 9)))
        t = "".join(r.choice("abc") for _ in range(r.randint(1, 3)))
        best = None
        for i in range(len(s)):
            for j in range(i + 1, len(s) + 1):
                if not (Counter(t) - Counter(s[i:j])) and (best is None or j - i < len(best)):
                    best = s[i:j]
        got = f(s, t)
        assert len(got) == len(best or "") and (not best or not (Counter(t) - Counter(got)) and got in s), (s, t, got, best)


def sliding_max(ns):
    f = ns["Solution"]().maxSlidingWindow
    assert f([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7] and f([1], 1) == [1]
    r = rng()
    for _ in range(300):
        a = [r.randint(-6, 6) for _ in range(r.randint(1, 12))]
        k = r.randint(1, len(a))
        assert f(list(a), k) == [max(a[i : i + k]) for i in range(len(a) - k + 1)], (a, k)


def valid_parentheses(ns):
    f = ns["Solution"]().isValid
    assert f("()") and f("()[]{}") and not f("(]") and f("([])") and not f("(") and not f(")") and not f("([)]")
    r = rng()

    def ref(s):
        st = []
        for c in s:
            if c in "([{":
                st.append(c)
            elif not st or "([{".index(st.pop()) != ")]}".index(c):
                return False
        return not st

    for _ in range(500):
        s = "".join(r.choice("()[]{}") for _ in range(r.randint(1, 8)))
        assert f(s) == ref(s), s


def min_stack(ns):
    r = rng()
    for _ in range(100):
        m, ref = ns["MinStack"](), []
        for _ in range(30):
            if ref and r.random() < 0.4:
                m.pop()
                ref.pop()
            else:
                v = r.randint(-5, 5)
                m.push(v)
                ref.append(v)
            if ref:
                assert m.top() == ref[-1] and m.getMin() == min(ref), ref


def eval_rpn(ns):
    f = ns["Solution"]().evalRPN
    assert f(["2", "1", "+", "3", "*"]) == 9 and f(["4", "13", "5", "/", "+"]) == 6
    assert f(["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]) == 22 and f(["7", "-2", "/"]) == -3 and f(["3", "4", "-"]) == -1
    r = rng()

    def build(depth):
        if depth == 0 or r.random() < 0.3:
            n = r.randint(-9, 9)
            return [str(n)], n
        lt, lv = build(depth - 1)
        rt, rv = build(depth - 1)
        op = r.choice("+-*/")
        if op == "/" and rv == 0:
            op = "+"
        val = {"+": lv + rv, "-": lv - rv, "*": lv * rv, "/": int(lv / rv) if rv else 0}[op]
        return lt + rt + [op], val

    for _ in range(300):
        toks, val = build(3)
        assert f(list(toks)) == val, toks


def daily_temperatures(ns):
    f = ns["Solution"]().dailyTemperatures
    assert f([73, 74, 75, 71, 69, 72, 76, 73]) == [1, 1, 4, 2, 1, 1, 0, 0] and f([30, 40, 50, 60]) == [1, 1, 1, 0] and f([30, 60, 90]) == [1, 1, 0]
    r = rng()
    for _ in range(300):
        a = [r.randint(30, 40) for _ in range(r.randint(1, 12))]
        want = []
        for i in range(len(a)):
            d = next((j - i for j in range(i + 1, len(a)) if a[j] > a[i]), 0)
            want.append(d)
        assert f(list(a)) == want, a


def car_fleet(ns):
    f = ns["Solution"]().carFleet
    assert f(12, [10, 8, 0, 5, 3], [2, 4, 1, 1, 3]) == 3 and f(10, [3], [3]) == 1 and f(100, [0, 2, 4], [4, 2, 1]) == 1
    r = rng()
    for _ in range(300):
        n = r.randint(1, 6)
        target = r.randint(5, 20)
        pos = r.sample(range(0, target), min(n, target))
        spd = [r.randint(1, 5) for _ in pos]
        # simulate with exact fractions: a car's arrival is the max of its own time and the car ahead's
        from fractions import Fraction

        cars = sorted(zip(pos, spd), reverse=True)
        fleets, ahead = 0, Fraction(0)
        for p, s_ in cars:
            t = Fraction(target - p, s_)
            if t > ahead:
                fleets, ahead = fleets + 1, t
        assert f(target, list(pos), list(spd)) == fleets, (target, pos, spd)


def largest_rectangle(ns):
    f = ns["Solution"]().largestRectangleArea
    assert f([2, 1, 5, 6, 2, 3]) == 10 and f([2, 4]) == 4 and f([1]) == 1 and f([2, 2]) == 4 and f([0, 9]) == 9
    r = rng()
    for _ in range(300):
        a = [r.randint(0, 8) for _ in range(r.randint(1, 10))]
        want = max(min(a[i : j + 1]) * (j - i + 1) for i in range(len(a)) for j in range(i, len(a)))
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
    "valid-palindrome": valid_palindrome,
    "two-sum-ii-input-array-is-sorted": two_sum_ii,
    "3sum": three_sum,
    "container-with-most-water": container,
    "trapping-rain-water": trap,
    "best-time-to-buy-and-sell-stock": best_time,
    "longest-substring-without-repeating-characters": longest_substring,
    "longest-repeating-character-replacement": char_replacement,
    "permutation-in-string": permutation_in_string,
    "minimum-window-substring": min_window,
    "sliding-window-maximum": sliding_max,
    "valid-parentheses": valid_parentheses,
    "min-stack": min_stack,
    "evaluate-reverse-polish-notation": eval_rpn,
    "daily-temperatures": daily_temperatures,
    "car-fleet": car_fleet,
    "largest-rectangle-in-histogram": largest_rectangle,
}


def run(slug, ns):
    if slug not in CHECKS:
        raise AssertionError(f"no checks for {slug} in page_tests.py")
    CHECKS[slug](ns)
