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


class TreeNode:
    """LeetCode's TreeNode."""

    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class ListNode:
    """LeetCode's ListNode."""

    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


PROVIDED_CLASSES = {"Node": Node, "TreeNode": TreeNode, "ListNode": ListNode}


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


# ---------------------------------------------------------------- binary search


def binary_search(ns):
    f = ns["Solution"]().search
    assert f([-1, 0, 3, 5, 9, 12], 9) == 4 and f([-1, 0, 3, 5, 9, 12], 2) == -1 and f([5], 5) == 0 and f([5], 4) == -1 and f([], 1) == -1
    r = rng()
    for _ in range(500):
        a = sorted(r.sample(range(-20, 20), r.randint(0, 12)))
        t = r.randint(-22, 22)
        assert f(list(a), t) == (a.index(t) if t in a else -1), (a, t)


def search_matrix(ns):
    f = ns["Solution"]().searchMatrix
    m = [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]]
    assert f(m, 3) is True and f(m, 13) is False and f([[1]], 1) is True and f([[1]], 0) is False and f([[]], 1) is False and f([], 1) is False
    r = rng()
    for _ in range(400):
        rows, cols = r.randint(1, 5), r.randint(1, 5)
        values = sorted(r.sample(range(0, 60), rows * cols))
        grid = [values[i * cols : (i + 1) * cols] for i in range(rows)]
        t = r.randint(-2, 62)
        assert f([row[:] for row in grid], t) == (t in values), (grid, t)


