"""Behavioural checks for the solutions in content/dsa/pages. run(slug, namespace) raises on a wrong answer.

Each check compares against a brute-force reference on the problem's examples and on random inputs, so a page can't
ship a solution that only passes the sample.
"""
import math
import random
from collections import Counter, defaultdict


class Node:
    """LeetCode's Node for Clone Graph."""

    def __init__(self, val=0, neighbors=None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []


PROVIDED_CLASSES = {"Node": Node}


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


# ---------------------------------------------------------------- graphs

import copy
import itertools
from collections import deque


def _grid(r, rows, cols, values, weights=None):
    return [[r.choices(values, weights)[0] for _ in range(cols)] for _ in range(rows)]


def _components(grid, land):
    rows, cols = len(grid), len(grid[0])
    seen, sizes = set(), []
    for r0 in range(rows):
        for c0 in range(cols):
            if grid[r0][c0] != land or (r0, c0) in seen:
                continue
            seen.add((r0, c0))
            q, n = deque([(r0, c0)]), 0
            while q:
                a, b = q.popleft()
                n += 1
                for x, y in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)):
                    if 0 <= x < rows and 0 <= y < cols and grid[x][y] == land and (x, y) not in seen:
                        seen.add((x, y))
                        q.append((x, y))
            sizes.append(n)
    return sizes


def number_of_islands(ns):
    f = ns["Solution"]().numIslands
    assert f([list("11110"), list("11010"), list("11000"), list("00000")]) == 1
    assert f([list("11000"), list("11000"), list("00100"), list("00011")]) == 3
    r = rng()
    for _ in range(300):
        g = _grid(r, r.randint(1, 6), r.randint(1, 6), ["0", "1"])
        assert f(copy.deepcopy(g)) == len(_components(g, "1")), g


def max_area_of_island(ns):
    f = ns["Solution"]().maxAreaOfIsland
    assert f([[0, 0, 0, 0, 0, 0, 0, 0]]) == 0 and f([[1, 1, 0], [0, 1, 0], [1, 0, 1]]) == 3
    r = rng()
    for _ in range(300):
        g = _grid(r, r.randint(1, 6), r.randint(1, 6), [0, 1])
        assert f(copy.deepcopy(g)) == max(_components(g, 1) + [0]), g


def clone_graph(ns):
    f = ns["Solution"]().cloneGraph
    Node = ns["Node"]
    assert f(None) is None
    r = rng()
    for _ in range(200):
        n = r.randint(1, 7)
        nodes = [Node(i + 1) for i in range(n)]
        pairs = [r.sample(range(n), 2) for _ in range(r.randint(0, 8))] if n > 1 else []
        edges = {(min(a, b), max(a, b)) for a, b in pairs}
        for a, b in sorted(edges):
            nodes[a].neighbors.append(nodes[b])
            nodes[b].neighbors.append(nodes[a])

        def shape(start):
            seen, order, q = {start}, [], deque([start])
            while q:
                x = q.popleft()
                order.append(x)
                for y in x.neighbors:
                    if y not in seen:
                        seen.add(y)
                        q.append(y)
            return order

        original = shape(nodes[0])
        copy_root = f(nodes[0])
        cloned = shape(copy_root)
        assert len(cloned) == len(original)
        assert not ({id(x) for x in cloned} & {id(x) for x in original}), "shares nodes with the original"
        assert [(x.val, [y.val for y in x.neighbors]) for x in original] == [(x.val, [y.val for y in x.neighbors]) for x in cloned]


def walls_and_gates(ns):
    f = ns["Solution"]().wallsAndGates
    INF = 2147483647
    g = [[INF, -1, 0, INF], [INF, INF, INF, -1], [INF, -1, INF, -1], [0, -1, INF, INF]]
    f(g)
    assert g == [[3, -1, 0, 1], [2, 2, 1, -1], [1, -1, 2, -1], [0, -1, 3, 4]]
    r = rng()
    for _ in range(300):
        g = _grid(r, r.randint(1, 5), r.randint(1, 5), [INF, -1, 0], [5, 2, 2])
        want = copy.deepcopy(g)
        gates = [(a, b) for a in range(len(g)) for b in range(len(g[0])) if g[a][b] == 0]
        for a in range(len(g)):
            for b in range(len(g[0])):
                if g[a][b] != INF:
                    continue
                best = INF
                q, seen = deque([(a, b, 0)]), {(a, b)}
                while q:
                    x, y, d = q.popleft()
                    if g[x][y] == 0:
                        best = d
                        break
                    for u, v in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                        if 0 <= u < len(g) and 0 <= v < len(g[0]) and g[u][v] != -1 and (u, v) not in seen:
                            seen.add((u, v))
                            q.append((u, v, d + 1))
                want[a][b] = best
        got = copy.deepcopy(g)
        f(got)
        assert got == want, (g, got, want)


def rotting_oranges(ns):
    f = ns["Solution"]().orangesRotting
    assert f([[2, 1, 1], [1, 1, 0], [0, 1, 1]]) == 4 and f([[2, 1, 1], [0, 1, 1], [1, 0, 1]]) == -1 and f([[0, 2]]) == 0 and f([[0]]) == 0
    r = rng()
    for _ in range(300):
        g = _grid(r, r.randint(1, 5), r.randint(1, 5), [0, 1, 2], [2, 4, 1])
        cur, minutes = copy.deepcopy(g), 0
        while True:
            nxt = copy.deepcopy(cur)
            changed = False
            for a in range(len(cur)):
                for b in range(len(cur[0])):
                    if cur[a][b] == 1 and any(0 <= u < len(cur) and 0 <= v < len(cur[0]) and cur[u][v] == 2 for u, v in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1))):
                        nxt[a][b] = 2
                        changed = True
            if not changed:
                break
            cur, minutes = nxt, minutes + 1
        want = -1 if any(1 in row for row in cur) else minutes
        assert f(copy.deepcopy(g)) == want, g