def koko(ns):
    f = ns["Solution"]().minEatingSpeed
    assert f([3, 6, 7, 11], 8) == 4 and f([30, 11, 23, 4, 20], 5) == 30 and f([30, 11, 23, 4, 20], 6) == 23 and f([1], 1) == 1 and f([10**9], 2) == 5 * 10**8
    r = rng()
    for _ in range(400):
        piles = [r.randint(1, 30) for _ in range(r.randint(1, 6))]
        h = r.randint(len(piles), len(piles) + 12)
        want = next(k for k in range(1, max(piles) + 1) if sum(-(-p // k) for p in piles) <= h)
        assert f(list(piles), h) == want, (piles, h)


def find_min_rotated(ns):
    f = ns["Solution"]().findMin
    assert f([3, 4, 5, 1, 2]) == 1 and f([4, 5, 6, 7, 0, 1, 2]) == 0 and f([11, 13, 15, 17]) == 11 and f([5]) == 5 and f([2, 1]) == 1
    r = rng()
    for _ in range(500):
        a = sorted(r.sample(range(-30, 30), r.randint(1, 12)))
        k = r.randint(0, len(a) - 1)
        rot = a[k:] + a[:k]
        assert f(list(rot)) == min(a), rot


def search_rotated(ns):
    f = ns["Solution"]().search
    assert f([4, 5, 6, 7, 0, 1, 2], 0) == 4 and f([4, 5, 6, 7, 0, 1, 2], 3) == -1 and f([1], 0) == -1 and f([1], 1) == 0 and f([3, 1], 1) == 1
    r = rng()
    for _ in range(600):
        a = sorted(r.sample(range(-30, 30), r.randint(1, 12)))
        k = r.randint(0, len(a) - 1)
        rot = a[k:] + a[:k]
        t = r.randint(-32, 32)
        assert f(list(rot), t) == (rot.index(t) if t in rot else -1), (rot, t)


def time_map(ns):
    TimeMap = ns["TimeMap"]
    m = TimeMap()
    m.set("foo", "bar", 1)
    assert m.get("foo", 1) == "bar" and m.get("foo", 3) == "bar"
    m.set("foo", "bar2", 4)
    assert m.get("foo", 4) == "bar2" and m.get("foo", 5) == "bar2" and m.get("foo", 3) == "bar" and m.get("foo", 0) == "" and m.get("nope", 9) == ""
    r = rng()
    for _ in range(100):
        m, model, t = TimeMap(), {}, 0
        for _ in range(40):
            t += r.randint(1, 3)
            if r.random() < 0.5:
                key, val = r.choice("abc"), str(r.randint(0, 99))
                m.set(key, val, t)
                model.setdefault(key, []).append((t, val))
            else:
                key, q = r.choice("abcd"), r.randint(0, t + 2)
                want = ""
                for ts, v in model.get(key, []):
                    if ts <= q:
                        want = v
                assert m.get(key, q) == want, (key, q)


def median_two_sorted(ns):
    import statistics

    f = ns["Solution"]().findMedianSortedArrays
    assert f([1, 3], [2]) == 2.0 and f([1, 2], [3, 4]) == 2.5 and f([], [1]) == 1.0 and f([2], []) == 2.0 and f([0, 0], [0, 0]) == 0.0
    r = rng()
    for _ in range(600):
        a = sorted(r.randint(-20, 20) for _ in range(r.randint(0, 8)))
        b = sorted(r.randint(-20, 20) for _ in range(r.randint(0, 8)))
        if not a and not b:
            continue
        assert f(list(a), list(b)) == statistics.median(a + b), (a, b)
    big_a, big_b = list(range(0, 2_000_000, 2)), list(range(1, 2_000_001, 2))
    assert f(big_a, big_b) == 999_999.5


# ---------------------------------------------------------------- backtracking


def _same_sets(got, want):
    """Whether two lists of lists hold the same lists (order of lists irrelevant, no repeats)."""
    got_t = sorted(tuple(x) for x in got)
    want_t = sorted(tuple(x) for x in want)
    return got_t == want_t


def subsets_check(ns):
    f = ns["Solution"]().subsets
    assert _same_sets(f([1, 2, 3]), [[], [1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]]) and f([0]) in ([[], [0]], [[0], []])
    r = rng()
    for _ in range(100):
        a = r.sample(range(-5, 6), r.randint(0, 8))
        want = [list(c) for k in range(len(a) + 1) for c in itertools.combinations(a, k)]
        got = f(list(a))
        assert len(got) == len(want) and sorted(sorted(x) for x in got) == sorted(sorted(x) for x in want), a


def combination_sum_check(ns):
    f = ns["Solution"]().combinationSum

    def want(c, t):
        out = []

        def go(i, rem, path):
            if rem == 0:
                out.append(path[:])
                return
            if i == len(c) or rem < 0:
                return
            path.append(c[i])
            go(i, rem - c[i], path)
            path.pop()
            go(i + 1, rem, path)

        go(0, t, [])
        return out

    assert _same_sets([sorted(x) for x in f([2, 3, 6, 7], 7)], [[2, 2, 3], [7]]) and f([2], 1) == [] and _same_sets([sorted(x) for x in f([2, 3, 5], 8)], [[2, 2, 2, 2], [2, 3, 3], [3, 5]])
    r = rng()
    for _ in range(150):
        c = r.sample(range(1, 9), r.randint(1, 4))
        t = r.randint(1, 14)
        got = [tuple(sorted(x)) for x in f(list(c), t)]
        assert len(got) == len(set(got)) and sorted(got) == sorted(tuple(sorted(x)) for x in want(c, t)), (c, t)


def combination_sum_ii_check(ns):
    f = ns["Solution"]().combinationSum2
    assert _same_sets([sorted(x) for x in f([10, 1, 2, 7, 6, 1, 5], 8)], [[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]]) and _same_sets([sorted(x) for x in f([2, 5, 2, 1, 2], 5)], [[1, 2, 2], [5]])
    r = rng()
    for _ in range(200):
        c = [r.randint(1, 6) for _ in range(r.randint(1, 8))]
        t = r.randint(1, 12)
        want = set()
        for k in range(len(c) + 1):
            for idx in itertools.combinations(range(len(c)), k):
                if sum(c[i] for i in idx) == t:
                    want.add(tuple(sorted(c[i] for i in idx)))
        got = [tuple(sorted(x)) for x in f(list(c), t)]
        assert len(got) == len(set(got)) and set(got) == want, (c, t)


def permutations_check(ns):
    f = ns["Solution"]().permute
    assert _same_sets(f([1, 2, 3]), list(map(list, itertools.permutations([1, 2, 3])))) and f([1]) == [[1]] and _same_sets(f([0, 1]), [[0, 1], [1, 0]])
    r = rng()
    for _ in range(60):
        a = r.sample(range(-9, 10), r.randint(1, 6))
        got = f(list(a))
        assert len(got) == len(set(map(tuple, got))) and _same_sets(got, list(map(list, itertools.permutations(a)))), a


def subsets_ii_check(ns):
    f = ns["Solution"]().subsetsWithDup
    assert _same_sets([sorted(x) for x in f([1, 2, 2])], [[], [1], [2], [1, 2], [2, 2], [1, 2, 2]]) and f([0]) in ([[], [0]], [[0], []])
    r = rng()
    for _ in range(200):
        a = [r.randint(0, 3) for _ in range(r.randint(0, 7))]
        want = {tuple(sorted(c)) for k in range(len(a) + 1) for c in itertools.combinations(a, k)}
        got = [tuple(sorted(x)) for x in f(list(a))]
        assert len(got) == len(set(got)) and set(got) == want, a


def generate_parentheses_check(ns):
    f = ns["Solution"]().generateParenthesis
    assert sorted(f(3)) == sorted(["((()))", "(()())", "(())()", "()(())", "()()()"]) and f(1) == ["()"]
    from math import comb

    for n in range(1, 9):
        got = f(n)
        assert len(got) == comb(2 * n, n) // (n + 1) and len(set(got)) == len(got)
        for s_ in got:
            depth = 0
            for ch in s_:
                depth += 1 if ch == "(" else -1
                assert depth >= 0
            assert depth == 0 and len(s_) == 2 * n


def word_search_check(ns):
    f = ns["Solution"]().exist
    b = [list("ABCE"), list("SFCS"), list("ADEE")]
    assert f([r_[:] for r_ in b], "ABCCED") is True and f([r_[:] for r_ in b], "SEE") is True and f([r_[:] for r_ in b], "ABCB") is False and f([["a"]], "a") is True and f([["a"]], "b") is False
    r = rng()

    def brute(board, word):
        rows, cols = len(board), len(board[0])

        def go(i, j, k, seen):
            if k == len(word):
                return True
            if not (0 <= i < rows and 0 <= j < cols) or (i, j) in seen or board[i][j] != word[k]:
                return False
            seen = seen | {(i, j)}
            return any(go(i + a, j + c, k + 1, seen) for a, c in ((1, 0), (-1, 0), (0, 1), (0, -1)))

        return any(go(i, j, 0, frozenset()) for i in range(rows) for j in range(cols))

    for _ in range(400):
        rows, cols = r.randint(1, 4), r.randint(1, 4)
        board = [[r.choice("ab") for _ in range(cols)] for _ in range(rows)]
        word = "".join(r.choice("ab") for _ in range(r.randint(1, 6)))
        before = [row[:] for row in board]
        assert f([row[:] for row in board], word) == brute(before, word), (board, word)


def palindrome_partitioning_check(ns):
    f = ns["Solution"]().partition
    assert _same_sets(f("aab"), [["a", "a", "b"], ["aa", "b"]]) and f("a") == [["a"]]
    r = rng()

    def brute(s_):
        if not s_:
            return [[]]
        out = []
        for i in range(1, len(s_) + 1):
            if s_[:i] == s_[:i][::-1]:
                out += [[s_[:i]] + rest for rest in brute(s_[i:])]
        return out

    for _ in range(200):
        s_ = "".join(r.choice("ab") for _ in range(r.randint(1, 9)))
        got = f(s_)
        assert len(got) == len(set(map(tuple, got))) and _same_sets(got, brute(s_)), s_


def letter_combinations_check(ns):
    f = ns["Solution"]().letterCombinations
    assert sorted(f("23")) == sorted(["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"]) and f("") == [] and sorted(f("2")) == ["a", "b", "c"]
    keypad = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl", "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}
    r = rng()
    for _ in range(100):
        digits = "".join(r.choice("23456789") for _ in range(r.randint(1, 4)))
        want = ["".join(c) for c in itertools.product(*(keypad[d] for d in digits))]
        got = f(digits)
        assert len(got) == len(set(got)) and sorted(got) == sorted(want), digits


def n_queens_check(ns):
    f = ns["Solution"]().solveNQueens
    assert f(1) == [["Q"]] and f(2) == [] and f(3) == [] and sorted(map(tuple, f(4))) == sorted([(".Q..", "...Q", "Q...", "..Q."), ("..Q.", "Q...", "...Q", ".Q..")])
    for n, count in ((5, 10), (6, 4), (7, 40), (8, 92)):
        boards = f(n)
        assert len(boards) == count and len(set(map(tuple, boards))) == count
        for b in boards:
            cols = [row.index("Q") for row in b]
            assert all(row.count("Q") == 1 and len(row) == n for row in b) and len(set(cols)) == n
            assert len({r_ - c for r_, c in enumerate(cols)}) == n and len({r_ + c for r_, c in enumerate(cols)}) == n


# ---- binary trees -------------------------------------------------------------------------------------------------


def _tree(values):
    """LeetCode's level-order list ([1, None, 2, 3]) as nodes."""
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    q, i = deque([root]), 1
    while q and i < len(values):
        node = q.popleft()
        for side in ("left", "right"):
            if i < len(values) and values[i] is not None:
                setattr(node, side, TreeNode(values[i]))
                q.append(getattr(node, side))
            i += 1
    return root


def _shape(t):
    """Nested (value, left, right) tuples, so two trees compare with ==."""
    return None if t is None else (t.val, _shape(t.left), _shape(t.right))


def _random_tree(r, n, lo=-20, hi=20, distinct=False):
    """A random binary tree of n nodes; splits are sometimes even, so balanced trees turn up too."""
    vals = iter(r.sample(range(lo, hi + 1), n) if distinct else [r.randint(lo, hi) for _ in range(n)])

    def make(k):
        if k == 0:
            return None
        node = TreeNode(next(vals))
        left = r.choice([(k - 1) // 2, k - 1 - (k - 1) // 2, r.randint(0, k - 1)])
        node.left = make(left)
        node.right = make(k - 1 - left)
        return node

    return make(n)


def _random_bst(r, n, lo=0, hi=60):
    root = None
    for key in r.sample(range(lo, hi + 1), n):
        if root is None:
            root = TreeNode(key)
            continue
        cur = root
        while True:
            side = "left" if key < cur.val else "right"
            if getattr(cur, side) is None:
                setattr(cur, side, TreeNode(key))
                break
            cur = getattr(cur, side)
    return root


def _preorder(t):
    return [] if t is None else [t] + _preorder(t.left) + _preorder(t.right)


def _inorder_vals(t):
    return [] if t is None else _inorder_vals(t.left) + [t.val] + _inorder_vals(t.right)


def _height(t):
    return 0 if t is None else 1 + max(_height(t.left), _height(t.right))


def _levels(t):
    out, row = [], [t] if t else []
    while row:
        out.append([x.val for x in row])
        row = [c for x in row for c in (x.left, x.right) if c]
    return out


def _tree_copy(t):
    return None if t is None else TreeNode(t.val, _tree_copy(t.left), _tree_copy(t.right))


def _tree_distances(t):
    """{(id(a), id(b)): edges between the nodes} for every pair, by BFS over the tree as a graph."""
    adj = defaultdict(list)
    for x in _preorder(t):
        for c in (x.left, x.right):
            if c:
                adj[id(x)].append(id(c))
                adj[id(c)].append(id(x))
    out = {}
    for x in _preorder(t):
        seen, q = {id(x): 0}, deque([id(x)])
        while q:
            a = q.popleft()
            for b in adj[a]:
                if b not in seen:
                    seen[b] = seen[a] + 1
                    q.append(b)
        for b, d in seen.items():
            out[(id(x), b)] = d
    return out


def invert_tree(ns):
    f = ns["Solution"]().invertTree

    def mirror(t):
        return None if t is None else (t.val, mirror(t.right), mirror(t.left))

    assert f(None) is None
    assert _shape(f(_tree([4, 2, 7, 1, 3, 6, 9]))) == _shape(_tree([4, 7, 2, 9, 6, 3, 1]))
    assert _shape(f(_tree([2, 1, 3]))) == _shape(_tree([2, 3, 1])) and _shape(f(_tree([1, 2]))) == _shape(_tree([1, None, 2]))
    r = rng()
    for _ in range(300):
        t = _random_tree(r, r.randint(0, 25))
        want = mirror(t)
        assert _shape(f(t)) == want


def max_depth(ns):
    f = ns["Solution"]().maxDepth
    assert f(None) == 0 and f(_tree([3, 9, 20, None, None, 15, 7])) == 3 and f(_tree([1, None, 2])) == 2 and f(_tree([0])) == 1
    r = rng()
    for _ in range(300):
        t = _random_tree(r, r.randint(0, 30))
        assert f(t) == _height(t)
    chain = TreeNode(0)
    for i in range(1, 300):
        chain = TreeNode(i, chain, None)
    assert f(chain) == 300


def diameter(ns):
    f = ns["Solution"]().diameterOfBinaryTree
    assert f(_tree([1, 2, 3, 4, 5])) == 3 and f(_tree([1, 2])) == 1 and f(_tree([1])) == 0
    # the longest path can avoid the root: a deep left subtree and a small right one
    assert f(_tree([1, 2, None, 3, 4, None, None, 5, None, 6])) == 4
    r = rng()
    for _ in range(300):
        t = _random_tree(r, r.randint(1, 14))
        assert f(t) == max(_tree_distances(t).values())


def balanced(ns):
    f = ns["Solution"]().isBalanced
    assert f(None) is True and f(_tree([3, 9, 20, None, None, 15, 7])) is True
    assert f(_tree([1, 2, 2, 3, 3, None, None, 4, 4])) is False and f(_tree([1])) is True
    # unbalanced only deep down: the root's two sides differ by 0 but a node below is off by 2
    assert f(_tree([1, 2, 2, 3, None, None, 3, 4, None, None, 4])) is False

    def ok(t):
        return True if t is None else abs(_height(t.left) - _height(t.right)) <= 1 and ok(t.left) and ok(t.right)

    r = rng()
    seen = set()
    for _ in range(600):
        t = _random_tree(r, r.randint(0, 16))
        want = ok(t)
        seen.add(want)
        assert f(t) is want, _shape(t)
    assert seen == {True, False}


def same_tree(ns):
    f = ns["Solution"]().isSameTree
    assert f(None, None) is True and f(_tree([1]), None) is False and f(None, _tree([1])) is False
    assert f(_tree([1, 2, 3]), _tree([1, 2, 3])) is True and f(_tree([1, 2]), _tree([1, None, 2])) is False
    assert f(_tree([1, 2, 1]), _tree([1, 1, 2])) is False
    r = rng()
    for _ in range(400):
        a = _random_tree(r, r.randint(0, 12), -3, 3)
        b = _tree_copy(a)
        kind = r.randint(0, 3)
        nodes = _preorder(b)
        if nodes and kind == 0:
            r.choice(nodes).val += 1
        elif nodes and kind == 1:
            x = r.choice(nodes)
            x.left, x.right = x.right, x.left
        elif kind == 2:
            b = _random_tree(r, r.randint(0, 12), -3, 3)
        assert f(a, b) is (_shape(a) == _shape(b))


def subtree(ns):
    f = ns["Solution"]().isSubtree
    assert f(_tree([3, 4, 5, 1, 2]), _tree([4, 1, 2])) is True
    assert f(_tree([3, 4, 5, 1, 2, None, None, None, None, 0]), _tree([4, 1, 2])) is False
    assert f(_tree([1, 1]), _tree([1])) is True and f(_tree([12]), _tree([2])) is False
    r = rng()
    seen = set()
    for _ in range(500):
        root = _random_tree(r, r.randint(1, 14), 0, 2)
        nodes = _preorder(root)
        kind = r.randint(0, 3)
        if kind == 0:
            sub = _tree_copy(r.choice(nodes))
        elif kind == 1:
            sub = _tree_copy(r.choice(nodes))
            leaf = r.choice(_preorder(sub))
            if leaf.left is None:
                leaf.left = TreeNode(r.randint(0, 2))
            else:
                leaf.val += 1
        else:
            sub = _random_tree(r, r.randint(1, 4), 0, 2)
        want = any(_shape(x) == _shape(sub) for x in nodes)
        seen.add(want)
        assert f(root, sub) is want
    assert seen == {True, False}


def lca_bst(ns):
    f = ns["Solution"]().lowestCommonAncestor
    root = _tree([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5])
    by = {x.val: x for x in _preorder(root)}
    assert f(root, by[2], by[8]) is by[6] and f(root, by[2], by[4]) is by[2] and f(root, by[3], by[5]) is by[4]
    r = rng()

    def path(t, target):
        out, cur = [], t
        while True:
            out.append(cur)
            if cur is target:
                return out
            cur = cur.left if target.val < cur.val else cur.right

    for _ in range(400):
        t = _random_bst(r, r.randint(2, 20))
        p, q = r.sample(_preorder(t), 2)
        a, b = path(t, p), path(t, q)
        want = [x for x, y in zip(a, b) if x is y][-1]
        assert f(t, p, q) is want


def level_order(ns):
    f = ns["Solution"]().levelOrder
    assert f(None) == [] and f(_tree([1])) == [[1]] and f(_tree([3, 9, 20, None, None, 15, 7])) == [[3], [9, 20], [15, 7]]
    r = rng()
    for _ in range(300):
        t = _random_tree(r, r.randint(0, 25))
        assert f(t) == _levels(t)


def right_side_view(ns):
    f = ns["Solution"]().rightSideView
    assert f(None) == [] and f(_tree([1, 2, 3, None, 5, None, 4])) == [1, 3, 4] and f(_tree([1, None, 3])) == [1, 3]
    assert f(_tree([1, 2, 3, 4])) == [1, 3, 4]
    r = rng()
    for _ in range(300):
        t = _random_tree(r, r.randint(0, 25))
        assert f(t) == [row[-1] for row in _levels(t)]


def good_nodes(ns):
    f = ns["Solution"]().goodNodes
    assert f(_tree([3, 1, 4, 3, None, 1, 5])) == 4 and f(_tree([3, 3, None, 4, 2])) == 3 and f(_tree([1])) == 1
    assert f(_tree([-1, -2, -3])) == 1
    r = rng()

    def count(t, seen):
        if t is None:
            return 0
        return (all(v <= t.val for v in seen)) + count(t.left, seen + [t.val]) + count(t.right, seen + [t.val])

    for _ in range(400):
        t = _random_tree(r, r.randint(1, 25), -6, 6)
        assert f(t) == count(t, [])


def validate_bst(ns):
    f = ns["Solution"]().isValidBST
    assert f(_tree([2, 1, 3])) is True and f(_tree([5, 1, 4, None, None, 3, 6])) is False
    assert f(_tree([5, 4, 6, None, None, 3, 7])) is False, "a node must fit every ancestor's bound, not just its parent's"
    assert f(_tree([2, 2, 2])) is False and f(_tree([1, None, 1])) is False and f(_tree([1, 1])) is False
    assert f(_tree([-2147483648])) is True and f(_tree([2147483647])) is True and f(_tree([2147483647, 2147483647])) is False
    r = rng()
    seen = set()
    for _ in range(600):
        if r.random() < 0.3:
            t = _random_tree(r, r.randint(1, 8), 0, 6)
        else:
            t = _random_bst(r, r.randint(1, 15))
            nodes = _preorder(t)
            if r.random() < 0.6:
                r.choice(nodes).val = r.randint(0, 60)
        vals = _inorder_vals(t)
        want = all(a < b for a, b in zip(vals, vals[1:]))
        seen.add(want)
        assert f(t) is want, _shape(t)
    assert seen == {True, False}


def kth_smallest(ns):
    f = ns["Solution"]().kthSmallest
    assert f(_tree([3, 1, 4, None, 2]), 1) == 1 and f(_tree([5, 3, 6, 2, 4, None, None, 1]), 3) == 3
    r = rng()
    for _ in range(400):
        n = r.randint(1, 20)
        t = _random_bst(r, n)
        k = r.randint(1, n)
        assert f(t, k) == _inorder_vals(t)[k - 1]


def build_tree(ns):
    f = ns["Solution"]().buildTree
    assert _shape(f([3, 9, 20, 15, 7], [9, 3, 15, 20, 7])) == _shape(_tree([3, 9, 20, None, None, 15, 7]))
    assert _shape(f([-1], [-1])) == (-1, None, None)
    r = rng()
    for _ in range(400):
        t = _random_tree(r, r.randint(1, 20), -30, 30, distinct=True)
        pre = [x.val for x in _preorder(t)]
        assert _shape(f(pre[:], _inorder_vals(t))) == _shape(t)


def max_path_sum(ns):
    f = ns["Solution"]().maxPathSum
    assert f(_tree([1, 2, 3])) == 6 and f(_tree([-10, 9, 20, None, None, 15, 7])) == 42
    assert f(_tree([-3])) == -3 and f(_tree([-2, -1])) == -1 and f(_tree([2, -1])) == 2
    r = rng()
    for _ in range(300):
        t = _random_tree(r, r.randint(1, 12), -15, 15)
        nodes = _preorder(t)
        adj = defaultdict(list)
        for x in nodes:
            for c in (x.left, x.right):
                if c:
                    adj[id(x)].append(c)
                    adj[id(c)].append(x)
        best = -10**9
        for s in nodes:
            stack = [(s, None, s.val)]
            while stack:
                x, parent, total = stack.pop()
                best = max(best, total)
                for y in adj[id(x)]:
                    if y is not parent:
                        stack.append((y, x, total + y.val))
        assert f(t) == best, _shape(t)


def serialize_tree(ns):
    Codec = ns["Codec"]
    assert Codec().deserialize(Codec().serialize(None)) is None
    r = rng()
    cases = [_tree([1, 2, 3, None, None, 4, 5]), _tree([1]), _tree([-1000, None, 1000]), _tree([0, 0, 0])]
    cases += [_random_tree(r, r.randint(0, 25), -1000, 1000) for _ in range(300)]
    chain = TreeNode(0)
    for i in range(1, 300):
        chain = TreeNode(i, None, chain)
    cases.append(chain)
    for t in cases:
        want = _shape(t)
        text = Codec().serialize(t)
        assert isinstance(text, str), "serialize returns a string"
        assert _shape(Codec().deserialize(text)) == want, want
    # the string alone carries the tree: a fresh Codec shares nothing with the one that serialized
    a, b = _random_tree(r, 8, 10, 99), _random_tree(r, 9, 10, 99)
    sa, sb = Codec().serialize(a), Codec().serialize(b)
    assert _shape(Codec().deserialize(sb)) == _shape(b) and _shape(Codec().deserialize(sa)) == _shape(a)


# ---- tries ----------------------------------------------------------------------------------------------------------


def trie_check(ns):
    r = rng()
    for _ in range(150):
        trie, words = ns["Trie"](), set()
        for _ in range(r.randint(1, 40)):
            w = "".join(r.choice("abc") for _ in range(r.randint(1, 5)))
            op = r.randint(0, 2)
            if op == 0:
                trie.insert(w)
                words.add(w)
            elif op == 1:
                assert trie.search(w) is (w in words), (w, words)
            else:
                assert trie.startsWith(w) is any(x.startswith(w) for x in words), (w, words)
    t = ns["Trie"]()
    t.insert("apple")
    assert t.search("apple") is True and t.search("app") is False and t.startsWith("app") is True
    t.insert("app")
    assert t.search("app") is True


def word_dictionary_check(ns):
    def matches(pattern, w):
        return len(pattern) == len(w) and all(a in (".", b) for a, b in zip(pattern, w))

    r = rng()
    for _ in range(150):
        d, words = ns["WordDictionary"](), []
        for _ in range(r.randint(1, 40)):
            if r.random() < 0.4:
                w = "".join(r.choice("abc") for _ in range(r.randint(1, 5)))
                d.addWord(w)
                words.append(w)
            else:
                q = "".join(r.choice("abc.") for _ in range(r.randint(1, 5)))
                assert d.search(q) is any(matches(q, w) for w in words), (q, words)
    d = ns["WordDictionary"]()
    for w in ("bad", "dad", "mad"):
        d.addWord(w)
    assert [d.search(x) for x in ("pad", "bad", ".ad", "b..", "b.", "...", "....")] == [False, True, True, True, False, True, False]


def word_search_ii(ns):
    f = ns["Solution"]().findWords
    board = [["o", "a", "a", "n"], ["e", "t", "a", "e"], ["i", "h", "k", "r"], ["i", "f", "l", "v"]]
    assert sorted(f(board, ["oath", "pea", "eat", "rain"])) == ["eat", "oath"]
    assert f([["a", "b"], ["c", "d"]], ["abcb"]) == []
    r = rng()

    def found(grid, word):
        rows, cols = len(grid), len(grid[0])

        def go(i, j, k, used):
            if grid[i][j] != word[k]:
                return False
            if k == len(word) - 1:
                return True
            used.add((i, j))
            ok = any(0 <= a < rows and 0 <= b < cols and (a, b) not in used and go(a, b, k + 1, used) for a, b in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)))
            used.discard((i, j))
            return ok

        return any(go(i, j, 0, set()) for i in range(rows) for j in range(cols))

    for _ in range(300):
        rows, cols = r.randint(1, 4), r.randint(1, 4)
        grid = [[r.choice("abc") for _ in range(cols)] for _ in range(rows)]
        words = {"".join(r.choice("abc") for _ in range(r.randint(1, 6))) for _ in range(r.randint(1, 10))}
        # also words that are real paths, so some are found
        for _ in range(3):
            i, j = r.randrange(rows), r.randrange(cols)
            w, seen = grid[i][j], {(i, j)}
            for _ in range(r.randint(0, 4)):
                nxt = [(a, b) for a, b in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)) if 0 <= a < rows and 0 <= b < cols and (a, b) not in seen]
                if not nxt:
                    break
                i, j = r.choice(nxt)
                seen.add((i, j))
                w += grid[i][j]
            words.add(w)
        words = sorted(words)
        got = f([row[:] for row in grid], words[:])
        assert sorted(got) == [w for w in words if found(grid, w)] and len(got) == len(set(got)), (grid, words, got)