def pacific_atlantic(ns):
    f = ns["Solution"]().pacificAtlantic
    h = [[1, 2, 2, 3, 5], [3, 2, 3, 4, 4], [2, 4, 5, 3, 1], [6, 7, 1, 4, 5], [5, 1, 1, 2, 4]]
    assert sorted(f(h)) == sorted([[0, 4], [1, 3], [1, 4], [2, 2], [3, 0], [3, 1], [4, 0]]) and f([[1]]) == [[0, 0]]
    r = rng()
    for _ in range(200):
        g = _grid(r, r.randint(1, 5), r.randint(1, 5), [1, 2, 3, 4])
        R, C = len(g), len(g[0])

        def reaches(a, b, ocean):
            seen, st = {(a, b)}, [(a, b)]
            while st:
                x, y = st.pop()
                if (ocean == "p" and (x == 0 or y == 0)) or (ocean == "a" and (x == R - 1 or y == C - 1)):
                    return True
                for u, v in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= u < R and 0 <= v < C and (u, v) not in seen and g[u][v] <= g[x][y]:
                        seen.add((u, v))
                        st.append((u, v))
            return False

        want = sorted([a, b] for a in range(R) for b in range(C) if reaches(a, b, "p") and reaches(a, b, "a"))
        assert sorted(f(copy.deepcopy(g))) == want, g


def surrounded_regions(ns):
    f = ns["Solution"]().solve
    b = [list("XXXX"), list("XOOX"), list("XXOX"), list("XOXX")]
    f(b)
    assert b == [list("XXXX"), list("XXXX"), list("XXXX"), list("XOXX")]
    r = rng()
    for _ in range(300):
        g = _grid(r, r.randint(1, 6), r.randint(1, 6), ["X", "O"])
        R, C = len(g), len(g[0])
        safe, st = set(), [(a, c) for a in range(R) for c in range(C) if g[a][c] == "O" and (a in (0, R - 1) or c in (0, C - 1))]
        safe.update(st)
        while st:
            x, y = st.pop()
            for u, v in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= u < R and 0 <= v < C and g[u][v] == "O" and (u, v) not in safe:
                    safe.add((u, v))
                    st.append((u, v))
        want = [["O" if (a, c) in safe else "X" for c in range(C)] for a in range(R)]
        got = copy.deepcopy(g)
        f(got)
        assert got == want, g


def _has_cycle(n, prereqs):
    reach = [[False] * n for _ in range(n)]
    for a, b in prereqs:
        reach[b][a] = True
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if reach[i][k] and reach[k][j]:
                    reach[i][j] = True
    return any(reach[i][i] for i in range(n))


def course_schedule(ns):
    f = ns["Solution"]().canFinish
    assert f(2, [[1, 0]]) is True and f(2, [[1, 0], [0, 1]]) is False and f(1, []) is True
    r = rng()
    for _ in range(400):
        n = r.randint(1, 6)
        pre = [[r.randrange(n), r.randrange(n)] for _ in range(r.randint(0, 8))]
        pre = [p for p in pre if p[0] != p[1] or r.random() < 0.2]
        assert f(n, copy.deepcopy(pre)) == (not _has_cycle(n, pre)), (n, pre)


def course_schedule_ii(ns):
    f = ns["Solution"]().findOrder
    assert f(2, [[1, 0]]) == [0, 1] and f(1, []) == [0] and f(2, [[1, 0], [0, 1]]) == []
    r = rng()
    for _ in range(400):
        n = r.randint(1, 6)
        pre = [[r.randrange(n), r.randrange(n)] for _ in range(r.randint(0, 8))]
        got = f(n, copy.deepcopy(pre))
        if _has_cycle(n, pre):
            assert got == [], (n, pre)
        else:
            assert sorted(got) == list(range(n)), (n, pre, got)
            pos = {c: i for i, c in enumerate(got)}
            assert all(pos[b] < pos[a] for a, b in pre), (n, pre, got)


def _is_tree(n, edges):
    if len(edges) != n - 1:
        return False
    comp = list(range(n))
    for a, b in edges:
        ca, cb = comp[a], comp[b]
        comp = [ca if c == cb else c for c in comp]
    return len(set(comp)) == 1


def graph_valid_tree(ns):
    f = ns["Solution"]().validTree
    assert f(5, [[0, 1], [0, 2], [0, 3], [1, 4]]) is True and f(5, [[0, 1], [1, 2], [2, 3], [1, 3], [1, 4]]) is False and f(1, []) is True and f(2, []) is False
    r = rng()
    for _ in range(500):
        n = r.randint(1, 7)
        edges = [r.sample(range(n), 2) for _ in range(r.randint(max(0, n - 2), n)) if n > 1]
        assert f(n, copy.deepcopy(edges)) == _is_tree(n, edges), (n, edges)


def count_components(ns):
    f = ns["Solution"]().countComponents
    assert f(5, [[0, 1], [1, 2], [3, 4]]) == 2 and f(5, [[0, 1], [1, 2], [2, 3], [3, 4]]) == 1 and f(3, []) == 3
    r = rng()
    for _ in range(400):
        n = r.randint(1, 8)
        edges = [r.sample(range(n), 2) for _ in range(r.randint(0, 8)) if n > 1]
        comp = list(range(n))
        for a, b in edges:
            ca, cb = comp[a], comp[b]
            comp = [ca if c == cb else c for c in comp]
        assert f(n, copy.deepcopy(edges)) == len(set(comp)), (n, edges)


def redundant_connection(ns):
    f = ns["Solution"]().findRedundantConnection
    assert f([[1, 2], [1, 3], [2, 3]]) == [2, 3] and f([[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]]) == [1, 4]
    r = rng()
    for _ in range(300):
        n = r.randint(3, 8)
        edges = [[r.randint(1, i), i + 1] for i in range(1, n)]  # a random tree on 1..n
        a, b = r.sample(range(1, n + 1), 2)
        if [a, b] in edges or [b, a] in edges:
            continue
        edges.insert(r.randint(0, len(edges)), [a, b])
        r.shuffle(edges)
        want = next(e for e in reversed(edges) if _is_tree(n, [x for x in edges if x is not e] and [[u - 1, v - 1] for u, v in edges if u != e[0] or v != e[1]]))
        assert f(copy.deepcopy(edges)) == want, (n, edges)


def word_ladder(ns):
    f = ns["Solution"]().ladderLength
    assert f("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]) == 5 and f("hit", "cog", ["hot", "dot", "dog", "lot", "log"]) == 0
    r = rng()
    for _ in range(300):
        words = list({"".join(r.choice("abc") for _ in range(3)) for _ in range(r.randint(1, 10))})
        begin = "".join(r.choice("abc") for _ in range(3))
        end = r.choice(words)
        if begin == end:
            continue
        nodes = [begin] + [w for w in words if w != begin]
        one = lambda a, b: sum(x != y for x, y in zip(a, b)) == 1
        dist, q = {begin: 1}, deque([begin])
        while q:
            u = q.popleft()
            for w in nodes:
                if w not in dist and one(u, w):
                    dist[w] = dist[u] + 1
                    q.append(w)
        assert f(begin, end, list(words)) == dist.get(end, 0), (begin, end, words)


def network_delay(ns):
    f = ns["Solution"]().networkDelayTime
    assert f([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2) == 2 and f([[1, 2, 1]], 2, 1) == 1 and f([[1, 2, 1]], 2, 2) == -1
    r = rng()
    for _ in range(300):
        n = r.randint(1, 6)
        times = [[r.randint(1, n), r.randint(1, n), r.randint(0, 9)] for _ in range(r.randint(0, 10))]
        times = [t for t in times if t[0] != t[1]]
        k = r.randint(1, n)
        INF = float("inf")
        d = [[INF] * (n + 1) for _ in range(n + 1)]
        for i in range(n + 1):
            d[i][i] = 0
        for u, v, w in times:
            d[u][v] = min(d[u][v], w)
        for m in range(1, n + 1):
            for i in range(1, n + 1):
                for j in range(1, n + 1):
                    d[i][j] = min(d[i][j], d[i][m] + d[m][j])
        far = max(d[k][1:])
        assert f(copy.deepcopy(times), n, k) == (-1 if far == INF else far), (times, n, k)


def reconstruct_itinerary(ns):
    f = ns["Solution"]().findItinerary
    assert f([["MUC", "LHR"], ["JFK", "MUC"], ["SFO", "SJC"], ["LHR", "SFO"]]) == ["JFK", "MUC", "LHR", "SFO", "SJC"]
    assert f([["JFK", "SFO"], ["JFK", "ATL"], ["SFO", "ATL"], ["ATL", "JFK"], ["ATL", "SFO"]]) == ["JFK", "ATL", "JFK", "SFO", "ATL", "SFO"]
    r = rng()
    cities = ["JFK", "A", "B", "C"]
    done = 0
    while done < 200:
        # a random valid trip, so an itinerary always exists
        route = ["JFK"]
        for _ in range(r.randint(1, 7)):
            route.append(r.choice(cities))
        tickets = [[a, b] for a, b in zip(route, route[1:])]
        best = None
        for perm in set(itertools.permutations(range(len(tickets)))):
            path = ["JFK"]
            ok = True
            for i in perm:
                if tickets[i][0] != path[-1]:
                    ok = False
                    break
                path.append(tickets[i][1])
            if ok and (best is None or path < best):
                best = path
        assert f(copy.deepcopy(tickets)) == best, tickets
        done += 1


def min_cost_connect(ns):
    f = ns["Solution"]().minCostConnectPoints
    assert f([[0, 0], [2, 2], [3, 10], [5, 2], [7, 0]]) == 20 and f([[3, 12], [-2, 5], [-4, 1]]) == 18 and f([[0, 0]]) == 0
    r = rng()
    for _ in range(200):
        pts = [[r.randint(-6, 6), r.randint(-6, 6)] for _ in range(r.randint(1, 6))]
        pts = [list(p) for p in {tuple(p) for p in pts}]
        n = len(pts)
        dist = lambda a, b: abs(a[0] - b[0]) + abs(a[1] - b[1])
        # brute force over every spanning tree is too big; use Kruskal on a sorted edge list as the reference
        edges = sorted((dist(pts[i], pts[j]), i, j) for i in range(n) for j in range(i + 1, n))
        comp, total = list(range(n)), 0
        for w, i, j in edges:
            if comp[i] != comp[j]:
                ci, cj = comp[i], comp[j]
                comp = [ci if c == cj else c for c in comp]
                total += w
        assert f(copy.deepcopy(pts)) == total, pts


def swim_in_water(ns):
    f = ns["Solution"]().swimInWater
    assert f([[0, 2], [1, 3]]) == 3 and f([[0]]) == 0
    assert f([[0, 1, 2, 3, 4], [24, 23, 22, 21, 5], [12, 13, 14, 15, 16], [11, 17, 18, 19, 20], [10, 9, 8, 7, 6]]) == 16
    r = rng()
    for _ in range(300):
        n = r.randint(1, 4)
        vals = list(range(n * n))
        r.shuffle(vals)
        g = [vals[i * n : (i + 1) * n] for i in range(n)]
        best = [[float("inf")] * n for _ in range(n)]
        best[0][0] = g[0][0]
        changed = True
        while changed:
            changed = False
            for a in range(n):
                for b in range(n):
                    for u, v in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)):
                        if 0 <= u < n and 0 <= v < n and max(best[u][v], 0) < float("inf"):
                            cand = max(best[u][v], g[a][b])
                            if cand < best[a][b]:
                                best[a][b] = cand
                                changed = True
        assert f(copy.deepcopy(g)) == best[n - 1][n - 1], g


def alien_dictionary(ns):
    f = ns["Solution"]().alienOrder
    assert f(["z", "x", "z"]) == "" and f(["abc", "ab"]) == "" and f(["z", "z"]) == "z"
    got = f(["wrt", "wrf", "er", "ett", "rftt"])
    assert sorted(got) == sorted("wertf") and got.index("e") < got.index("r") < got.index("t") < got.index("f") and got.index("w") < got.index("e")
    r = rng()
    for _ in range(300):
        alphabet = list("abcdef")
        r.shuffle(alphabet)
        key = {c: i for i, c in enumerate(alphabet)}
        words = ["".join(r.choice("abcdef") for _ in range(r.randint(1, 4))) for _ in range(r.randint(1, 6))]
        words.sort(key=lambda w: [key[c] for c in w])
        order = f(list(words))
        letters = set("".join(words))
        assert sorted(order) == sorted(letters), (words, order)
        pos = {c: i for i, c in enumerate(order)}
        assert words == sorted(words, key=lambda w: [pos[c] for c in w]) or all(
            [pos[c] for c in a] <= [pos[c] for c in b] for a, b in zip(words, words[1:])
        ), (words, order)