# ---- linked lists ---------------------------------------------------------------------------------------------------


def _ll(values):
    head = None
    for v in reversed(values):
        head = ListNode(v, head)
    return head


def _ll_vals(head, limit=100000):
    out = []
    while head:
        out.append(head.val)
        head = head.next
        assert len(out) <= limit, "the list never ends (a cycle?)"
    return out


def _ll_nodes(head):
    out = []
    while head:
        out.append(head)
        head = head.next
        assert len(out) < 100000, "the list never ends (a cycle?)"
    return out


def reverse_list(ns):
    f = ns["Solution"]().reverseList
    assert f(None) is None and _ll_vals(f(_ll([1]))) == [1] and _ll_vals(f(_ll([1, 2, 3, 4, 5]))) == [5, 4, 3, 2, 1]
    r = rng()
    for _ in range(200):
        v = [r.randint(-9, 9) for _ in range(r.randint(0, 15))]
        assert _ll_vals(f(_ll(v))) == v[::-1]


def merge_two_lists(ns):
    f = ns["Solution"]().mergeTwoLists
    assert f(None, None) is None and _ll_vals(f(None, _ll([0]))) == [0] and _ll_vals(f(_ll([1, 2, 4]), _ll([1, 3, 4]))) == [1, 1, 2, 3, 4, 4]
    r = rng()
    for _ in range(300):
        a = sorted(r.randint(-6, 6) for _ in range(r.randint(0, 8)))
        b = sorted(r.randint(-6, 6) for _ in range(r.randint(0, 8)))
        assert _ll_vals(f(_ll(a), _ll(b))) == sorted(a + b)


def has_cycle(ns):
    f = ns["Solution"]().hasCycle
    assert f(None) is False
    r = rng()
    seen = set()
    for _ in range(400):
        n = r.randint(1, 12)
        nodes = [ListNode(i) for i in range(n)]
        for a, b in zip(nodes, nodes[1:]):
            a.next = b
        pos = r.randint(-1, n - 1)
        if pos >= 0:
            nodes[-1].next = nodes[pos]
        seen.add(pos >= 0)
        assert f(nodes[0]) is (pos >= 0), (n, pos)
    assert seen == {True, False}
    # a long list: the check can't recurse or copy per step
    nodes = [ListNode(0) for _ in range(20000)]
    for a, b in zip(nodes, nodes[1:]):
        a.next = b
    assert f(nodes[0]) is False
    nodes[-1].next = nodes[7]
    assert f(nodes[0]) is True


def reorder_list(ns):
    f = ns["Solution"]().reorderList
    r = rng()
    for n in list(range(1, 12)) * 20:
        v = [r.randint(0, 99) for _ in range(n)]
        head = _ll(v)
        ids = sorted(id(x) for x in _ll_nodes(head))
        assert f(head) is None
        want = []
        lo, hi = 0, n - 1
        while lo <= hi:
            want.append(v[lo])
            if lo != hi:
                want.append(v[hi])
            lo, hi = lo + 1, hi - 1
        assert _ll_vals(head, n + 1) == want, (v, _ll_vals(head, n + 1))
        assert sorted(id(x) for x in _ll_nodes(head)) == ids, "the same nodes, relinked in place"


def remove_nth(ns):
    f = ns["Solution"]().removeNthFromEnd
    assert f(_ll([1]), 1) is None and _ll_vals(f(_ll([1, 2]), 1)) == [1] and _ll_vals(f(_ll([1, 2]), 2)) == [2]
    assert _ll_vals(f(_ll([1, 2, 3, 4, 5]), 2)) == [1, 2, 3, 5]
    r = rng()
    for _ in range(300):
        v = [r.randint(0, 9) for _ in range(r.randint(1, 12))]
        n = r.randint(1, len(v))
        assert _ll_vals(f(_ll(v), n)) == v[: len(v) - n] + v[len(v) - n + 1 :]


class _RandomNode:
    """LeetCode's Node for Copy List with Random Pointer."""

    def __init__(self, x, next=None, random=None):
        self.val = int(x)
        self.next = next
        self.random = random


def copy_random_list(ns):
    ns["Node"] = _RandomNode  # LeetCode's Node for this problem differs from Clone Graph's
    f = ns["Solution"]().copyRandomList
    assert f(None) is None
    r = rng()
    for _ in range(300):
        n = r.randint(1, 10)
        nodes = [_RandomNode(r.randint(-5, 5)) for _ in range(n)]
        for a, b in zip(nodes, nodes[1:]):
            a.next = b
        pointers = [r.choice([None] + list(range(n))) for _ in range(n)]
        for node, k in zip(nodes, pointers):
            node.random = None if k is None else nodes[k]
        copy_head = f(nodes[0])
        copies = _ll_nodes(copy_head)
        assert len(copies) == n and not ({id(c) for c in copies} & {id(x) for x in nodes}), "must be new nodes"
        assert [c.val for c in copies] == [x.val for x in nodes]
        index = {id(c): i for i, c in enumerate(copies)}
        assert [None if c.random is None else index[id(c.random)] for c in copies] == pointers, "random pointers must point into the copy"
        assert [None if x.random is None else nodes.index(x.random) for x in nodes] == pointers and _ll_nodes(nodes[0]) == nodes, "the original must be unchanged"


def add_two_numbers(ns):
    f = ns["Solution"]().addTwoNumbers
    assert _ll_vals(f(_ll([2, 4, 3]), _ll([5, 6, 4]))) == [7, 0, 8] and _ll_vals(f(_ll([0]), _ll([0]))) == [0]
    assert _ll_vals(f(_ll([9, 9, 9, 9, 9, 9, 9]), _ll([9, 9, 9, 9]))) == [8, 9, 9, 9, 0, 0, 0, 1]
    r = rng()

    def number(digits):
        return int("".join(map(str, reversed(digits))))

    for _ in range(400):
        a = [r.choice([0, 9, r.randint(0, 9)]) for _ in range(r.randint(1, 14))]
        b = [r.choice([0, 9, r.randint(0, 9)]) for _ in range(r.randint(1, 14))]
        if a[-1] == 0 and len(a) > 1:
            a[-1] = r.randint(1, 9)
        if b[-1] == 0 and len(b) > 1:
            b[-1] = r.randint(1, 9)
        got = _ll_vals(f(_ll(a), _ll(b)))
        assert number(got) == number(a) + number(b) and (got[-1] != 0 or got == [0]), (a, b, got)


def find_duplicate(ns):
    f = ns["Solution"]().findDuplicate
    assert f([1, 3, 4, 2, 2]) == 2 and f([3, 1, 3, 4, 2]) == 3 and f([3, 3, 3, 3, 3]) == 3 and f([1, 1]) == 1
    r = rng()
    for _ in range(400):
        n = r.randint(1, 30)
        d = r.randint(1, n)
        copies = r.choice([2, 2, 2, r.randint(2, n + 1)]) if n > 1 else 2
        others = r.sample([x for x in range(1, n + 1) if x != d], n + 1 - copies) if n + 1 - copies > 0 else []
        nums = [d] * copies + others
        r.shuffle(nums)
        before = nums[:]
        assert f(nums) == d, before
        assert nums == before, "the array must not be modified"


def lru_cache(ns):
    LRU = ns["LRUCache"]
    c = LRU(2)
    c.put(1, 1)
    c.put(2, 2)
    assert c.get(1) == 1
    c.put(3, 3)
    assert c.get(2) == -1
    c.put(4, 4)
    assert c.get(1) == -1 and c.get(3) == 3 and c.get(4) == 4
    r = rng()
    for _ in range(200):
        cap = r.randint(1, 4)
        cache, order = LRU(cap), []  # order: oldest first; model of (key, value)
        for _ in range(r.randint(1, 60)):
            k = r.randint(0, 6)
            if r.random() < 0.5:
                v = r.randint(0, 99)
                cache.put(k, v)
                order = [(a, b) for a, b in order if a != k] + [(k, v)]
                if len(order) > cap:
                    order.pop(0)
            else:
                want = next((b for a, b in order if a == k), -1)
                assert cache.get(k) == want, (cap, k, order)
                if want != -1:
                    order = [(a, b) for a, b in order if a != k] + [(k, want)]
    # an update of an existing key refreshes it and doesn't evict anything
    c = LRU(2)
    c.put(1, 1)
    c.put(2, 2)
    c.put(1, 10)
    c.put(3, 3)
    assert c.get(2) == -1 and c.get(1) == 10 and c.get(3) == 3


def merge_k_lists(ns):
    f = ns["Solution"]().mergeKLists
    assert f([]) is None and f([None]) is None and _ll_vals(f([_ll([1, 4, 5]), _ll([1, 3, 4]), _ll([2, 6])])) == [1, 1, 2, 3, 4, 4, 5, 6]
    r = rng()
    for _ in range(300):
        lists = [sorted(r.randint(-8, 8) for _ in range(r.randint(0, 6))) for _ in range(r.randint(0, 8))]
        got = f([_ll(v) for v in lists])
        assert _ll_vals(got) == sorted(x for v in lists for x in v)


def reverse_k_group(ns):
    f = ns["Solution"]().reverseKGroup
    assert _ll_vals(f(_ll([1, 2, 3, 4, 5]), 2)) == [2, 1, 4, 3, 5] and _ll_vals(f(_ll([1, 2, 3, 4, 5]), 3)) == [3, 2, 1, 4, 5]
    assert _ll_vals(f(_ll([1]), 1)) == [1]
    r = rng()
    for _ in range(300):
        v = [r.randint(0, 99) for _ in range(r.randint(1, 16))]
        k = r.randint(1, len(v))
        want = []
        for i in range(0, len(v), k):
            chunk = v[i : i + k]
            want += chunk[::-1] if len(chunk) == k else chunk
        assert _ll_vals(f(_ll(v), k)) == want, (v, k)


# ---- heaps ----------------------------------------------------------------------------------------------------------


def kth_largest_stream(ns):
    r = rng()
    c = ns["KthLargest"](3, [4, 5, 8, 2])
    assert [c.add(x) for x in (3, 5, 10, 9, 4)] == [4, 5, 5, 8, 8]
    for _ in range(200):
        k = r.randint(1, 5)
        nums = [r.randint(-10, 10) for _ in range(r.randint(max(0, k - 1), k + 4))]
        c, seen = ns["KthLargest"](k, nums[:]), nums[:]
        for _ in range(r.randint(1, 20)):
            x = r.randint(-10, 10)
            seen.append(x)
            assert c.add(x) == sorted(seen)[-k], (k, nums, seen)


def last_stone_weight(ns):
    f = ns["Solution"]().lastStoneWeight
    assert f([2, 7, 4, 1, 8, 1]) == 1 and f([1]) == 1 and f([2, 2]) == 0 and f([3, 3, 3]) == 3
    r = rng()
    for _ in range(300):
        stones = [r.randint(1, 30) for _ in range(r.randint(1, 10))]
        left = sorted(stones)
        while len(left) > 1:
            y, x = left.pop(), left.pop()
            if y != x:
                left.append(y - x)
                left.sort()
        assert f(stones[:]) == (left[0] if left else 0), stones


def k_closest(ns):
    f = ns["Solution"]().kClosest
    assert f([[1, 3], [-2, 2]], 1) == [[-2, 2]] and sorted(f([[3, 3], [5, -1], [-2, 4]], 2)) == [[-2, 4], [3, 3]]
    r = rng()
    for _ in range(300):
        pts = [[r.randint(-9, 9), r.randint(-9, 9)] for _ in range(r.randint(1, 12))]
        k = r.randint(1, len(pts))
        got = f([p[:] for p in pts], k)
        dist = lambda p: p[0] * p[0] + p[1] * p[1]  # noqa: E731
        assert len(got) == k and sorted(map(dist, got)) == sorted(map(dist, pts))[:k], (pts, k, got)
        pool = Counter(map(tuple, pts))
        for p in got:
            pool[tuple(p)] -= 1
            assert pool[tuple(p)] >= 0, "returned a point that isn't in the input"


def find_kth_largest(ns):
    f = ns["Solution"]().findKthLargest
    assert f([3, 2, 1, 5, 6, 4], 2) == 5 and f([3, 2, 3, 1, 2, 4, 5, 5, 6], 4) == 4 and f([1], 1) == 1
    r = rng()
    for _ in range(400):
        nums = [r.randint(-8, 8) for _ in range(r.randint(1, 15))]
        k = r.randint(1, len(nums))
        assert f(nums[:], k) == sorted(nums)[-k], (nums, k)


def least_interval(ns):
    f = ns["Solution"]().leastInterval
    assert f(["A", "A", "A", "B", "B", "B"], 2) == 8 and f(["A", "A", "A", "B", "B", "B"], 0) == 6
    assert f(["A", "A", "A", "A", "A", "A", "B", "C", "D", "E", "F", "G"], 2) == 16

    def best(counts, n):
        """Fewest time units, by breadth-first search over (counts left, cooldown left per task type)."""
        start = (tuple(counts), (0,) * len(counts))
        frontier, seen, t = {start}, {start}, 0
        while True:
            t += 1
            nxt = set()
            for left, cool in frontier:
                after = tuple(max(0, c - 1) for c in cool)
                options = [(left, after)]
                for i, c in enumerate(left):
                    if c and cool[i] == 0:
                        new_left = left[:i] + (c - 1,) + left[i + 1 :]
                        new_cool = after[:i] + (n,) + after[i + 1 :]
                        if not any(new_left):
                            return t
                        options.append((new_left, new_cool))
                for o in options:
                    if o not in seen:
                        seen.add(o)
                        nxt.add(o)
            frontier = nxt

    r = rng()
    for _ in range(150):
        counts = [r.randint(1, 3) for _ in range(r.randint(1, 3))]
        n = r.randint(0, 3)
        tasks = [chr(65 + i) for i, c in enumerate(counts) for _ in range(c)]
        r.shuffle(tasks)
        assert f(tasks, n) == best(counts, n), (tasks, n)
    # the closed form (checked against the search above on small inputs) for a big case
    big = ["A"] * 5000 + ["B"] * 5000 + ["C"] * 1000
    assert f(big, 100) == max(len(big), (5000 - 1) * 101 + 2)