def cheapest_flights(ns):
    f = ns["Solution"]().findCheapestPrice
    assert f(4, [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600], [2, 3, 200]], 0, 3, 1) == 700
    assert f(3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 1) == 200 and f(3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 0) == 500
    r = rng()
    for _ in range(300):
        n = r.randint(2, 5)
        flights = [[r.randrange(n), r.randrange(n), r.randint(1, 9)] for _ in range(r.randint(0, 9))]
        flights = [x for x in flights if x[0] != x[1]]
        src, dst = r.sample(range(n), 2)
        k = r.randint(0, 3)
        best = float("inf")

        def go(city, cost, used):
            nonlocal best
            if city == dst:
                best = min(best, cost)
                return
            if used > k:
                return
            for u, v, w in flights:
                if u == city:
                    go(v, cost + w, used + 1)

        go(src, 0, 0)
        assert f(n, copy.deepcopy(flights), src, dst, k) == (-1 if best == float("inf") else best), (n, flights, src, dst, k)


# ---------------------------------------------------------------- greedy and intervals


def maximum_subarray(ns):
    f = ns["Solution"]().maxSubArray
    assert f([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6 and f([1]) == 1 and f([5, 4, -1, 7, 8]) == 23 and f([-3, -1, -2]) == -1
    r = rng()
    for _ in range(400):
        a = [r.randint(-6, 6) for _ in range(r.randint(1, 10))]
        want = max(sum(a[i : j + 1]) for i in range(len(a)) for j in range(i, len(a)))
        assert f(list(a)) == want, a


def jump_game(ns):
    f = ns["Solution"]().canJump
    assert f([2, 3, 1, 1, 4]) is True and f([3, 2, 1, 0, 4]) is False and f([0]) is True and f([0, 1]) is False
    r = rng()
    for _ in range(500):
        a = [r.randint(0, 3) for _ in range(r.randint(1, 9))]
        reach = [False] * len(a)
        reach[0] = True
        for i in range(len(a)):
            if reach[i]:
                for j in range(i + 1, min(len(a), i + a[i] + 1)):
                    reach[j] = True
        assert f(list(a)) == reach[-1], a


def jump_game_ii(ns):
    f = ns["Solution"]().jump
    assert f([2, 3, 1, 1, 4]) == 2 and f([2, 3, 0, 1, 4]) == 2 and f([0]) == 0 and f([1, 2, 3]) == 2
    r = rng()
    n_checked = 0
    for _ in range(800):
        a = [r.randint(0, 4) for _ in range(r.randint(1, 9))]
        best = [float("inf")] * len(a)
        best[0] = 0
        for i in range(len(a)):
            for j in range(i + 1, min(len(a), i + a[i] + 1)):
                best[j] = min(best[j], best[i] + 1)
        if best[-1] == float("inf"):
            continue  # the problem guarantees the end is reachable
        assert f(list(a)) == best[-1], a
        n_checked += 1
    assert n_checked > 100


def gas_station(ns):
    f = ns["Solution"]().canCompleteCircuit
    assert f([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]) == 3 and f([2, 3, 4], [3, 4, 3]) == -1 and f([5], [4]) == 0
    r = rng()
    for _ in range(500):
        n = r.randint(1, 7)
        gas = [r.randint(0, 6) for _ in range(n)]
        cost = [r.randint(0, 6) for _ in range(n)]
        ok = []
        for s in range(n):
            tank = 0
            for k in range(n):
                i = (s + k) % n
                tank += gas[i] - cost[i]
                if tank < 0:
                    break
            else:
                ok.append(s)
        if len(ok) > 1:
            continue  # the problem guarantees a unique answer
        assert f(list(gas), list(cost)) == (ok[0] if ok else -1), (gas, cost)


def hand_of_straights(ns):
    f = ns["Solution"]().isNStraightHand
    assert f([1, 2, 3, 6, 2, 3, 4, 7, 8], 3) is True and f([1, 2, 3, 4, 5], 4) is False and f([1], 1) is True and f([1, 1, 2, 2, 3, 3], 3) is True
    r = rng()
    for _ in range(500):
        size = r.randint(1, 3)
        hand = [r.randint(0, 6) for _ in range(size * r.randint(1, 3))]
        pool = Counter(hand)
        ok = True
        while pool:
            lo = min(pool)
            for c in range(lo, lo + size):
                if pool[c] <= 0:
                    ok = False
                    break
                pool[c] -= 1
                if pool[c] == 0:
                    del pool[c]
            if not ok:
                break
        assert f(list(hand), size) == ok, (hand, size)


def merge_triplets(ns):
    f = ns["Solution"]().mergeTriplets
    assert f([[2, 5, 3], [1, 8, 4], [1, 7, 5]], [2, 7, 5]) is True and f([[3, 4, 5], [4, 5, 6]], [3, 2, 5]) is False
    assert f([[2, 5, 3], [2, 3, 4], [1, 2, 5], [5, 2, 3]], [5, 5, 5]) is True
    r = rng()
    for _ in range(500):
        ts = [[r.randint(1, 4) for _ in range(3)] for _ in range(r.randint(1, 5))]
        target = [r.randint(1, 4) for _ in range(3)]
        best = False
        for mask in range(1, 1 << len(ts)):
            cur = [0, 0, 0]
            for i, t in enumerate(ts):
                if mask >> i & 1:
                    cur = [max(a, b) for a, b in zip(cur, t)]
            if cur == target:
                best = True
                break
        assert f([list(t) for t in ts], list(target)) == best, (ts, target)


def partition_labels(ns):
    f = ns["Solution"]().partitionLabels
    assert f("ababcbacadefegdehijhklij") == [9, 7, 8] and f("eccbbbbdec") == [10] and f("a") == [1]
    r = rng()
    for _ in range(400):
        s = "".join(r.choice("abcd") for _ in range(r.randint(1, 10)))
        got = f(s)
        assert sum(got) == len(s)
        parts, i = [], 0
        for size in got:
            parts.append(s[i : i + size])
            i += size
        assert all(not (set(a) & set(b)) for a, b in itertools.combinations(parts, 2)), (s, got)
        # the most parts possible: one more cut anywhere would split a letter
        cuts = [i for i in range(1, len(s)) if not (set(s[:i]) & set(s[i:]))]
        assert len(got) == len(cuts) + 1, (s, got)


def valid_parenthesis_string(ns):
    f = ns["Solution"]().checkValidString
    assert f("()") is True and f("(*)") is True and f("(*))") is True and f(")(") is False and f("(") is False and f("*") is True
    assert f("(((*)") is False and f("((*)") is True and f("((**") is True and f("**((") is False
    r = rng()

    def ref(s, i=0, open_=0):
        if open_ < 0:
            return False
        if i == len(s):
            return open_ == 0
        c = s[i]
        if c == "(":
            return ref(s, i + 1, open_ + 1)
        if c == ")":
            return ref(s, i + 1, open_ - 1)
        return ref(s, i + 1, open_ + 1) or ref(s, i + 1, open_ - 1) or ref(s, i + 1, open_)

    for _ in range(800):
        s = "".join(r.choice("()*") for _ in range(r.randint(1, 10)))
        assert f(s) == ref(s), s


def _merged(iv):
    out = []
    for a, b in sorted(iv):
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def _rand_intervals(r, n=6, hi=12, min_len=0):
    out = []
    for _ in range(r.randint(1, n)):
        a = r.randint(0, hi)
        out.append([a, a + r.randint(min_len, 4)])
    return out


def insert_interval(ns):
    f = ns["Solution"]().insert
    assert f([[1, 3], [6, 9]], [2, 5]) == [[1, 5], [6, 9]]
    assert f([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]) == [[1, 2], [3, 10], [12, 16]] and f([], [5, 7]) == [[5, 7]]
    r = rng()
    for _ in range(400):
        base = _merged(_rand_intervals(r))
        base = [x for x in base]
        # the problem's input is sorted and non-overlapping (touching intervals are merged, so use the merged form)
        new = [r.randint(0, 14)] * 2
        new[1] += r.randint(0, 4)
        want = _merged(base + [new])
        assert f([list(x) for x in base], list(new)) == want, (base, new)


def merge_intervals(ns):
    f = ns["Solution"]().merge
    assert f([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]] and f([[1, 4], [4, 5]]) == [[1, 5]] and f([[1, 10], [2, 3]]) == [[1, 10]]
    r = rng()
    for _ in range(400):
        iv = _rand_intervals(r)
        assert f([list(x) for x in iv]) == _merged(iv), iv


def non_overlapping(ns):
    f = ns["Solution"]().eraseOverlapIntervals
    assert f([[1, 2], [2, 3], [3, 4], [1, 3]]) == 1 and f([[1, 2], [1, 2], [1, 2]]) == 2 and f([[1, 2], [2, 3]]) == 0
    r = rng()
    for _ in range(300):
        iv = _rand_intervals(r, 7, 10, min_len=1)
        best = 0
        for mask in range(1 << len(iv)):
            kept = sorted(iv[i] for i in range(len(iv)) if mask >> i & 1)
            if all(kept[i][1] <= kept[i + 1][0] for i in range(len(kept) - 1)):
                best = max(best, len(kept))
        assert f([list(x) for x in iv]) == len(iv) - best, iv


def meeting_rooms(ns):
    f = ns["Solution"]().canAttendMeetings
    assert f([[0, 30], [5, 10], [15, 20]]) is False and f([[7, 10], [2, 4]]) is True and f([]) is True and f([[1, 2], [2, 3]]) is True
    r = rng()
    for _ in range(400):
        iv = _rand_intervals(r, 6, 10, min_len=1)
        ok = all(a[1] <= b[0] or b[1] <= a[0] for a, b in itertools.combinations(iv, 2))
        assert f([list(x) for x in iv]) == ok, iv


def meeting_rooms_ii(ns):
    f = ns["Solution"]().minMeetingRooms
    assert f([[0, 30], [5, 10], [15, 20]]) == 2 and f([[7, 10], [2, 4]]) == 1 and f([[1, 2], [2, 3]]) == 1
    r = rng()
    for _ in range(400):
        iv = _rand_intervals(r, 8, 10, min_len=1)
        want = max(sum(1 for a, b in iv if a <= t < b) for t in range(0, 20))
        assert f([list(x) for x in iv]) == want, iv


def min_interval(ns):
    f = ns["Solution"]().minInterval
    assert f([[1, 4], [2, 4], [3, 6], [4, 4]], [2, 3, 4, 5]) == [3, 3, 1, 4] and f([[2, 3], [2, 5], [1, 8], [20, 25]], [2, 19, 5, 22]) == [2, -1, 4, 6]
    r = rng()
    for _ in range(300):
        iv = _rand_intervals(r, 6, 12)
        qs = [r.randint(0, 18) for _ in range(r.randint(1, 6))]
        want = [min([b - a + 1 for a, b in iv if a <= q <= b], default=-1) for q in qs]
        assert f([list(x) for x in iv], list(qs)) == want, (iv, qs)


# ---------------------------------------------------------------- 1-D dynamic programming


def climbing_stairs(ns):
    f = ns["Solution"]().climbStairs
    assert [f(n) for n in range(1, 8)] == [1, 2, 3, 5, 8, 13, 21] and f(45) == 1836311903

    def ways(n):
        return 1 if n <= 1 else ways(n - 1) + ways(n - 2)

    for n in range(1, 15):
        assert f(n) == ways(n), n


def min_cost_climbing(ns):
    f = ns["Solution"]().minCostClimbingStairs
    assert f([10, 15, 20]) == 15 and f([1, 100, 1, 1, 1, 100, 1, 1, 100, 1]) == 6 and f([5, 5]) == 5
    r = rng()
    for _ in range(300):
        c = [r.randint(0, 20) for _ in range(r.randint(2, 9))]
        n = len(c)
        best = None
        for start in (0, 1):
            cost = {start: c[start]}
            for i in range(start + 1, n):
                cost[i] = c[i] + min(cost.get(i - 1, 10**9), cost.get(i - 2, 10**9))
            for last in (n - 1, n - 2):
                if last in cost:
                    best = cost[last] if best is None else min(best, cost[last])
        assert f(list(c)) == best, c


def house_robber(ns):
    f = ns["Solution"]().rob
    assert f([1, 2, 3, 1]) == 4 and f([2, 7, 9, 3, 1]) == 12 and f([5]) == 5 and f([2, 1]) == 2
    r = rng()
    for _ in range(300):
        a = [r.randint(0, 9) for _ in range(r.randint(1, 10))]
        want = max(sum(a[i] for i in range(len(a)) if m >> i & 1) for m in range(1 << len(a)) if not any(m >> i & 1 and m >> (i + 1) & 1 for i in range(len(a) - 1)))
        assert f(list(a)) == want, a


def house_robber_ii(ns):
    f = ns["Solution"]().rob
    assert f([2, 3, 2]) == 3 and f([1, 2, 3, 1]) == 4 and f([1, 2, 3]) == 3 and f([5]) == 5
    r = rng()
    for _ in range(300):
        a = [r.randint(0, 9) for _ in range(r.randint(1, 9))]
        n = len(a)
        best = 0
        for m in range(1 << n):
            ok = all(not (m >> i & 1 and m >> ((i + 1) % n) & 1) for i in range(n)) if n > 1 else True
            if ok:
                best = max(best, sum(a[i] for i in range(n) if m >> i & 1))
        assert f(list(a)) == best, a


def longest_palindromic_substring(ns):
    f = ns["Solution"]().longestPalindrome
    assert f("babad") in ("bab", "aba") and f("cbbd") == "bb" and f("a") == "a" and f("ac") in ("a", "c")
    r = rng()
    for _ in range(400):
        s = "".join(r.choice("abc") for _ in range(r.randint(1, 10)))
        got = f(s)
        assert got in s and got == got[::-1], (s, got)
        want = max(len(s[i:j]) for i in range(len(s)) for j in range(i + 1, len(s) + 1) if s[i:j] == s[i:j][::-1])
        assert len(got) == want, (s, got, want)


def palindromic_substrings(ns):
    f = ns["Solution"]().countSubstrings
    assert f("abc") == 3 and f("aaa") == 6 and f("a") == 1
    r = rng()
    for _ in range(400):
        s = "".join(r.choice("abc") for _ in range(r.randint(1, 10)))
        want = sum(1 for i in range(len(s)) for j in range(i + 1, len(s) + 1) if s[i:j] == s[i:j][::-1])
        assert f(s) == want, s


def decode_ways(ns):
    f = ns["Solution"]().numDecodings
    assert f("12") == 2 and f("226") == 3 and f("06") == 0 and f("10") == 1 and f("0") == 0 and f("27") == 1 and f("2101") == 1 and f("1") == 1

    def count(s):
        if not s:
            return 1
        if s[0] == "0":
            return 0
        total = count(s[1:])
        if len(s) > 1 and int(s[:2]) <= 26:
            total += count(s[2:])
        return total

    r = rng()
    for _ in range(500):
        s = "".join(r.choice("0123456789") if r.random() < 0.5 else r.choice("12") for _ in range(r.randint(1, 9)))
        assert f(s) == count(s), s


def coin_change(ns):
    f = ns["Solution"]().coinChange
    assert f([1, 2, 5], 11) == 3 and f([2], 3) == -1 and f([1], 0) == 0 and f([1, 3, 4], 6) == 2
    r = rng()
    for _ in range(300):
        coins = sorted({r.randint(1, 7) for _ in range(r.randint(1, 4))})
        amount = r.randint(0, 25)
        best = [0] + [10**9] * amount
        for a in range(1, amount + 1):
            for c in coins:
                if c <= a:
                    best[a] = min(best[a], best[a - c] + 1)
        assert f(list(coins), amount) == (-1 if best[amount] >= 10**9 else best[amount]), (coins, amount)


def max_product_subarray(ns):
    f = ns["Solution"]().maxProduct
    assert f([2, 3, -2, 4]) == 6 and f([-2, 0, -1]) == 0 and f([-2]) == -2 and f([-2, 3, -4]) == 24
    r = rng()
    for _ in range(500):
        a = [r.randint(-3, 3) for _ in range(r.randint(1, 8))]
        want = max(math.prod(a[i:j]) for i in range(len(a)) for j in range(i + 1, len(a) + 1))
        assert f(list(a)) == want, a


def word_break(ns):
    f = ns["Solution"]().wordBreak
    assert f("leetcode", ["leet", "code"]) is True and f("applepenapple", ["apple", "pen"]) is True
    assert f("catsandog", ["cats", "dog", "sand", "and", "cat"]) is False
    r = rng()
    for _ in range(400):
        words = list({"".join(r.choice("ab") for _ in range(r.randint(1, 3))) for _ in range(r.randint(1, 4))})
        s = "".join(r.choice("ab") for _ in range(r.randint(1, 9)))

        def can(i, memo={}):
            if i == len(s):
                return True
            return any(s.startswith(w, i) and can(i + len(w), memo) for w in words)

        assert f(s, list(words)) == can(0, {}), (s, words)
    assert f("a" * 300, ["a", "aa", "aaa"]) is True
    assert f("a" * 299 + "b", ["a", "aa", "aaa"]) is False


def lis(ns):
    f = ns["Solution"]().lengthOfLIS
    assert f([10, 9, 2, 5, 3, 7, 101, 18]) == 4 and f([0, 1, 0, 3, 2, 3]) == 4 and f([7, 7, 7]) == 1 and f([5]) == 1
    r = rng()
    for _ in range(400):
        a = [r.randint(-5, 9) for _ in range(r.randint(1, 10))]
        best = [1] * len(a)
        for i in range(len(a)):
            for j in range(i):
                if a[j] < a[i]:
                    best[i] = max(best[i], best[j] + 1)
        assert f(list(a)) == max(best), a


def partition_equal_subset(ns):
    f = ns["Solution"]().canPartition
    assert f([1, 5, 11, 5]) is True and f([1, 2, 3, 5]) is False and f([1, 1]) is True and f([2]) is False
    r = rng()
    for _ in range(500):
        a = [r.randint(1, 9) for _ in range(r.randint(1, 9))]
        total = sum(a)
        want = total % 2 == 0 and any(sum(a[i] for i in range(len(a)) if m >> i & 1) == total // 2 for m in range(1 << len(a)))
        assert f(list(a)) == want, a


# ---------------------------------------------------------------- 2-D dynamic programming


def unique_paths(ns):
    f = ns["Solution"]().uniquePaths
    assert f(3, 7) == 28 and f(3, 2) == 3 and f(1, 1) == 1 and f(1, 9) == 1 and f(23, 12) == 193536720
    for m in range(1, 7):
        for n in range(1, 7):
            grid = [[1] * n for _ in range(m)]
            for i in range(1, m):
                for j in range(1, n):
                    grid[i][j] = grid[i - 1][j] + grid[i][j - 1]
            assert f(m, n) == grid[-1][-1], (m, n)


def lcs(ns):
    f = ns["Solution"]().longestCommonSubsequence
    assert f("abcde", "ace") == 3 and f("abc", "abc") == 3 and f("abc", "def") == 0
    r = rng()

    def is_subseq(a, b):
        it = iter(b)
        return all(c in it for c in a)

    for _ in range(300):
        a = "".join(r.choice("abc") for _ in range(r.randint(1, 7)))
        b = "".join(r.choice("abc") for _ in range(r.randint(1, 7)))
        want = max(len(c) for k in range(len(a) + 1) for c in map("".join, itertools.combinations(a, k)) if is_subseq(c, b))
        assert f(a, b) == want, (a, b)


def stock_cooldown(ns):
    f = ns["Solution"]().maxProfit
    assert f([1, 2, 3, 0, 2]) == 3 and f([1]) == 0 and f([2, 1]) == 0 and f([1, 2, 4]) == 3
    r = rng()

    def brute(prices, day=0, holding=False, cool=False):
        if day == len(prices):
            return 0
        best = brute(prices, day + 1, holding, False)  # do nothing
        if holding:
            best = max(best, prices[day] + brute(prices, day + 1, False, True))
        elif not cool:
            best = max(best, -prices[day] + brute(prices, day + 1, True, False))
        return best

    for _ in range(400):
        a = [r.randint(1, 8) for _ in range(r.randint(1, 9))]
        assert f(list(a)) == brute(a), a


def coin_change_ii(ns):
    f = ns["Solution"]().change
    assert f(5, [1, 2, 5]) == 4 and f(3, [2]) == 0 and f(10, [10]) == 1 and f(0, [7]) == 1
    r = rng()

    def count(amount, coins):
        if amount == 0:
            return 1
        if amount < 0 or not coins:
            return 0
        return count(amount - coins[0], coins) + count(amount, coins[1:])

    for _ in range(300):
        coins = sorted({r.randint(1, 6) for _ in range(r.randint(1, 4))})
        amount = r.randint(0, 14)
        assert f(amount, list(coins)) == count(amount, coins), (amount, coins)


def target_sum(ns):
    f = ns["Solution"]().findTargetSumWays
    assert f([1, 1, 1, 1, 1], 3) == 5 and f([1], 1) == 1 and f([1], 2) == 0 and f([0, 0, 0], 0) == 8
    r = rng()
    for _ in range(400):
        a = [r.randint(0, 5) for _ in range(r.randint(1, 8))]
        target = r.randint(-8, 8)
        want = sum(1 for signs in itertools.product((1, -1), repeat=len(a)) if sum(x * y for x, y in zip(a, signs)) == target)
        assert f(list(a), target) == want, (a, target)


def interleaving(ns):
    f = ns["Solution"]().isInterleave
    assert f("aabcc", "dbbca", "aadbbcbcac") is True and f("aabcc", "dbbca", "aadbbbaccc") is False and f("", "", "") is True and f("a", "", "c") is False
    assert f("a", "", "aa") is False and f("ab", "", "a") is False and f("", "", "a") is False and f("a", "b", "a") is False
    r = rng()

    def ok(a, b, c):
        if not a and not b:
            return not c
        if not c:
            return False
        return (bool(a) and a[0] == c[0] and ok(a[1:], b, c[1:])) or (bool(b) and b[0] == c[0] and ok(a, b[1:], c[1:]))

    for _ in range(500):
        a = "".join(r.choice("ab") for _ in range(r.randint(0, 5)))
        b = "".join(r.choice("ab") for _ in range(r.randint(0, 5)))
        if r.random() < 0.6:  # build a real interleaving half of the time
            ia, ib, c = 0, 0, ""
            while ia < len(a) or ib < len(b):
                if ib == len(b) or (ia < len(a) and r.random() < 0.5):
                    c += a[ia]
                    ia += 1
                else:
                    c += b[ib]
                    ib += 1
        else:
            c = "".join(r.choice("ab") for _ in range(len(a) + len(b)))
        assert f(a, b, c) == ok(a, b, c), (a, b, c)


def longest_increasing_path(ns):
    f = ns["Solution"]().longestIncreasingPath
    assert f([[9, 9, 4], [6, 6, 8], [2, 1, 1]]) == 4 and f([[3, 4, 5], [3, 2, 6], [2, 2, 1]]) == 4 and f([[1]]) == 1
    r = rng()

    def brute(g, i, j):
        best = 1
        for x, y in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
            if 0 <= x < len(g) and 0 <= y < len(g[0]) and g[x][y] > g[i][j]:
                best = max(best, 1 + brute(g, x, y))
        return best

    for _ in range(300):
        g = [[r.randint(0, 6) for _ in range(3)] for _ in range(r.randint(1, 4))]
        assert f([row[:] for row in g]) == max(brute(g, i, j) for i in range(len(g)) for j in range(3)), g
    snake = [[i * 40 + (j if i % 2 == 0 else 39 - j) for j in range(40)] for i in range(40)]
    assert f(snake) == 1600


def distinct_subsequences(ns):
    f = ns["Solution"]().numDistinct
    assert f("rabbbit", "rabbit") == 3 and f("babgbag", "bag") == 5 and f("a", "b") == 0 and f("abc", "") == 1
    r = rng()
    for _ in range(400):
        s_ = "".join(r.choice("ab") for _ in range(r.randint(1, 9)))
        t = "".join(r.choice("ab") for _ in range(r.randint(1, 4)))
        want = sum(1 for idx in itertools.combinations(range(len(s_)), len(t)) if "".join(s_[i] for i in idx) == t)
        assert f(s_, t) == want, (s_, t)


def edit_distance(ns):
    f = ns["Solution"]().minDistance
    assert f("horse", "ros") == 3 and f("intention", "execution") == 5 and f("", "") == 0 and f("", "abc") == 3 and f("abc", "") == 3 and f("same", "same") == 0
    r = rng()

    def lev(a, b, memo={}):
        key = (a, b)
        if key in memo:
            return memo[key]
        if not a or not b:
            res = len(a) + len(b)
        elif a[-1] == b[-1]:
            res = lev(a[:-1], b[:-1])
        else:
            res = 1 + min(lev(a[:-1], b[:-1]), lev(a[:-1], b), lev(a, b[:-1]))
        memo[key] = res
        return res

    for _ in range(400):
        a = "".join(r.choice("abc") for _ in range(r.randint(0, 7)))
        b = "".join(r.choice("abc") for _ in range(r.randint(0, 7)))
        assert f(a, b) == lev(a, b), (a, b)


def burst_balloons(ns):
    f = ns["Solution"]().maxCoins
    assert f([3, 1, 5, 8]) == 167 and f([1, 5]) == 10 and f([7]) == 7
    r = rng()

    def brute(a):
        if not a:
            return 0
        best = 0
        for i in range(len(a)):
            left = a[i - 1] if i else 1
            right = a[i + 1] if i + 1 < len(a) else 1
            best = max(best, left * a[i] * right + brute(a[:i] + a[i + 1 :]))
        return best

    for _ in range(200):
        a = [r.randint(0, 6) for _ in range(r.randint(1, 7))]
        assert f(list(a)) == brute(a), a


def regex_matching(ns):
    f = ns["Solution"]().isMatch
    assert f("aa", "a") is False and f("aa", "a*") is True and f("ab", ".*") is True and f("aab", "c*a*b") is True and f("mississippi", "mis*is*p*.") is False
    assert f("", "a*b*") is True and f("a", "ab*") is True and f("ab", ".*c") is False
    import re

    r = rng()
    for _ in range(1500):
        p = ""
        for _ in range(r.randint(1, 4)):
            p += r.choice("ab.") + (r.choice(["", "*"]) if r.random() < 0.5 else "")
        text = "".join(r.choice("ab") for _ in range(r.randint(0, 6)))
        assert f(text, p) == (re.fullmatch(p, text) is not None), (text, p)


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
    "number-of-islands": number_of_islands,
    "max-area-of-island": max_area_of_island,
    "clone-graph": clone_graph,
    "walls-and-gates": walls_and_gates,
    "rotting-oranges": rotting_oranges,
    "pacific-atlantic-water-flow": pacific_atlantic,
    "surrounded-regions": surrounded_regions,
    "course-schedule": course_schedule,
    "course-schedule-ii": course_schedule_ii,
    "graph-valid-tree": graph_valid_tree,
    "number-of-connected-components-in-an-undirected-graph": count_components,
    "redundant-connection": redundant_connection,
    "word-ladder": word_ladder,
    "network-delay-time": network_delay,
    "reconstruct-itinerary": reconstruct_itinerary,
    "min-cost-to-connect-all-points": min_cost_connect,
    "swim-in-rising-water": swim_in_water,
    "alien-dictionary": alien_dictionary,
    "cheapest-flights-within-k-stops": cheapest_flights,
    "maximum-subarray": maximum_subarray,
    "jump-game": jump_game,
    "jump-game-ii": jump_game_ii,
    "gas-station": gas_station,
    "hand-of-straights": hand_of_straights,
    "merge-triplets-to-form-target-triplet": merge_triplets,
    "partition-labels": partition_labels,
    "valid-parenthesis-string": valid_parenthesis_string,
    "insert-interval": insert_interval,
    "merge-intervals": merge_intervals,
    "non-overlapping-intervals": non_overlapping,
    "meeting-rooms": meeting_rooms,
    "meeting-rooms-ii": meeting_rooms_ii,
    "minimum-interval-to-include-each-query": min_interval,
    "climbing-stairs": climbing_stairs,
    "min-cost-climbing-stairs": min_cost_climbing,
    "house-robber": house_robber,
    "house-robber-ii": house_robber_ii,
    "longest-palindromic-substring": longest_palindromic_substring,
    "palindromic-substrings": palindromic_substrings,
    "decode-ways": decode_ways,
    "coin-change": coin_change,
    "maximum-product-subarray": max_product_subarray,
    "word-break": word_break,
    "longest-increasing-subsequence": lis,
    "partition-equal-subset-sum": partition_equal_subset,
    "unique-paths": unique_paths,
    "longest-common-subsequence": lcs,
    "best-time-to-buy-and-sell-stock-with-cooldown": stock_cooldown,
    "coin-change-ii": coin_change_ii,
    "target-sum": target_sum,
    "interleaving-string": interleaving,
    "longest-increasing-path-in-a-matrix": longest_increasing_path,
    "distinct-subsequences": distinct_subsequences,
    "edit-distance": edit_distance,
    "burst-balloons": burst_balloons,
    "regular-expression-matching": regex_matching,
}


def run(slug, ns):
    if slug not in CHECKS:
        raise AssertionError(f"no checks for {slug} in page_tests.py")
    CHECKS[slug](ns)