def design_twitter(ns):
    T = ns["Twitter"]
    t = T()
    t.postTweet(1, 5)
    assert t.getNewsFeed(1) == [5]
    t.follow(1, 2)
    t.postTweet(2, 6)
    assert t.getNewsFeed(1) == [6, 5]
    t.unfollow(1, 2)
    assert t.getNewsFeed(1) == [5]
    r = rng()
    for _ in range(100):
        t, tweets, follows, next_id = T(), [], {u: set() for u in range(1, 5)}, 100
        for _ in range(r.randint(5, 70)):
            op = r.randint(0, 3)
            u, v = r.sample(range(1, 5), 2)
            if op == 0:
                t.postTweet(u, next_id)
                tweets.append((u, next_id))
                next_id += 1
            elif op == 1:
                t.follow(u, v)
                follows[u].add(v)
            elif op == 2:
                t.unfollow(u, v)
                follows[u].discard(v)
            else:
                want = [tid for owner, tid in reversed(tweets) if owner == u or owner in follows[u]][:10]
                assert t.getNewsFeed(u) == want, (u, want)


def median_finder(ns):
    r = rng()
    m = ns["MedianFinder"]()
    m.addNum(1)
    m.addNum(2)
    assert m.findMedian() == 1.5
    m.addNum(3)
    assert m.findMedian() == 2.0
    for _ in range(200):
        m, seen = ns["MedianFinder"](), []
        for _ in range(r.randint(1, 30)):
            x = r.randint(-20, 20)
            m.addNum(x)
            seen.append(x)
            ordered = sorted(seen)
            mid = len(ordered) // 2
            want = ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2
            assert m.findMedian() == want, (seen, want)


# ---- math and geometry ----------------------------------------------------------------------------------------------


def rotate_image(ns):
    f = ns["Solution"]().rotate
    r = rng()
    for n in list(range(1, 8)) * 15:
        m = [[r.randint(-9, 9) for _ in range(n)] for _ in range(n)]
        want = [list(row) for row in zip(*m[::-1])]
        assert f(m) is None
        assert m == want, (n, want)


def spiral_matrix(ns):
    f = ns["Solution"]().spiralOrder
    assert f([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == [1, 2, 3, 6, 9, 8, 7, 4, 5]
    assert f([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]) == [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7] and f([[1]]) == [1] and f([[1, 2, 3]]) == [1, 2, 3] and f([[1], [2], [3]]) == [1, 2, 3]
    r = rng()
    for _ in range(300):
        rows, cols = r.randint(1, 7), r.randint(1, 7)
        m = [[i * cols + j for j in range(cols)] for i in range(rows)]
        i = j = d = 0
        seen, want = set(), []
        for _ in range(rows * cols):
            want.append(m[i][j])
            seen.add((i, j))
            di, dj = ((0, 1), (1, 0), (0, -1), (-1, 0))[d]
            if not (0 <= i + di < rows and 0 <= j + dj < cols) or (i + di, j + dj) in seen:
                d = (d + 1) % 4
                di, dj = ((0, 1), (1, 0), (0, -1), (-1, 0))[d]
            i, j = i + di, j + dj
        assert f([row[:] for row in m]) == want, (rows, cols)


def set_zeroes(ns):
    f = ns["Solution"]().setZeroes
    m = [[1, 1, 1], [1, 0, 1], [1, 1, 1]]
    assert f(m) is None and m == [[1, 0, 1], [0, 0, 0], [1, 0, 1]]
    m = [[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]]
    f(m)
    assert m == [[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]]
    r = rng()
    for _ in range(500):
        rows, cols = r.randint(1, 6), r.randint(1, 6)
        m = [[0 if r.random() < 0.15 else r.randint(-5, 5) or 1 for _ in range(cols)] for _ in range(rows)]
        zr = {i for i in range(rows) for j in range(cols) if m[i][j] == 0}
        zc = {j for i in range(rows) for j in range(cols) if m[i][j] == 0}
        want = [[0 if i in zr or j in zc else m[i][j] for j in range(cols)] for i in range(rows)]
        f(m)
        assert m == want, (want, m)


def happy_number(ns):
    f = ns["Solution"]().isHappy

    def happy(n):
        seen = set()
        while n != 1 and n not in seen:
            seen.add(n)
            n = sum(int(c) ** 2 for c in str(n))
        return n == 1

    assert f(19) is True and f(2) is False and f(1) is True
    for n in list(range(1, 400)) + [7, 100, 1111111, 2147483647, 999999999]:
        assert f(n) is happy(n), n


def plus_one(ns):
    f = ns["Solution"]().plusOne
    assert f([1, 2, 3]) == [1, 2, 4] and f([9]) == [1, 0] and f([4, 3, 2, 9]) == [4, 3, 3, 0] and f([9, 9, 9]) == [1, 0, 0, 0] and f([0]) == [1]
    r = rng()
    for _ in range(400):
        d = [r.choice([9, 9, r.randint(0, 9)]) for _ in range(r.randint(1, 12))]
        if d[0] == 0 and len(d) > 1:
            d[0] = r.randint(1, 9)
        got = f(d[:])
        assert int("".join(map(str, got))) == int("".join(map(str, d))) + 1 and (got[0] != 0 or got == [0]), d


def my_pow(ns):
    import signal

    f = ns["Solution"]().myPow

    def close(a, b):
        return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-12)

    assert close(f(2.0, 10), 1024.0) and close(f(2.1, 3), 9.261) and close(f(2.0, -2), 0.25) and f(5.0, 0) == 1.0 and f(1.0, 2**31 - 1) == 1.0
    assert f(2.0, -(2**31)) == 0.0 and f(-1.0, 2**31 - 1) == -1.0 and f(-1.0, -(2**31)) == 1.0
    r = rng()
    for _ in range(500):
        x = r.choice([r.uniform(-3, 3), float(r.randint(-3, 3)), 0.5])
        n = r.randint(-12, 12)
        if x == 0 and n < 0:
            continue
        assert close(f(x, n), x**n), (x, n)

    def too_slow(*_):
        raise AssertionError("myPow is too slow for a huge exponent (it must take O(log n) steps)")

    signal.signal(signal.SIGALRM, too_slow)
    signal.alarm(5)
    try:
        # repeated squaring doubles the rounding error at every step, so a huge exponent can't match to 1e-9 (LeetCode allows 1e-5)
        assert math.isclose(f(1.0000000001, 2**31 - 1), 1.0000000001 ** (2**31 - 1), rel_tol=1e-5)
        assert math.isclose(f(0.99999999, -(2**31) + 1), 0.99999999 ** (-(2**31) + 1), rel_tol=1e-5)
    finally:
        signal.alarm(0)


def multiply_strings(ns):
    f = ns["Solution"]().multiply
    assert f("2", "3") == "6" and f("123", "456") == "56088" and f("0", "9133") == "0" and f("9133", "0") == "0" and f("999", "999") == "998001"
    r = rng()
    for _ in range(400):
        a = "".join(r.choice("0123456789") for _ in range(r.randint(1, 30))).lstrip("0") or "0"
        b = "".join(r.choice("0123456789") for _ in range(r.randint(1, 30))).lstrip("0") or "0"
        assert f(a, b) == str(int(a) * int(b)), (a, b)


def detect_squares(ns):
    r = rng()
    d = ns["DetectSquares"]()
    for p in ([3, 10], [11, 2], [3, 2]):
        d.add(p)
    assert d.count([11, 10]) == 1 and d.count([14, 8]) == 0
    d.add([11, 2])
    assert d.count([11, 10]) == 2
    for _ in range(150):
        d, points = ns["DetectSquares"](), Counter()
        for _ in range(r.randint(5, 50)):
            p = (r.randint(0, 4), r.randint(0, 4))
            if r.random() < 0.55:
                d.add(list(p))
                points[p] += 1
            else:
                x, y = p
                want = sum(
                    points[(a, b)] * points[(x, b)] * points[(a, y)]
                    for (a, b) in list(points)
                    if abs(a - x) == abs(b - y) and a != x
                )
                assert d.count(list(p)) == want, (p, dict(points))


# ---- bit manipulation -----------------------------------------------------------------------------------------------


def single_number(ns):
    f = ns["Solution"]().singleNumber
    assert f([2, 2, 1]) == 1 and f([4, 1, 2, 1, 2]) == 4 and f([1]) == 1
    r = rng()
    for _ in range(300):
        vals = r.sample(range(-50, 50), r.randint(1, 8))
        nums = vals + vals[1:]
        r.shuffle(nums)
        before = nums[:]
        assert f(nums) == vals[0], before


def hamming_weight(ns):
    f = ns["Solution"]().hammingWeight
    assert f(11) == 3 and f(128) == 1 and f(2147483645) == 30 and f(0) == 0 and f(2**31 - 1) == 31
    r = rng()
    for _ in range(300):
        n = r.randint(0, 2**31 - 1)
        assert f(n) == bin(n).count("1")


def count_bits(ns):
    f = ns["Solution"]().countBits
    assert f(2) == [0, 1, 1] and f(5) == [0, 1, 1, 2, 1, 2] and f(0) == [0]
    for n in list(range(0, 70)) + [1000, 4096, 10**5]:
        assert f(n) == [bin(i).count("1") for i in range(n + 1)], n


def reverse_bits(ns):
    f = ns["Solution"]().reverseBits
    assert f(43261596) == 964176192 and f(2147483644) == 1073741822 and f(0) == 0 and f(1) == 2**31 and f(2**32 - 1) == 2**32 - 1
    r = rng()
    for _ in range(300):
        n = r.randint(0, 2**32 - 1)
        assert f(n) == int(f"{n:032b}"[::-1], 2), n


def missing_number(ns):
    f = ns["Solution"]().missingNumber
    assert f([3, 0, 1]) == 2 and f([0, 1]) == 2 and f([9, 6, 4, 2, 3, 5, 7, 0, 1]) == 8 and f([0]) == 1 and f([1]) == 0
    r = rng()
    for _ in range(300):
        n = r.randint(1, 30)
        nums = list(range(n + 1))
        gone = nums.pop(r.randrange(n + 1))
        r.shuffle(nums)
        assert f(nums) == gone


def get_sum(ns):
    f = ns["Solution"]().getSum
    assert f(1, 2) == 3 and f(2, 3) == 5 and f(-1, 1) == 0 and f(-2, -3) == -5 and f(0, 0) == 0 and f(-1000, 1000) == 0
    r = rng()
    for _ in range(600):
        a, b = r.randint(-1000, 1000), r.randint(-1000, 1000)
        assert f(a, b) == a + b, (a, b)
    assert f(-(2**31), 2**31 - 1) == -1 and f(2**30, 2**30 - 1) == 2**31 - 1


def reverse_integer(ns):
    f = ns["Solution"]().reverse
    assert f(123) == 321 and f(-123) == -321 and f(120) == 21 and f(0) == 0 and f(1534236469) == 0 and f(-2147483648) == 0
    assert f(1463847412) == 2147483641 and f(-1463847412) == -2147483641 and f(2147483647) == 0
    r = rng()
    for _ in range(500):
        x = r.choice([r.randint(-(2**31), 2**31 - 1), r.randint(-10**6, 10**6)])
        sign = -1 if x < 0 else 1
        want = sign * int(str(abs(x))[::-1])
        want = want if -(2**31) <= want <= 2**31 - 1 else 0
        assert f(x) == want, x


# ---- the 250's must-learn problems ------------------------------------------------------------------------------------


def _time_limit(seconds, what):
    """Context manager: raises AssertionError if the block runs longer than `seconds` (Unix; checks run in the main thread)."""
    import contextlib
    import signal

    @contextlib.contextmanager
    def limit():
        def too_slow(*_):
            raise AssertionError(f"{what}: too slow")

        old = signal.signal(signal.SIGALRM, too_slow)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old)

    return limit()


def concatenation_of_array(ns):
    f = ns["Solution"]().getConcatenation
    assert f([1, 2, 1]) == [1, 2, 1, 1, 2, 1] and f([1, 3, 2, 1]) == [1, 3, 2, 1, 1, 3, 2, 1] and f([5]) == [5, 5]
    r = rng()
    for _ in range(100):
        a = [r.randint(1, 1000) for _ in range(r.randint(1, 30))]
        before = a[:]
        assert f(a) == before + before


def remove_element(ns):
    f = ns["Solution"]().removeElement
    nums = [3, 2, 2, 3]
    k = f(nums, 3)
    assert k == 2 and sorted(nums[:k]) == [2, 2]
    r = rng()
    for _ in range(400):
        nums = [r.randint(0, 5) for _ in range(r.randint(0, 20))]
        val = r.randint(0, 5)
        keep = sorted(x for x in nums if x != val)
        k = f(nums, val)
        assert k == len(keep) and sorted(nums[:k]) == keep, (nums, val)


def majority_element(ns):
    f = ns["Solution"]().majorityElement
    assert f([3, 2, 3]) == 3 and f([2, 2, 1, 1, 1, 2, 2]) == 2 and f([1]) == 1
    r = rng()
    for _ in range(400):
        n = r.randint(1, 25)
        major = r.randint(-5, 5)
        nums = [major] * (n // 2 + 1) + [r.randint(-5, 5) for _ in range(n - n // 2 - 1)]
        r.shuffle(nums)
        assert f(nums) == major, nums


def design_hashset(ns):
    S = ns["MyHashSet"]
    s = S()
    s.add(1)
    s.add(2)
    assert s.contains(1) is True and s.contains(3) is False
    s.add(2)
    assert s.contains(2) is True
    s.remove(2)
    assert s.contains(2) is False
    s.remove(77)  # removing something absent is fine
    r = rng()
    for _ in range(100):
        s, model = S(), set()
        keys = [r.randint(0, 10**6) for _ in range(6)] + [0, 10**6, 1000, 1001]
        for _ in range(r.randint(1, 60)):
            k, op = r.choice(keys), r.randint(0, 2)
            if op == 0:
                s.add(k)
                model.add(k)
            elif op == 1:
                s.remove(k)
                model.discard(k)
            else:
                assert s.contains(k) is (k in model), (k, model)


def sort_an_array(ns):
    f = ns["Solution"]().sortArray
    assert f([5, 2, 3, 1]) == [1, 2, 3, 5] and f([5, 1, 1, 2, 0, 0]) == [0, 0, 1, 1, 2, 5] and f([1]) == [1]
    r = rng()
    for _ in range(300):
        a = [r.randint(-50, 50) for _ in range(r.randint(1, 30))]
        assert f(a[:]) == sorted(a)
    with _time_limit(10, "sortArray on 50000 numbers and on adversarial orders"):
        for a in (
            [r.randint(-50000, 50000) for _ in range(50000)],
            list(range(2000)),
            list(range(2000, 0, -1)),
            [7] * 2000,
            [r.randint(0, 3) for _ in range(20000)],
        ):
            assert f(a[:]) == sorted(a)


def best_time_ii(ns):
    f = ns["Solution"]().maxProfit
    assert f([7, 1, 5, 3, 6, 4]) == 7 and f([1, 2, 3, 4, 5]) == 4 and f([7, 6, 4, 3, 1]) == 0 and f([5]) == 0
    r = rng()

    def best(prices, i, holding):
        if i == len(prices):
            return 0
        skip = best(prices, i + 1, holding)
        act = prices[i] + best(prices, i + 1, False) if holding else -prices[i] + best(prices, i + 1, True)
        return max(skip, act)

    for _ in range(300):
        prices = [r.randint(0, 9) for _ in range(r.randint(1, 10))]
        assert f(prices) == best(prices, 0, False), prices


def subarray_sum_k(ns):
    f = ns["Solution"]().subarraySum
    assert f([1, 1, 1], 2) == 2 and f([1, 2, 3], 3) == 2 and f([1], 0) == 0 and f([0, 0, 0], 0) == 6
    assert f([1, -1, 0], 0) == 3, "negative numbers and zeros need a prefix-sum map, not a sliding window"
    r = rng()
    for _ in range(500):
        nums = [r.randint(-3, 3) for _ in range(r.randint(1, 30))]
        k = r.randint(-5, 5)
        want = sum(sum(nums[i : j + 1]) == k for i in range(len(nums)) for j in range(i, len(nums)))
        assert f(nums, k) == want, (nums, k)
    with _time_limit(5, "subarraySum on 20000 zeros"):
        assert f([0] * 20000, 0) == 20000 * 20001 // 2


def first_missing_positive(ns):
    f = ns["Solution"]().firstMissingPositive
    assert f([1, 2, 0]) == 3 and f([3, 4, -1, 1]) == 2 and f([7, 8, 9, 11, 12]) == 1 and f([1]) == 2 and f([2147483647]) == 1
    r = rng()
    for _ in range(600):
        nums = [r.randint(-4, 14) for _ in range(r.randint(1, 14))]
        have = set(nums)
        want = next(i for i in range(1, 100) if i not in have)
        assert f(nums[:]) == want, nums


def makesquare(ns):
    f = ns["Solution"]().makesquare
    assert f([1, 1, 2, 2, 2]) is True and f([3, 3, 3, 3, 4]) is False and f([5, 5, 5, 5, 4, 4, 4, 4, 3, 3, 3, 3]) is True

    def exact(sticks):
        total = sum(sticks)
        if total % 4 or max(sticks) > total // 4:
            return False
        side, n = total // 4, len(sticks)
        reach = [False] * (1 << n)
        reach[0] = True
        used = [0] * (1 << n)
        for mask in range(1 << n):
            if not reach[mask]:
                continue
            for i in range(n):
                if not mask >> i & 1 and used[mask] % side + sticks[i] <= side:
                    nxt = mask | 1 << i
                    reach[nxt] = True
                    used[nxt] = used[mask] + sticks[i]
        return reach[-1]

    r = rng()
    seen = set()
    for _ in range(300):
        n = r.randint(4, 11)
        if r.random() < 0.5:
            side = r.randint(2, 9)
            sticks = []
            for _ in range(4):
                left = side
                while left:
                    x = r.randint(1, left)
                    sticks.append(x)
                    left -= x
            sticks = sticks[:12]
        else:
            sticks = [r.randint(1, 8) for _ in range(n)]
        r.shuffle(sticks)
        want = exact(sticks)
        seen.add(want)
        assert f(sticks[:]) is want, sticks
    assert seen == {True, False}
    with _time_limit(5, "makesquare on a hard negative case"):
        assert f([1] * 14 + [2]) is False and f([3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]) is False


def word_break_ii(ns):
    f = ns["Solution"]().wordBreak
    assert sorted(f("catsanddog", ["cat", "cats", "and", "sand", "dog"])) == ["cat sand dog", "cats and dog"]
    assert sorted(f("pineapplepenapple", ["apple", "pen", "applepen", "pine", "pineapple"])) == ["pine apple pen apple", "pine applepen apple", "pineapple pen apple"]
    assert f("catsandog", ["cats", "dog", "sand", "and", "cat"]) == []
    r = rng()

    def every(s, words):
        if not s:
            return [[]]
        return [[w] + rest for w in words if s.startswith(w) for rest in every(s[len(w) :], words)]

    for _ in range(300):
        words = sorted({"".join(r.choice("ab") for _ in range(r.randint(1, 3))) for _ in range(r.randint(1, 5))})
        s = "".join(r.choice("ab") for _ in range(r.randint(1, 9)))
        want = sorted(" ".join(x) for x in every(s, words))
        assert sorted(f(s, words[:])) == want, (s, words)
    with _time_limit(5, "wordBreak on a string that has no segmentation"):
        assert f("a" * 40 + "b", ["a", "aa", "aaa", "aaaa"]) == []
        assert len(f("a" * 14, ["a", "aa", "aaa"])) == 1705


def search_insert(ns):
    f = ns["Solution"]().searchInsert
    assert f([1, 3, 5, 6], 5) == 2 and f([1, 3, 5, 6], 2) == 1 and f([1, 3, 5, 6], 7) == 4 and f([1, 3, 5, 6], 0) == 0 and f([1], 1) == 0
    import bisect

    r = rng()
    for _ in range(400):
        nums = sorted(r.sample(range(-30, 30), r.randint(1, 15)))
        t = r.randint(-32, 32)
        assert f(nums, t) == bisect.bisect_left(nums, t)
    class_ = type("Seq", (), {"__len__": lambda self: 10**18, "__getitem__": lambda self, i: i})
    with _time_limit(5, "searchInsert over a huge range"):
        assert f(class_(), 12345678901234) == 12345678901234


class _Mountain:
    """LeetCode's MountainArray: only get() and length() are allowed, and get() may be called at most 100 times."""

    def __init__(self, values):
        self.values = values
        self.calls = 0

    def get(self, index):
        self.calls += 1
        assert self.calls <= 100, "more than 100 calls to MountainArray.get"
        return self.values[index]

    def length(self):
        return len(self.values)


def find_in_mountain_array(ns):
    f = ns["Solution"]().findInMountainArray
    assert f(3, _Mountain([1, 2, 3, 4, 5, 3, 1])) == 2 and f(3, _Mountain([0, 1, 2, 4, 2, 1])) == -1
    r = rng()

    def make(n):
        peak = r.randint(1, n - 2)
        up = sorted(r.sample(range(0, 10**9), peak))
        top = up[-1] + r.randint(1, 100)
        down = sorted(r.sample(range(0, top), n - peak - 1), reverse=True)
        return up + [top] + down

    for _ in range(300):
        arr = make(r.randint(3, 40))
        for t in {r.choice(arr), r.randint(0, arr[0] + 5), arr[-1], arr[0]}:
            want = next((i for i, v in enumerate(arr) if v == t), -1)
            assert f(t, _Mountain(arr)) == want, (arr, t)
    big = make(10000)
    for t in (big[0], big[-1], max(big), big[5000], big[9000], -1, big[3] + 1):
        want = next((i for i, v in enumerate(big) if v == t), -1)
        assert f(t, _Mountain(big)) == want, t


def alien_sorted(ns):
    f = ns["Solution"]().isAlienSorted
    assert f(["hello", "leetcode"], "hlabcdefgijkmnopqrstuvwxyz") is True and f(["word", "world", "row"], "worldabcefghijkmnpqstuvxyz") is False
    assert f(["apple", "app"], "abcdefghijklmnopqrstuvwxyz") is False and f(["app", "apple"], "abcdefghijklmnopqrstuvwxyz") is True
    r = rng()
    seen = set()
    for _ in range(500):
        order = list("abcdefghijklmnopqrstuvwxyz")
        r.shuffle(order)
        rank = {c: i for i, c in enumerate(order)}
        words = ["".join(r.choice(order[:3]) for _ in range(r.randint(1, 4))) for _ in range(r.randint(1, 5))]
        if r.random() < 0.5:
            words.sort(key=lambda w: [rank[c] for c in w])
        want = all([rank[c] for c in a] <= [rank[c] for c in b] for a, b in zip(words, words[1:]))
        seen.add(want)
        assert f(words, "".join(order)) is want, (words, order)
    assert seen == {True, False}


def find_judge(ns):
    f = ns["Solution"]().findJudge
    assert f(2, [[1, 2]]) == 2 and f(3, [[1, 3], [2, 3]]) == 3 and f(3, [[1, 3], [2, 3], [3, 1]]) == -1 and f(1, []) == 1 and f(3, [[1, 2], [2, 3]]) == -1
    r = rng()
    for _ in range(500):
        n = r.randint(1, 6)
        pairs = {(a, b) for a in range(1, n + 1) for b in range(1, n + 1) if a != b}
        if r.random() < 0.6:
            judge = r.randint(1, n)
            trust = [(a, judge) for a in range(1, n + 1) if a != judge and r.random() < 0.95]
            trust += [(a, b) for (a, b) in pairs if a != judge and b != judge and r.random() < 0.2]
        else:
            trust = [pr for pr in pairs if r.random() < 0.3]
        trust = sorted(set(trust))
        r.shuffle(trust)
        judges = [j for j in range(1, n + 1) if all(a != j for a, _ in trust) and sum(b == j for _, b in trust) == n - 1]
        want = judges[0] if judges else -1
        assert f(n, [list(t) for t in trust]) == want, (n, trust)


def eval_division(ns):
    f = ns["Solution"]().calcEquation
    assert [round(x, 4) for x in f([["a", "b"], ["b", "c"]], [2.0, 3.0], [["a", "c"], ["b", "a"], ["a", "e"], ["a", "a"], ["x", "x"]])] == [6.0, 0.5, -1.0, 1.0, -1.0]
    assert f([["a", "b"]], [0.5], [["a", "b"], ["b", "a"], ["a", "c"], ["x", "y"]]) == [0.5, 2.0, -1.0, -1.0]
    r = rng()
    for _ in range(300):
        names = [f"v{i}" for i in range(r.randint(2, 8))]
        group = {v: r.randint(0, 2) for v in names}
        value = {v: r.choice([0.5, 1.0, 2.0, 3.0, 4.0, 0.25, 8.0]) for v in names}
        eqs, vals = [], []
        for _ in range(r.randint(1, 8)):
            a, b = r.sample(names, 2)
            if group[a] == group[b]:
                eqs.append([a, b])
                vals.append(value[a] / value[b])
        if not eqs:
            continue
        known = {x for e in eqs for x in e}
        # components are decided by the equations themselves
        parent = {v: v for v in known}

        def find(x):
            while parent[x] != x:
                x = parent[x]
            return x

        # values are consistent only within a group, so link equations into components
        for a, b in eqs:
            parent[find(a)] = find(b)
        queries, want = [], []
        for _ in range(8):
            a, b = r.choice(names + ["zz"]), r.choice(names + ["zz"])
            queries.append([a, b])
            if a in known and b in known and find(a) == find(b):
                want.append(value[a] / value[b])
            else:
                want.append(-1.0)
        got = f([e[:] for e in eqs], vals[:], [q[:] for q in queries])
        assert len(got) == len(want) and all(math.isclose(g, w, rel_tol=1e-6) for g, w in zip(got, want)), (eqs, vals, queries, got, want)


def dota2_senate(ns):
    f = ns["Solution"]().predictPartyVictory
    assert f("RD") == "Radiant" and f("RDD") == "Dire" and f("R") == "Radiant" and f("DDRRR") == "Dire"
    r = rng()
    for _ in range(500):
        senate = "".join(r.choice("RD") for _ in range(r.randint(1, 14)))
        line = list(senate)
        i = 0
        while len(set(line)) > 1:
            # senator i bans the next opposing senator in voting order
            n = len(line)
            me = line[i]
            j = next(k for k in (((i + d) % n) for d in range(1, n)) if line[k] != me)
            if j < i:
                i -= 1
            line.pop(j)
            i = (i + 1) % len(line)
        assert f(senate) == ("Radiant" if line[0] == "R" else "Dire"), senate


def single_threaded_cpu(ns):
    f = ns["Solution"]().getOrder
    assert f([[1, 2], [2, 4], [3, 2], [4, 1]]) == [0, 2, 3, 1] and f([[7, 10], [7, 12], [7, 5], [7, 4], [7, 2]]) == [4, 3, 2, 0, 1]
    r = rng()
    for _ in range(300):
        tasks = [[r.randint(1, 15), r.randint(1, 6)] for _ in range(r.randint(1, 10))]
        left, t, want = set(range(len(tasks))), 0, []
        while left:
            ready = [i for i in left if tasks[i][0] <= t]
            if not ready:
                t = min(tasks[i][0] for i in left)
                continue
            i = min(ready, key=lambda k: (tasks[k][1], k))
            left.discard(i)
            want.append(i)
            t += tasks[i][1]
        assert f([x[:] for x in tasks]) == want, tasks


def ipo(ns):
    f = ns["Solution"]().findMaximizedCapital
    assert f(2, 0, [1, 2, 3], [0, 1, 1]) == 4 and f(3, 0, [1, 2, 3], [0, 1, 2]) == 6 and f(1, 0, [1], [5]) == 0
    r = rng()
    for _ in range(400):
        n = r.randint(1, 10)
        profits = [r.randint(0, 9) for _ in range(n)]
        capital = [r.randint(0, 12) for _ in range(n)]
        k, w = r.randint(1, 6), r.randint(0, 6)
        money, left = w, set(range(n))
        for _ in range(k):
            ok = [i for i in left if capital[i] <= money]
            if not ok:
                break
            i = max(ok, key=lambda x: profits[x])
            money += profits[i]
            left.discard(i)
        assert f(k, w, profits[:], capital[:]) == money, (k, w, profits, capital)


def design_circular_queue(ns):
    Q = ns["MyCircularQueue"]
    q = Q(3)
    assert [q.enQueue(1), q.enQueue(2), q.enQueue(3), q.enQueue(4)] == [True, True, True, False]
    assert q.Rear() == 3 and q.isFull() is True and q.deQueue() is True and q.enQueue(4) is True and q.Rear() == 4 and q.Front() == 2
    r = rng()
    for _ in range(150):
        k = r.randint(1, 5)
        q, model = Q(k), []
        for _ in range(r.randint(1, 60)):
            op = r.randint(0, 5)
            if op == 0:
                v = r.randint(0, 99)
                ok = len(model) < k
                assert q.enQueue(v) is ok
                if ok:
                    model.append(v)
            elif op == 1:
                assert q.deQueue() is bool(model)
                if model:
                    model.pop(0)
            elif op == 2:
                assert q.Front() == (model[0] if model else -1)
            elif op == 3:
                assert q.Rear() == (model[-1] if model else -1)
            elif op == 4:
                assert q.isEmpty() is (not model)
            else:
                assert q.isFull() is (len(model) == k)


def excel_title(ns):
    f = ns["Solution"]().convertToTitle
    assert f(1) == "A" and f(26) == "Z" and f(27) == "AA" and f(28) == "AB" and f(52) == "AZ" and f(701) == "ZY" and f(703) == "AAA" and f(2147483647) == "FXSHRXW"

    def number(title):
        n = 0
        for c in title:
            n = n * 26 + ord(c) - 64
        return n

    for n in list(range(1, 2000)) + [18278, 18279, 456976, 2**31 - 1]:
        got = f(n)
        assert got.isalpha() and got.isupper() and number(got) == n, (n, got)


def gcd_of_strings(ns):
    f = ns["Solution"]().gcdOfStrings
    assert f("ABCABC", "ABC") == "ABC" and f("ABABAB", "ABAB") == "AB" and f("LEET", "CODE") == "" and f("AAAAAB", "AAA") == ""
    r = rng()
    for _ in range(500):
        if r.random() < 0.6:
            base = "".join(r.choice("AB") for _ in range(r.randint(1, 3)))
            a, b = base * r.randint(1, 6), base * r.randint(1, 6)
        else:
            a, b = ("".join(r.choice("AB") for _ in range(r.randint(1, 8))) for _ in range(2))
        want = ""
        for length in range(min(len(a), len(b)), 0, -1):
            cand = a[:length]
            if len(a) % length == 0 and len(b) % length == 0 and cand * (len(a) // length) == a and cand * (len(b) // length) == b:
                want = cand
                break
        assert f(a, b) == want, (a, b)


def transpose_matrix(ns):
    f = ns["Solution"]().transpose
    assert f([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == [[1, 4, 7], [2, 5, 8], [3, 6, 9]] and f([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]] and f([[1]]) == [[1]]
    r = rng()
    for _ in range(200):
        rows, cols = r.randint(1, 6), r.randint(1, 6)
        m = [[r.randint(-9, 9) for _ in range(cols)] for _ in range(rows)]
        assert f([row[:] for row in m]) == [[m[i][j] for i in range(rows)] for j in range(cols)]


def find_k_closest(ns):
    f = ns["Solution"]().findClosestElements
    assert f([1, 2, 3, 4, 5], 4, 3) == [1, 2, 3, 4] and f([1, 1, 2, 3, 4, 5], 4, -1) == [1, 1, 2, 3] and f([1, 3], 1, 2) == [1]
    r = rng()
    for _ in range(600):
        arr = sorted(r.randint(-15, 15) for _ in range(r.randint(1, 15)))
        k, x = r.randint(1, len(arr)), r.randint(-20, 20)
        want = sorted(sorted(arr, key=lambda v: (abs(v - x), v))[:k])
        assert f(arr[:], k, x) == want, (arr, k, x)
    big = list(range(0, 2 * 10**5, 2))
    with _time_limit(5, "findClosestElements on 100000 numbers"):
        for _ in range(2000):
            k, x = r.randint(1, 50), r.randint(-10, 2 * 10**5 + 10)
            got = f(big, k, x)
            assert len(got) == k and got == sorted(got)


def baseball_game(ns):
    f = ns["Solution"]().calPoints
    assert f(["5", "2", "C", "D", "+"]) == 30 and f(["5", "-2", "4", "C", "D", "9", "+", "+"]) == 27 and f(["1", "C"]) == 0
    r = rng()
    for _ in range(300):
        ops, scores = [], []
        for _ in range(r.randint(1, 20)):
            options = ["n"] + (["C", "D"] if scores else []) + (["+"] if len(scores) > 1 else [])
            o = r.choice(options)
            if o == "n":
                v = r.randint(-30, 30)
                ops.append(str(v))
                scores.append(v)
            elif o == "C":
                ops.append("C")
                scores.pop()
            elif o == "D":
                ops.append("D")
                scores.append(2 * scores[-1])
            else:
                ops.append("+")
                scores.append(scores[-1] + scores[-2])
        assert f(ops[:]) == sum(scores), ops


def stack_using_queues(ns):
    S = ns["MyStack"]
    s = S()
    s.push(1)
    s.push(2)
    assert s.top() == 2 and s.pop() == 2 and s.empty() is False and s.pop() == 1 and s.empty() is True
    r = rng()
    for _ in range(150):
        s, model = S(), []
        for _ in range(r.randint(1, 60)):
            op = r.randint(0, 3)
            if op == 0 or not model:
                v = r.randint(0, 99)
                s.push(v)
                model.append(v)
            elif op == 1:
                assert s.pop() == model.pop()
            elif op == 2:
                assert s.top() == model[-1]
            else:
                assert s.empty() is False
        assert s.empty() is (not model)


def decode_string(ns):
    f = ns["Solution"]().decodeString
    assert f("3[a]2[bc]") == "aaabcbc" and f("3[a2[c]]") == "accaccacc" and f("2[abc]3[cd]ef") == "abcabccdcdcdef" and f("abc") == "abc" and f("10[a]") == "a" * 10
    r = rng()

    def gen(depth):
        text, out = "", ""
        for _ in range(r.randint(1, 3)):
            if depth < 3 and r.random() < 0.5:
                k = r.choice([1, 2, 3, 10, 12])
                inner_text, inner_out = gen(depth + 1)
                text += f"{k}[{inner_text}]"
                out += inner_out * k
            else:
                letters = "".join(r.choice("abcxyz") for _ in range(r.randint(1, 3)))
                text += letters
                out += letters
        return text, out

    for _ in range(300):
        text, out = gen(0)
        assert f(text) == out, text


def insert_into_bst(ns):
    f = ns["Solution"]().insertIntoBST
    assert _shape(f(None, 5)) == (5, None, None)
    r = rng()
    for _ in range(400):
        keys = r.sample(range(0, 60), r.randint(0, 15) + 1)
        val, keys = keys[0], keys[1:]
        root = None
        for key in keys:
            node, parent = root, None
            while node:
                parent, node = node, node.left if key < node.val else node.right
            new = TreeNode(key)
            if parent is None:
                root = new
            elif key < parent.val:
                parent.left = new
            else:
                parent.right = new
        got = f(root, val)
        assert _inorder_vals(got) == sorted(keys + [val]), (keys, val)
        assert len(_preorder(got)) == len(keys) + 1


def remove_leaf_nodes(ns):
    f = ns["Solution"]().removeLeafNodes
    assert _shape(f(_tree([1, 2, 3, 2, None, 2, 4]), 2)) == _shape(_tree([1, None, 3, None, 4]))
    assert _shape(f(_tree([1, 3, 3, 3, 2]), 3)) == _shape(_tree([1, 3, None, None, 2])) and f(_tree([1, 2, None, 2, None, 2]), 2) is not None
    assert f(_tree([2, 2, 2]), 2) is None and _shape(f(_tree([1, 1, 1]), 1)) is None
    r = rng()

    def prune(t, target):
        if t is None:
            return None
        left, right = prune(t.left, target), prune(t.right, target)
        if left is None and right is None and t.val == target:
            return None
        return (t.val, left, right)

    for _ in range(400):
        t = _random_tree(r, r.randint(1, 15), 1, 3)
        target = r.randint(1, 3)
        want = prune(t, target)
        assert _shape(f(t, target)) == want, (_shape(t), target)


def merge_alternately(ns):
    f = ns["Solution"]().mergeAlternately
    assert f("abc", "pqr") == "apbqcr" and f("ab", "pqrs") == "apbqrs" and f("abcd", "pq") == "apbqcd" and f("a", "b") == "ab"
    import itertools

    r = rng()
    for _ in range(200):
        a, b = ("".join(r.choice("abcxyz") for _ in range(r.randint(1, 8))) for _ in range(2))
        assert f(a, b) == "".join(x + y for x, y in itertools.zip_longest(a, b, fillvalue=""))


def boats(ns):
    f = ns["Solution"]().numRescueBoats
    assert f([1, 2], 3) == 1 and f([3, 2, 2, 1], 3) == 3 and f([3, 5, 3, 4], 5) == 4

    def exact(people, limit):
        n = len(people)
        best = [0] + [10**9] * ((1 << n) - 1)
        for mask in range(1, 1 << n):
            i = (mask & -mask).bit_length() - 1
            rest = mask & ~(1 << i)
            best[mask] = best[rest] + 1
            for j in range(i + 1, n):
                if rest >> j & 1 and people[i] + people[j] <= limit:
                    best[mask] = min(best[mask], best[rest & ~(1 << j)] + 1)
        return best[-1]

    r = rng()
    for _ in range(300):
        limit = r.randint(3, 10)
        people = [r.randint(1, limit) for _ in range(r.randint(1, 9))]
        assert f(people[:], limit) == exact(people, limit), (people, limit)


def stone_game_iii(ns):
    f = ns["Solution"]().stoneGameIII
    assert f([1, 2, 3, 7]) == "Bob" and f([1, 2, 3, -9]) == "Alice" and f([1, 2, 3, 6]) == "Tie" and f([-1, -2, -3]) == "Tie"

    def play(values, i, a, b, alice):
        if i == len(values):
            return a - b
        results = []
        total = 0
        for k in range(1, 4):
            if i + k > len(values):
                break
            total += values[i + k - 1]
            results.append(play(values, i + k, a + total if alice else a, b if alice else b + total, not alice))
        return max(results) if alice else min(results)

    r = rng()
    seen = set()
    for _ in range(150):
        values = [r.randint(-6, 6) for _ in range(r.randint(1, 9))]
        diff = play(values, 0, 0, 0, True)
        want = "Alice" if diff > 0 else "Bob" if diff < 0 else "Tie"
        seen.add(want)
        assert f(values[:]) == want, values
    assert seen == {"Alice", "Bob", "Tie"}


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
    "binary-search": binary_search,
    "search-a-2d-matrix": search_matrix,
    "koko-eating-bananas": koko,
    "find-minimum-in-rotated-sorted-array": find_min_rotated,
    "search-in-rotated-sorted-array": search_rotated,
    "time-based-key-value-store": time_map,
    "median-of-two-sorted-arrays": median_two_sorted,
    "subsets": subsets_check,
    "combination-sum": combination_sum_check,
    "combination-sum-ii": combination_sum_ii_check,
    "permutations": permutations_check,
    "subsets-ii": subsets_ii_check,
    "generate-parentheses": generate_parentheses_check,
    "word-search": word_search_check,
    "palindrome-partitioning": palindrome_partitioning_check,
    "letter-combinations-of-a-phone-number": letter_combinations_check,
    "n-queens": n_queens_check,
    "invert-binary-tree": invert_tree,
    "maximum-depth-of-binary-tree": max_depth,
    "diameter-of-binary-tree": diameter,
    "balanced-binary-tree": balanced,
    "same-tree": same_tree,
    "subtree-of-another-tree": subtree,
    "lowest-common-ancestor-of-a-binary-search-tree": lca_bst,
    "binary-tree-level-order-traversal": level_order,
    "binary-tree-right-side-view": right_side_view,
    "count-good-nodes-in-binary-tree": good_nodes,
    "validate-binary-search-tree": validate_bst,
    "kth-smallest-element-in-a-bst": kth_smallest,
    "construct-binary-tree-from-preorder-and-inorder-traversal": build_tree,
    "binary-tree-maximum-path-sum": max_path_sum,
    "serialize-and-deserialize-binary-tree": serialize_tree,
    "implement-trie-prefix-tree": trie_check,
    "design-add-and-search-words-data-structure": word_dictionary_check,
    "word-search-ii": word_search_ii,
    "reverse-linked-list": reverse_list,
    "merge-two-sorted-lists": merge_two_lists,
    "linked-list-cycle": has_cycle,
    "reorder-list": reorder_list,
    "remove-nth-node-from-end-of-list": remove_nth,
    "copy-list-with-random-pointer": copy_random_list,
    "add-two-numbers": add_two_numbers,
    "find-the-duplicate-number": find_duplicate,
    "lru-cache": lru_cache,
    "merge-k-sorted-lists": merge_k_lists,
    "reverse-nodes-in-k-group": reverse_k_group,
    "kth-largest-element-in-a-stream": kth_largest_stream,
    "last-stone-weight": last_stone_weight,
    "k-closest-points-to-origin": k_closest,
    "kth-largest-element-in-an-array": find_kth_largest,
    "task-scheduler": least_interval,
    "design-twitter": design_twitter,
    "find-median-from-data-stream": median_finder,
    "rotate-image": rotate_image,
    "spiral-matrix": spiral_matrix,
    "set-matrix-zeroes": set_zeroes,
    "happy-number": happy_number,
    "plus-one": plus_one,
    "powx-n": my_pow,
    "multiply-strings": multiply_strings,
    "detect-squares": detect_squares,
    "single-number": single_number,
    "number-of-1-bits": hamming_weight,
    "counting-bits": count_bits,
    "reverse-bits": reverse_bits,
    "missing-number": missing_number,
    "sum-of-two-integers": get_sum,
    "reverse-integer": reverse_integer,
    "concatenation-of-array": concatenation_of_array,
    "remove-element": remove_element,
    "majority-element": majority_element,
    "design-hashset": design_hashset,
    "sort-an-array": sort_an_array,
    "best-time-to-buy-and-sell-stock-ii": best_time_ii,
    "subarray-sum-equals-k": subarray_sum_k,
    "first-missing-positive": first_missing_positive,
    "matchsticks-to-square": makesquare,
    "word-break-ii": word_break_ii,
    "search-insert-position": search_insert,
    "find-in-mountain-array": find_in_mountain_array,
    "verifying-an-alien-dictionary": alien_sorted,
    "find-the-town-judge": find_judge,
    "evaluate-division": eval_division,
    "dota2-senate": dota2_senate,
    "single-threaded-cpu": single_threaded_cpu,
    "ipo": ipo,
    "design-circular-queue": design_circular_queue,
    "excel-sheet-column-title": excel_title,
    "greatest-common-divisor-of-strings": gcd_of_strings,
    "transpose-matrix": transpose_matrix,
    "find-k-closest-elements": find_k_closest,
    "baseball-game": baseball_game,
    "implement-stack-using-queues": stack_using_queues,
    "decode-string": decode_string,
    "insert-into-a-binary-search-tree": insert_into_bst,
    "delete-leaves-with-a-given-value": remove_leaf_nodes,
    "merge-strings-alternately": merge_alternately,
    "boats-to-save-people": boats,
    "stone-game-iii": stone_game_iii,
}


def run(slug, ns):
    if slug not in CHECKS:
        raise AssertionError(f"no checks for {slug} in page_tests.py")
    CHECKS[slug](ns)
