"""Behaviour tests for the templates in content/dsa/lessons. TESTS maps a technique id to a function(ns) that exercises
the names the template defines (ns is the namespace the template was run in). Not every template has one: the ones with a
clear contract do, and check_lessons.py reports the count."""
import random
from collections import deque

TESTS = {}

from page_tests import ListNode, TreeNode, _ll, _ll_vals, _shape, _tree  # noqa: E402,F401


def test(technique):
    def register(fn):
        TESTS[technique] = fn
        return fn

    return register


def _grid(r, rows, cols, values):
    return [[r.choice(values) for _ in range(cols)] for _ in range(rows)]


@test("Graphs:simulation")
def _(ns):
    f = ns["is_sorted_by"]
    alpha = "hlabcdefgijkmnopqrstuvwxyz"
    assert f(alpha, ["hello", "leetcode"]) is True and f("worldabcefghijkmnpqstuvxyz", ["word", "world", "row"]) is False
    assert f("abcdefghijklmnopqrstuvwxyz", ["apple", "app"]) is False and f("abcdefghijklmnopqrstuvwxyz", ["app", "apple"]) is True


@test("Graphs:degree")
def _(ns):
    f = ns["find_judge"]
    assert f(2, [[1, 2]]) == 2 and f(3, [[1, 3], [2, 3], [3, 1]]) == -1 and f(1, []) == 1 and f(3, [[1, 3], [2, 3]]) == 3


@test("Graphs:flood")
def _(ns):
    f = ns["count_islands"]
    r = random.Random(3)
    for _ in range(200):
        g = _grid(r, r.randint(1, 6), r.randint(1, 6), ["0", "1"])
        want, seen = 0, set()
        for i in range(len(g)):
            for j in range(len(g[0])):
                if g[i][j] == "1" and (i, j) not in seen:
                    want += 1
                    stack = [(i, j)]
                    seen.add((i, j))
                    while stack:
                        a, b = stack.pop()
                        for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            x, y = a + da, b + db
                            if 0 <= x < len(g) and 0 <= y < len(g[0]) and g[x][y] == "1" and (x, y) not in seen:
                                seen.add((x, y))
                                stack.append((x, y))
        assert f([row[:] for row in g]) == want
    assert f([["1"] * 400 for _ in range(400)]) == 1, "a big grid must not hit the recursion limit"


@test("Graphs:clone")
def _(ns):
    Node = ns["Node"]
    a, b, c = Node(1), Node(2), Node(3)
    a.neighbors, b.neighbors, c.neighbors = [b, c], [a, c], [a, b]
    copy = ns["clone_graph"](a)
    assert copy is not a and copy.val == 1 and [n.val for n in copy.neighbors] == [2, 3]
    assert copy.neighbors[0].neighbors[0] is copy and copy.neighbors[0] is not b and ns["clone_graph"](None) is None


@test("Graphs:multi-bfs")
def _(ns):
    f = ns["spread"]
    d = f([[0] * 4 for _ in range(3)], [(0, 0), (2, 3)])
    assert d[0][0] == 0 and d[2][3] == 0 and d[1][1] == 2 and d[0][3] == 2 and d[2][0] == 2 and d[1][2] == 2


@test("Graphs:border")
def _(ns):
    f = ns["reach_from"]
    h = [[1, 2, 2, 3, 5], [3, 2, 3, 4, 4], [2, 4, 5, 3, 1], [6, 7, 1, 4, 5], [5, 1, 1, 2, 4]]
    pacific = f([(0, c) for c in range(5)] + [(r, 0) for r in range(1, 5)], h)
    atlantic = f([(4, c) for c in range(5)] + [(r, 4) for r in range(4)], h)
    assert sorted(pacific & atlantic) == sorted([(0, 4), (1, 3), (1, 4), (2, 2), (3, 0), (3, 1), (4, 0)])


@test("Graphs:tree-walk")
def _(ns):
    f = ns["min_flips_to_reach_zero"]
    assert f(6, [[0, 1], [1, 3], [2, 3], [4, 0], [4, 5]]) == 3 and f(5, [[1, 0], [1, 2], [3, 2], [3, 4]]) == 2 and f(3, [[1, 0], [2, 0]]) == 0


@test("Graphs:topo")
def _(ns):
    f = ns["topo_order"]
    r = random.Random(4)
    for _ in range(300):
        n = r.randint(1, 7)
        edges = list({(r.randrange(n), r.randrange(n)) for _ in range(r.randint(0, 8))})
        order = f(n, [list(e) for e in edges])
        # brute force: is there any order that respects every edge?
        import itertools

        exists = any(all(p.index(a) < p.index(b) for a, b in edges) for p in itertools.permutations(range(n)))
        if exists:
            assert sorted(order) == list(range(n)) and all(order.index(a) < order.index(b) for a, b in edges), (n, edges)
        else:
            assert order == [], (n, edges)


@test("Graphs:dsu")
def _(ns):
    DSU = ns["DSU"]
    r = random.Random(5)
    for _ in range(200):
        n = r.randint(1, 10)
        d = DSU(n)
        comp = list(range(n))
        for _ in range(r.randint(0, 12)):
            a, b = r.randrange(n), r.randrange(n)
            joined = d.union(a, b)
            assert joined == (comp[a] != comp[b])
            old, new = comp[a], comp[b]
            comp = [new if x == old else x for x in comp]
        assert d.groups == len(set(comp))
        assert all((d.find(a) == d.find(b)) == (comp[a] == comp[b]) for a in range(n) for b in range(n))


@test("Graphs:bipartite")
def _(ns):
    f = ns["is_bipartite"]
    import itertools

    r = random.Random(6)
    for _ in range(300):
        n = r.randint(1, 7)
        edges = {(min(a, b), max(a, b)) for a, b in ((r.randrange(n), r.randrange(n)) for _ in range(r.randint(0, 9))) if a != b}
        g = [[] for _ in range(n)]
        for a, b in edges:
            g[a].append(b)
            g[b].append(a)
        want = any(all(c[a] != c[b] for a, b in edges) for c in itertools.product([0, 1], repeat=n))
        assert f(g) is want, (n, edges)


@test("Graphs:weighted")
def _(ns):
    f = ns["solve_queries"]
    got = f([["a", "b"], ["b", "c"]], [2.0, 3.0], [["a", "c"], ["b", "a"], ["a", "e"], ["a", "a"], ["x", "x"]])
    assert [round(x, 4) for x in got] == [6.0, 0.5, -1.0, 1.0, -1.0]


@test("Graphs:bfs-implicit")
def _(ns):
    f = ns["ladder_length"]
    assert f("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]) == 5 and f("hit", "cog", ["hot", "dot", "dog", "lot", "log"]) == 0


# ---- 1-D dynamic programming ----------------------------------------------------------------------------------------

@test("1-D Dynamic Programming:recurrence")
def _(ns):
    f = ns["count_ways"]
    assert [f(n) for n in (1, 2, 3, 5)] == [1, 2, 3, 8] and f(4, (1, 2, 3)) == 7 and f(0) == 1


@test("1-D Dynamic Programming:take-skip")
def _(ns):
    f = ns["rob"]
    r = random.Random(1)
    assert f([1, 2, 3, 1]) == 4 and f([2, 7, 9, 3, 1]) == 12 and f([]) == 0
    for _ in range(200):
        a = [r.randint(0, 9) for _ in range(r.randint(0, 9))]
        want = max((sum(a[i] for i in range(len(a)) if m >> i & 1) for m in range(1 << len(a)) if not m & (m >> 1)), default=0)
        assert f(a) == want


@test("1-D Dynamic Programming:expand")
def _(ns):
    f = ns["longest_palindrome"]
    assert f("babad") in ("bab", "aba") and f("cbbd") == "bb" and f("a") == "a"
    r = random.Random(2)
    for _ in range(200):
        s = "".join(r.choice("ab") for _ in range(r.randint(1, 12)))
        got = f(s)
        assert got == got[::-1] and got in s
        assert len(got) == max(len(s[i:j]) for i in range(len(s)) for j in range(i + 1, len(s) + 1) if s[i:j] == s[i:j][::-1])


@test("1-D Dynamic Programming:unbounded")
def _(ns):
    f = ns["coin_change"]
    assert f([1, 2, 5], 11) == 3 and f([2], 3) == -1 and f([1], 0) == 0 and f([1, 3, 4], 6) == 2
    r = random.Random(3)
    for _ in range(200):
        coins = r.sample(range(1, 8), r.randint(1, 3))
        amount = r.randint(0, 20)
        level, seen, steps = {0}, {0}, 0
        while level and amount not in level:
            level = {x + c for x in level for c in coins if x + c <= amount} - seen
            seen |= level
            steps += 1
        assert f(coins, amount) == (steps if amount in level else -1)


@test("1-D Dynamic Programming:min-max-run")
def _(ns):
    f = ns["max_product"]
    assert f([2, 3, -2, 4]) == 6 and f([-2, 0, -1]) == 0 and f([-2, 3, -4]) == 24
    r = random.Random(4)
    for _ in range(300):
        a = [r.randint(-3, 3) for _ in range(r.randint(1, 8))]
        want = max(eval("*".join(map(str, [x if x >= 0 else f"({x})" for x in a[i:j]]))) for i in range(len(a)) for j in range(i + 1, len(a) + 1))
        assert f(a) == want


@test("1-D Dynamic Programming:prefix-dp")
def _(ns):
    f = ns["word_break"]
    assert f("leetcode", ["leet", "code"]) is True and f("catsandog", ["cats", "dog", "sand", "and", "cat"]) is False
    r = random.Random(5)

    def brute(s, words):
        return s == "" or any(s.startswith(w) and brute(s[len(w):], words) for w in words)

    for _ in range(300):
        words = ["".join(r.choice("ab") for _ in range(r.randint(1, 3))) for _ in range(r.randint(1, 4))]
        s = "".join(r.choice("ab") for _ in range(r.randint(1, 9)))
        assert f(s, words) is brute(s, words)


@test("1-D Dynamic Programming:lis")
def _(ns):
    f = ns["length_of_lis"]
    assert f([10, 9, 2, 5, 3, 7, 101, 18]) == 4 and f([0, 1, 0, 3, 2, 3]) == 4 and f([7, 7, 7]) == 1 and f([]) == 0
    r = random.Random(6)
    for _ in range(300):
        a = [r.randint(0, 9) for _ in range(r.randint(1, 12))]
        dp = [1] * len(a)
        for i in range(len(a)):
            for j in range(i):
                if a[j] < a[i]:
                    dp[i] = max(dp[i], dp[j] + 1)
        assert f(a) == max(dp)


@test("1-D Dynamic Programming:subset")
def _(ns):
    f = ns["can_make"]
    r = random.Random(7)
    for _ in range(300):
        a = [r.randint(1, 9) for _ in range(r.randint(0, 8))]
        t = r.randint(0, 30)
        want = any(sum(a[i] for i in range(len(a)) if m >> i & 1) == t for m in range(1 << len(a)))
        assert f(a, t) is want
    assert f([2], 4) is False, "an item can be used only once"


@test("1-D Dynamic Programming:partition-dp")
def _(ns):
    f = ns["min_total_height"]
    assert f([[1, 1], [2, 3], [2, 3], [1, 1], [1, 1], [1, 1], [1, 2]], 4) == 6
    r = random.Random(8)

    def brute(books, width):
        if not books:
            return 0
        best, w, h = float("inf"), 0, 0
        for k, (t, ht) in enumerate(books):
            w += t
            if w > width:
                break
            h = max(h, ht)
            best = min(best, h + brute(books[k + 1:], width))
        return best

    for _ in range(200):
        books = [[r.randint(1, 3), r.randint(1, 5)] for _ in range(r.randint(1, 7))]
        assert f(books, 4) == brute(books, 4)


@test("1-D Dynamic Programming:count-states")
def _(ns):
    f = ns["knight_dialer"]
    assert [f(n) for n in (1, 2, 3, 4)] == [10, 20, 46, 104] and f(3131) == 136006598


@test("1-D Dynamic Programming:game")
def _(ns):
    f = ns["stone_game"]
    assert f([1, 2, 3, 7]) < 0 and f([1, 2, 3, -9]) > 0 and f([1, 2, 3, 6]) == 0
    r = random.Random(9)

    def play(v, i, alice):
        if i == len(v):
            return 0
        opts = [sum(v[i:i + k]) * (1 if alice else -1) + play(v, i + k, not alice) for k in (1, 2, 3) if i + k <= len(v)]
        return max(opts) if alice else min(opts)

    for _ in range(150):
        v = [r.randint(-6, 6) for _ in range(r.randint(1, 8))]
        assert f(v) == play(v, 0, True)


@test("1-D Dynamic Programming:bitmask")
def _(ns):
    f = ns["max_palindrome_product"]
    assert f("leetcodecom") == 9 and f("bb") == 1 and f("accbcaxxcxx") == 25
    import itertools

    r = random.Random(10)
    for _ in range(40):
        s = "".join(r.choice("ab") for _ in range(r.randint(2, 7)))
        best = 0
        for assign in itertools.product((0, 1, 2), repeat=len(s)):
            a = [c for c, g in zip(s, assign) if g == 1]
            b = [c for c, g in zip(s, assign) if g == 2]
            if a == a[::-1] and b == b[::-1]:
                best = max(best, len(a) * len(b))
        assert f(s) == best


# ---- 2-D dynamic programming ----------------------------------------------------------------------------------------

@test("2-D Dynamic Programming:grid-dp")
def _(ns):
    f = ns["min_path_sum"]
    assert f([[1, 3, 1], [1, 5, 1], [4, 2, 1]]) == 7 and f([[1, 2, 3], [4, 5, 6]]) == 12 and f([[5]]) == 5
    r = random.Random(11)

    def brute(g, i=0, j=0):
        if i == len(g) - 1 and j == len(g[0]) - 1:
            return g[i][j]
        opts = [brute(g, i + 1, j)] if i + 1 < len(g) else []
        opts += [brute(g, i, j + 1)] if j + 1 < len(g[0]) else []
        return g[i][j] + min(opts)

    for _ in range(100):
        g = [[r.randint(0, 9) for _ in range(r.randint(1, 5))]] * 1
        g = [[r.randint(0, 9) for _ in range(len(g[0]))] for _ in range(r.randint(1, 5))]
        assert f(g) == brute(g)


@test("2-D Dynamic Programming:two-string")
def _(ns):
    f = ns["lcs_length"]
    assert f("abcde", "ace") == 3 and f("abc", "def") == 0 and f("", "x") == 0
    r = random.Random(12)

    def brute(a, b):
        if not a or not b:
            return 0
        return 1 + brute(a[1:], b[1:]) if a[0] == b[0] else max(brute(a[1:], b), brute(a, b[1:]))

    for _ in range(150):
        a = "".join(r.choice("abc") for _ in range(r.randint(0, 7)))
        b = "".join(r.choice("abc") for _ in range(r.randint(0, 7)))
        assert f(a, b) == brute(a, b)


@test("2-D Dynamic Programming:pair-dp")
def _(ns):
    f = ns["longest_fib_subseq"]
    assert f([1, 2, 3, 4, 5, 6, 7, 8]) == 5 and f([1, 3, 7, 11, 12, 14, 18]) == 3 and f([1, 3, 5]) == 0
    r = random.Random(13)
    for _ in range(150):
        arr = sorted(r.sample(range(1, 30), r.randint(3, 9)))
        best = 0
        for i in range(len(arr)):
            for j in range(i + 1, len(arr)):
                a, b, n = arr[i], arr[j], 2
                while a + b in arr:
                    a, b, n = b, a + b, n + 1
                best = max(best, n if n >= 3 else 0)
        assert f(arr) == best


@test("2-D Dynamic Programming:state-machine")
def _(ns):
    f = ns["max_profit_with_cooldown"]
    assert f([1, 2, 3, 0, 2]) == 3 and f([1]) == 0 and f([]) == 0
    r = random.Random(14)

    def brute(p, i, holding, cooldown):
        if i >= len(p):
            return 0
        best = brute(p, i + 1, holding, False)
        if holding:
            best = max(best, p[i] + brute(p, i + 2, False, False))  # sell, then rest a day
        elif not cooldown:
            best = max(best, -p[i] + brute(p, i + 1, True, False))
        return best

    for _ in range(200):
        p = [r.randint(1, 9) for _ in range(r.randint(0, 9))]
        assert f(p) == brute(p, 0, False, False)


@test("2-D Dynamic Programming:dfs-memo")
def _(ns):
    f = ns["longest_increasing_path"]
    assert f([[9, 9, 4], [6, 6, 8], [2, 1, 1]]) == 4 and f([[3, 4, 5], [3, 2, 6], [2, 2, 1]]) == 4 and f([[1]]) == 1
    r = random.Random(15)

    def brute(m, i, j):
        best = 1
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            x, y = i + di, j + dj
            if 0 <= x < len(m) and 0 <= y < len(m[0]) and m[x][y] > m[i][j]:
                best = max(best, 1 + brute(m, x, y))
        return best

    for _ in range(100):
        m = [[r.randint(0, 5) for _ in range(r.randint(1, 4))] for _ in range(1)]
        m = [[r.randint(0, 5) for _ in range(len(m[0]))] for _ in range(r.randint(1, 4))]
        assert f(m) == max(brute(m, i, j) for i in range(len(m)) for j in range(len(m[0])))


@test("2-D Dynamic Programming:interval")
def _(ns):
    f = ns["max_coins"]
    assert f([3, 1, 5, 8]) == 167 and f([1, 5]) == 10 and f([7]) == 7
    import itertools

    r = random.Random(16)
    for _ in range(40):
        a = [r.randint(1, 6) for _ in range(r.randint(1, 6))]
        best = 0
        for order in itertools.permutations(range(len(a))):
            alive, total = list(range(len(a))), 0
            for k in order:
                p = alive.index(k)
                left = a[alive[p - 1]] if p else 1
                right = a[alive[p + 1]] if p + 1 < len(alive) else 1
                total += left * a[k] * right
                alive.pop(p)
            best = max(best, total)
        assert f(a[:]) == best


# ---- greedy -----------------------------------------------------------------------------------------------------------

@test("Greedy:scan-balance")
def _(ns):
    f = ns["max_profit_unlimited"]
    r = random.Random(20)
    assert f([7, 1, 5, 3, 6, 4]) == 7 and f([1, 2, 3, 4, 5]) == 4 and f([5]) == 0

    def dp(p):
        hold, free = float("-inf"), 0
        for x in p:
            hold, free = max(hold, free - x), max(free, hold + x)
        return free

    for _ in range(200):
        p = [r.randint(0, 9) for _ in range(r.randint(1, 10))]
        assert f(p) == dp(p)


@test("Greedy:sort-pick")
def _(ns):
    f = ns["max_items"]
    r = random.Random(21)
    for _ in range(200):
        c = [r.randint(1, 9) for _ in range(r.randint(0, 8))]
        b = r.randint(0, 25)
        want = max((bin(m).count("1") for m in range(1 << len(c)) if sum(c[i] for i in range(len(c)) if m >> i & 1) <= b), default=0)
        assert f(c, b) == want


@test("Greedy:swap-greedy")
def _(ns):
    f = ns["max_odd_binary"]
    import itertools

    assert f("010") == "001" and f("0101") == "1001"
    r = random.Random(22)
    for _ in range(100):
        s = "".join(r.choice("01") for _ in range(r.randint(1, 7)))
        if "1" not in s:
            continue
        want = max(("".join(p) for p in itertools.permutations(s) if p[-1] == "1"), key=lambda x: int(x, 2))
        assert f(s) == want


@test("Greedy:count-greedy")
def _(ns):
    f = ns["one_swap_makes_equal"]
    r = random.Random(23)
    for _ in range(300):
        a = "".join(r.choice("abc") for _ in range(r.randint(2, 6)))
        b = "".join(r.choice("abc") for _ in range(len(a)))
        if r.random() < 0.5:
            l = list(a)
            i, j = r.sample(range(len(a)), 2)
            l[i], l[j] = l[j], l[i]
            b = "".join(l)
        want = a == b or any(a[:i] + a[j] + a[i + 1:j] + a[i] + a[j + 1:] == b for i in range(len(a)) for j in range(i + 1, len(a)))
        assert f(a, b) is want, (a, b)


@test("Greedy:flip-window")
def _(ns):
    f = ns["min_k_flips"]
    assert f([0, 1, 0], 1) == 2 and f([1, 1, 0], 2) == -1 and f([0, 0, 0, 1, 0, 1, 1, 0], 3) == 3
    r = random.Random(24)
    for _ in range(200):
        n = r.randint(1, 9)
        k = r.randint(1, 4)
        bits = [r.randint(0, 1) for _ in range(n)]
        target = tuple([1] * n)
        level, seen, steps = {tuple(bits)}, {tuple(bits)}, 0
        while level and target not in level:
            nxt = set()
            for st in level:
                for s in range(n - k + 1):
                    new = st[:s] + tuple(1 - x for x in st[s:s + k]) + st[s + k:]
                    if new not in seen:
                        seen.add(new)
                        nxt.add(new)
            level, steps = nxt, steps + 1
        assert f(bits, k) == (steps if target in level else -1), (bits, k)


@test("Greedy:kadane")
def _(ns):
    f = ns["max_subarray"]
    assert f([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6 and f([-3, -1, -2]) == -1 and f([5]) == 5
    r = random.Random(25)
    for _ in range(200):
        a = [r.randint(-5, 5) for _ in range(r.randint(1, 10))]
        assert f(a) == max(sum(a[i:j]) for i in range(len(a)) for j in range(i + 1, len(a) + 1))


@test("Greedy:reach")
def _(ns):
    f = ns["can_reach_end"]
    assert f([2, 3, 1, 1, 4]) is True and f([3, 2, 1, 0, 4]) is False and f([0]) is True
    r = random.Random(26)
    for _ in range(300):
        a = [r.randint(0, 4) for _ in range(r.randint(1, 8))]
        ok = [False] * len(a)
        ok[-1] = True
        for i in range(len(a) - 2, -1, -1):
            ok[i] = any(ok[j] for j in range(i + 1, min(len(a), i + a[i] + 1)))
        assert f(a) is ok[0]


@test("Greedy:surplus")
def _(ns):
    f = ns["can_complete_circuit"]
    assert f([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]) == 3 and f([2, 3, 4], [3, 4, 3]) == -1
    r = random.Random(27)
    for _ in range(300):
        n = r.randint(1, 7)
        g = [r.randint(0, 5) for _ in range(n)]
        c = [r.randint(0, 5) for _ in range(n)]
        starts = [s for s in range(n) if all(sum(g[(s + k) % n] - c[(s + k) % n] for k in range(m + 1)) >= 0 for m in range(n))]
        got = f(g, c)
        assert (got in starts) if starts else got == -1, (g, c, got, starts)


@test("Greedy:group-smallest")
def _(ns):
    f = ns["can_split_consecutive"]
    assert f([1, 2, 3, 6, 2, 3, 4, 7, 8], 3) is True and f([1, 2, 3, 4, 5], 4) is False
    r = random.Random(28)

    def brute(cards, size):
        if not cards:
            return True
        lo = min(cards)
        rest = list(cards)
        for v in range(lo, lo + size):
            if v not in rest:
                return False
            rest.remove(v)
        return brute(rest, size)

    for _ in range(300):
        size = r.randint(1, 3)
        h = [r.randint(1, 6) for _ in range(r.choice([size * 2, size * 3, size * 2 + 1]))]
        assert f(h, size) is brute(h, size) if len(h) % size == 0 else f(h, size) is False


@test("Greedy:simulate-greedy")
def _(ns):
    f = ns["winner"]
    assert f("RD") == "Radiant" and f("RDD") == "Dire"
    r = random.Random(29)
    for _ in range(300):
        senate = "".join(r.choice("RD") for _ in range(r.randint(1, 12)))
        line, i = list(senate), 0
        while len(set(line)) > 1:
            n = len(line)
            j = next(k for k in ((i + d) % n for d in range(1, n)) if line[k] != line[i])
            if j < i:
                i -= 1
            line.pop(j)
            i = (i + 1) % len(line)
        assert f(senate) == ("Radiant" if line[0] == "R" else "Dire")


@test("Greedy:filter")
def _(ns):
    f = ns["can_merge_to_target"]
    assert f([[2, 5, 3], [1, 8, 4], [1, 7, 5]], [2, 7, 5]) is True and f([[3, 4, 5], [4, 5, 6]], [3, 2, 5]) is False
    r = random.Random(30)
    for _ in range(300):
        ts = [[r.randint(1, 4) for _ in range(3)] for _ in range(r.randint(1, 5))]
        target = [r.randint(1, 4) for _ in range(3)]
        want = any(tuple(max(ts[i][k] for i in range(len(ts)) if m >> i & 1) for k in range(3)) == tuple(target) for m in range(1, 1 << len(ts)))
        assert f(ts, target) is want


@test("Greedy:last-seen")
def _(ns):
    f = ns["partition_labels"]
    assert f("ababcbacadefegdehijhklij") == [9, 7, 8] and f("eccbbbbdec") == [10]
    r = random.Random(31)
    for _ in range(300):
        s = "".join(r.choice("abcd") for _ in range(r.randint(1, 10)))
        # Merge every letter's [first, last] span: each merged span is one part.
        spans = sorted((s.index(c), s.rindex(c)) for c in set(s))
        merged = []
        for a, b in spans:
            if merged and a <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], b)
            else:
                merged.append([a, b])
        assert f(s) == [b - a + 1 for a, b in merged], s


@test("Greedy:paren-range")
def _(ns):
    f = ns["check_valid_string"]
    assert f("()") is True and f("(*)") is True and f("(*))") is True and f("(((*)") is False and f("") is True
    r = random.Random(32)

    def brute(s, open_=0):
        if open_ < 0:
            return False
        if not s:
            return open_ == 0
        c = s[0]
        if c == "(":
            return brute(s[1:], open_ + 1)
        if c == ")":
            return brute(s[1:], open_ - 1)
        return any(brute(s[1:], open_ + d) for d in (1, -1, 0))

    for _ in range(300):
        s = "".join(r.choice("()*") for _ in range(r.randint(0, 9)))
        assert f(s) is brute(s), s


# ---- intervals ------------------------------------------------------------------------------------------------------

@test("Intervals:merge")
def _(ns):
    f = ns["merge_intervals"]
    assert f([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]] and f([[1, 4], [4, 5]]) == [[1, 5]]
    r = random.Random(40)
    for _ in range(300):
        iv = [[a, a + r.randint(0, 5)] for a in (r.randint(0, 15) for _ in range(r.randint(1, 7)))]
        got = f([x[:] for x in iv])
        covered = {t for a, b in iv for t in range(a * 2, b * 2 + 1)}  # half-steps, so touching ends join
        assert {t for a, b in got for t in range(a * 2, b * 2 + 1)} == covered
        assert all(got[i][1] < got[i + 1][0] for i in range(len(got) - 1))


@test("Intervals:by-end")
def _(ns):
    f = ns["min_removals"]
    assert f([[1, 2], [2, 3], [3, 4], [1, 3]]) == 1 and f([[1, 2], [1, 2], [1, 2]]) == 2 and f([[1, 2], [2, 3]]) == 0
    r = random.Random(41)
    for _ in range(300):
        iv = [[a, a + r.randint(1, 4)] for a in (r.randint(0, 8) for _ in range(r.randint(1, 8)))]
        best = 0
        for m in range(1 << len(iv)):
            ch = sorted(iv[i] for i in range(len(iv)) if m >> i & 1)
            if all(ch[i][1] <= ch[i + 1][0] for i in range(len(ch) - 1)):
                best = max(best, len(ch))
        assert f([x[:] for x in iv]) == len(iv) - best


@test("Intervals:calendar")
def _(ns):
    C = ns["Calendar"]
    c = C()
    assert [c.book(10, 20), c.book(15, 25), c.book(20, 30)] == [True, False, True]
    r = random.Random(42)
    for _ in range(100):
        c, booked = C(), []
        for _ in range(r.randint(1, 15)):
            a = r.randint(0, 30)
            b = a + r.randint(1, 6)
            ok = all(b <= s or a >= e for s, e in booked)
            assert c.book(a, b) is ok
            if ok:
                booked.append((a, b))


@test("Intervals:sweep")
def _(ns):
    f = ns["min_rooms"]
    assert f([[0, 30], [5, 10], [15, 20]]) == 2 and f([[7, 10], [2, 4]]) == 1 and f([[1, 5], [5, 9]]) == 1
    r = random.Random(43)
    for _ in range(300):
        iv = [[a, a + r.randint(1, 6)] for a in (r.randint(0, 15) for _ in range(r.randint(1, 8)))]
        want = max(sum(a <= t < b for a, b in iv) for t in range(0, 25))
        assert f([x[:] for x in iv]) == want


# ---- advanced graphs ------------------------------------------------------------------------------------------------

def _random_digraph(r, n, m, lo=1, hi=9):
    return [(r.randrange(n), r.randrange(n), r.randint(lo, hi)) for _ in range(m)]


def _floyd(n, edges):
    inf = float("inf")
    d = [[0 if i == j else inf for j in range(n)] for i in range(n)]
    for u, v, w in edges:
        d[u][v] = min(d[u][v], w)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                d[i][j] = min(d[i][j], d[i][k] + d[k][j])
    return d


@test("Advanced Graphs:dijkstra")
def _(ns):
    f = ns["dijkstra"]
    r = random.Random(44)
    for _ in range(200):
        n = r.randint(1, 7)
        edges = _random_digraph(r, n, r.randint(0, 12))
        assert f(n, edges, 0) == _floyd(n, edges)[0]


@test("Advanced Graphs:euler")
def _(ns):
    f = ns["find_itinerary"]
    assert f([["MUC", "LHR"], ["JFK", "MUC"], ["SFO", "SJC"], ["LHR", "SFO"]]) == ["JFK", "MUC", "LHR", "SFO", "SJC"]
    assert f([["JFK", "SFO"], ["JFK", "ATL"], ["SFO", "ATL"], ["ATL", "JFK"], ["ATL", "SFO"]]) == ["JFK", "ATL", "JFK", "SFO", "ATL", "SFO"]
    import itertools

    r = random.Random(45)
    cities = ["JFK", "AAA", "BBB", "CCC"]
    for _ in range(100):
        # build a valid itinerary, so a path through all the tickets is guaranteed
        route = ["JFK"] + [r.choice(cities) for _ in range(r.randint(1, 6))]
        tickets = [[a, b] for a, b in zip(route, route[1:])]
        r.shuffle(tickets)
        best = None
        for perm in set(itertools.permutations(map(tuple, tickets))):
            if perm[0][0] == "JFK" and all(perm[i][1] == perm[i + 1][0] for i in range(len(perm) - 1)):
                path = [perm[0][0]] + [t[1] for t in perm]
                best = path if best is None or path < best else best
        assert f([t[:] for t in tickets]) == best


@test("Advanced Graphs:mst")
def _(ns):
    f = ns["min_spanning_tree"]
    import itertools

    assert f(4, [(1, 0, 1), (2, 0, 2), (3, 1, 2), (4, 2, 3)]) == 7 and f(3, [(1, 0, 1)]) == -1
    r = random.Random(46)
    for _ in range(100):
        n = r.randint(2, 5)
        edges = [(r.randint(1, 9), *r.sample(range(n), 2)) for _ in range(r.randint(1, 8))]
        best = None
        for combo in itertools.combinations(edges, n - 1):
            parent = list(range(n))

            def find(x):
                while parent[x] != x:
                    x = parent[x]
                return x

            ok = True
            for w, u, v in combo:
                a, b = find(u), find(v)
                if a == b:
                    ok = False
                    break
                parent[a] = b
            if ok:
                cost = sum(w for w, _, _ in combo)
                best = cost if best is None else min(best, cost)
        assert f(n, edges[:]) == (best if best is not None else -1)


@test("Advanced Graphs:bellman")
def _(ns):
    f = ns["cheapest_within_k"]
    flights = [(0, 1, 100), (1, 2, 100), (2, 0, 100), (1, 3, 600), (2, 3, 200)]
    assert f(4, flights, 0, 3, 1) == 700 and f(4, flights, 0, 3, 0) == -1 and f(4, flights, 0, 3, 2) == 400
    r = random.Random(47)

    def brute(n, fl, s, d, k):
        best = float("inf")
        stack = [(s, 0, 0)]
        while stack:
            node, edges_used, cost = stack.pop()
            if node == d:
                best = min(best, cost)
            if edges_used <= k:
                for u, v, w in fl:
                    if u == node:
                        stack.append((v, edges_used + 1, cost + w))
        return -1 if best == float("inf") else best

    for _ in range(150):
        n = r.randint(2, 5)
        fl = _random_digraph(r, n, r.randint(1, 8))
        k = r.randint(0, 3)
        assert f(n, fl, 0, n - 1, k) == brute(n, fl, 0, n - 1, k)


@test("Advanced Graphs:floyd")
def _(ns):
    f = ns["all_pairs"]
    r = random.Random(48)
    for _ in range(100):
        n = r.randint(1, 6)
        edges = _random_digraph(r, n, r.randint(0, 10))
        assert f(n, edges) == _floyd(n, edges)
    assert f(3, [(0, 1, 5), (0, 1, 2), (1, 2, 1)])[0][2] == 3


@test("Advanced Graphs:cycles")
def _(ns):
    f = ns["longest_cycle"]
    assert f([3, 3, 4, 2, 3]) == 3 and f([2, -1, 3, 1]) == -1
    r = random.Random(49)
    for _ in range(300):
        n = r.randint(1, 8)
        nxt = [r.choice([-1] + list(range(n))) for _ in range(n)]
        best = -1
        for s in range(n):
            seen, node, i = {}, s, 0
            while node != -1 and node not in seen:
                seen[node] = i
                node, i = nxt[node], i + 1
            if node != -1:
                best = max(best, i - seen[node])
        assert f(nxt) == best, nxt


@test("Advanced Graphs:articulation")
def _(ns):
    f = ns["bridges_and_cut_points"]
    r = random.Random(50)

    def components(n, edges, skip_edge=None, skip_node=None):
        parent = list(range(n))

        def find(x):
            while parent[x] != x:
                x = parent[x]
            return x

        for i, (a, b) in enumerate(edges):
            if i == skip_edge or a == skip_node or b == skip_node:
                continue
            parent[find(a)] = find(b)
        return len({find(x) for x in range(n) if x != skip_node})

    for _ in range(200):
        n = r.randint(2, 7)
        edges = list({(min(a, b), max(a, b)) for a, b in (r.sample(range(n), 2) for _ in range(r.randint(1, 9)))})
        bridges, cuts = f(n, [list(e) for e in edges])
        base = components(n, edges)
        want_bridges = {tuple(sorted(edges[i])) for i in range(len(edges)) if components(n, edges, skip_edge=i) > base}
        want_cuts = [v for v in range(n) if components(n, edges, skip_node=v) > base - (1 if not any(v in e for e in edges) else 0) and any(v in e for e in edges)]
        assert {tuple(sorted(b)) for b in bridges} == want_bridges, (n, edges)
        assert cuts == want_cuts, (n, edges, cuts, want_cuts)


# ---- arrays and hashing ---------------------------------------------------------------------------------------------

@test("Arrays & Hashing:simulation")
def _(ns):
    f = ns["get_concatenation"]
    assert f([1, 2, 1]) == [1, 2, 1, 1, 2, 1] and f([]) == []


@test("Arrays & Hashing:seen-set")
def _(ns):
    f = ns["contains_duplicate"]
    r = random.Random(60)
    for _ in range(200):
        a = [r.randint(0, 9) for _ in range(r.randint(0, 9))]
        assert f(a) is (len(set(a)) != len(a))


@test("Arrays & Hashing:counting")
def _(ns):
    r = random.Random(61)
    for _ in range(300):
        s = "".join(r.choice("abc") for _ in range(r.randint(0, 6)))
        t = "".join(r.choice("abc") for _ in range(r.randint(0, 6)))
        want = sorted(s) == sorted(t)
        assert ns["is_anagram"](s, t) is want and ns["is_anagram_fixed_alphabet"](s, t) is want


@test("Arrays & Hashing:complement")
def _(ns):
    f = ns["two_sum"]
    r = random.Random(62)
    for _ in range(300):
        a = [r.randint(-5, 9) for _ in range(r.randint(0, 8))]
        t = r.randint(-5, 15)
        got = f(a, t)
        pairs = [(i, j) for i in range(len(a)) for j in range(i + 1, len(a)) if a[i] + a[j] == t]
        if pairs:
            assert len(got) == 2 and got[0] != got[1] and a[got[0]] + a[got[1]] == t
        else:
            assert got == []


@test("Arrays & Hashing:string-match")
def _(ns):
    f = ns["find_all"]
    assert f("abababa", "aba") == [0, 2, 4] and f("abc", "d") == [] and f("a", "abc") == []
    r = random.Random(63)
    for _ in range(300):
        text = "".join(r.choice("ab") for _ in range(r.randint(0, 14)))
        pat = "".join(r.choice("ab") for _ in range(r.randint(1, 4)))
        assert f(text, pat) == [i for i in range(len(text) - len(pat) + 1) if text[i:i + len(pat)] == pat]


@test("Arrays & Hashing:signature")
def _(ns):
    f = ns["group_anagrams"]
    got = f(["eat", "tea", "tan", "ate", "nat", "bat"])
    assert sorted(sorted(g) for g in got) == [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]] and f([""]) == [[""]]


@test("Arrays & Hashing:majority-vote")
def _(ns):
    f = ns["majority_element"]
    r = random.Random(64)
    for _ in range(300):
        n = r.randint(1, 15)
        major = r.randint(0, 3)
        a = [major] * (n // 2 + 1) + [r.randint(0, 3) for _ in range(n - n // 2 - 1)]
        r.shuffle(a)
        assert f(a) == major


@test("Arrays & Hashing:design-hash")
def _(ns):
    S = ns["MyHashSet"]
    s = S()
    r = random.Random(65)
    model = set()
    for _ in range(500):
        k = r.choice([0, 1, 1009, 2018, 10**6, r.randint(0, 10**6)])
        op = r.randint(0, 2)
        if op == 0:
            s.add(k)
            model.add(k)
        elif op == 1:
            s.remove(k)
            model.discard(k)
        else:
            assert s.contains(k) is (k in model)


@test("Arrays & Hashing:sorting")
def _(ns):
    f = ns["merge_sort"]
    r = random.Random(66)
    for _ in range(200):
        a = [r.randint(-9, 9) for _ in range(r.randint(0, 20))]
        assert f(a[:]) == sorted(a)
    pairs = [(1, "a"), (0, "b"), (1, "c"), (0, "d")]
    class K:
        def __init__(self, v):
            self.v = v[0]
            self.tag = v[1]
        def __le__(self, other):
            return self.v <= other.v
    assert [x.tag for x in f([K(p) for p in pairs])] == ["b", "d", "a", "c"], "equal keys keep their order"


@test("Arrays & Hashing:top-k")
def _(ns):
    f = ns["top_k_frequent"]
    assert sorted(f([1, 1, 1, 2, 2, 3], 2)) == [1, 2] and f([1], 1) == [1]
    r = random.Random(67)
    from collections import Counter

    for _ in range(200):
        a = [r.randint(0, 5) for _ in range(r.randint(1, 15))]
        k = r.randint(1, len(set(a)))
        counts = Counter(a)
        got = f(a, k)
        assert len(got) == k and sorted(counts[x] for x in got) == sorted(counts.values())[-k:] or sorted((counts[x] for x in got), reverse=True) == sorted(counts.values(), reverse=True)[:k]


@test("Arrays & Hashing:encoding")
def _(ns):
    enc, dec = ns["encode"], ns["decode"]
    r = random.Random(68)
    for _ in range(300):
        strs = ["".join(r.choice("ab#1 4") for _ in range(r.randint(0, 6))) for _ in range(r.randint(0, 5))]
        assert dec(enc(strs)) == strs, strs
    assert dec(enc(["", ""])) == ["", ""]


@test("Arrays & Hashing:prefix")
def _(ns):
    f = ns["product_except_self"]
    assert f([1, 2, 3, 4]) == [24, 12, 8, 6] and f([-1, 1, 0, -3, 3]) == [0, 0, 9, 0, 0]
    r = random.Random(69)
    for _ in range(200):
        a = [r.randint(-3, 3) for _ in range(r.randint(2, 7))]
        want = []
        for i in range(len(a)):
            p = 1
            for j, x in enumerate(a):
                if j != i:
                    p *= x
            want.append(p)
        assert f(a[:]) == want


@test("Arrays & Hashing:consecutive")
def _(ns):
    f = ns["longest_consecutive"]
    assert f([100, 4, 200, 1, 3, 2]) == 4 and f([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]) == 9 and f([]) == 0
    r = random.Random(70)
    for _ in range(200):
        a = [r.randint(0, 12) for _ in range(r.randint(0, 10))]
        s, best = set(a), 0
        for x in s:
            n = 0
            while x + n in s:
                n += 1
            best = max(best, n)
        assert f(a) == best
    import signal

    def too_slow(*_):
        raise AssertionError("longest_consecutive on one long run is too slow")

    signal.signal(signal.SIGALRM, too_slow)
    signal.alarm(3)
    try:
        assert f(list(range(30000))) == 30000, "only a run's first element may start counting"
    finally:
        signal.alarm(0)


@test("Arrays & Hashing:prefix-map")
def _(ns):
    f = ns["subarray_sum"]
    assert f([1, 1, 1], 2) == 2 and f([1, -1, 0], 0) == 3
    r = random.Random(71)
    for _ in range(300):
        a = [r.randint(-3, 3) for _ in range(r.randint(1, 10))]
        k = r.randint(-4, 4)
        assert f(a, k) == sum(sum(a[i:j]) == k for i in range(len(a)) for j in range(i + 1, len(a) + 1))


@test("Arrays & Hashing:index-marks")
def _(ns):
    f = ns["first_missing_positive"]
    assert f([3, 4, -1, 1]) == 2 and f([7, 8, 9]) == 1 and f([1, 2, 0]) == 3
    r = random.Random(72)
    for _ in range(300):
        a = [r.randint(-3, 12) for _ in range(r.randint(1, 10))]
        have = set(a)
        want = next(i for i in range(1, 50) if i not in have)
        assert f(a[:]) == want


# ---- two pointers ---------------------------------------------------------------------------------------------------

@test("Two Pointers:in-place")
def _(ns):
    f = ns["remove_duplicates"]
    r = random.Random(80)
    for _ in range(200):
        a = sorted(r.randint(0, 5) for _ in range(r.randint(0, 10)))
        want = sorted(set(a))
        b = a[:]
        k = f(b)
        assert k == len(want) and b[:k] == want


@test("Two Pointers:opposite")
def _(ns):
    f = ns["is_palindrome"]
    assert f("A man, a plan, a canal: Panama") is True and f("race a car") is False and f(" ") is True
    r = random.Random(81)
    for _ in range(300):
        s = "".join(r.choice("aAb ,") for _ in range(r.randint(0, 8)))
        t = "".join(c.lower() for c in s if c.isalnum())
        assert f(s) is (t == t[::-1])


@test("Two Pointers:merge-sorted")
def _(ns):
    f = ns["merge"]
    r = random.Random(82)
    for _ in range(200):
        a = sorted(r.randint(0, 9) for _ in range(r.randint(0, 6)))
        b = sorted(r.randint(0, 9) for _ in range(r.randint(0, 6)))
        n1 = a + [0] * len(b)
        f(n1, len(a), b[:], len(b))
        assert n1 == sorted(a + b)


@test("Two Pointers:simulate")
def _(ns):
    f = ns["add_spaces"]
    assert f("LeetcodeHelpsMeLearn", [8, 13, 15]) == "Leetcode Helps Me Learn" and f("abc", []) == "abc" and f("abc", [0]) == " abc"


@test("Two Pointers:ksum")
def _(ns):
    f = ns["three_sum"]
    import itertools

    r = random.Random(83)
    for _ in range(300):
        a = [r.randint(-4, 4) for _ in range(r.randint(0, 9))]
        want = sorted({tuple(sorted(c)) for c in itertools.combinations(a, 3) if sum(c) == 0})
        got = f(a[:])
        assert sorted(tuple(t) for t in got) == want and len(got) == len(want), a


@test("Two Pointers:pair-count")
def _(ns):
    f = ns["num_subseq"]
    assert f([3, 5, 6, 7], 9) == 4 and f([3, 3, 6, 8], 10) == 6 and f([2, 3, 3, 4, 6, 7], 12) == 61
    r = random.Random(84)
    for _ in range(200):
        a = [r.randint(1, 8) for _ in range(r.randint(1, 9))]
        t = r.randint(2, 16)
        want = sum(1 for m in range(1, 1 << len(a)) if min(a[i] for i in range(len(a)) if m >> i & 1) + max(a[i] for i in range(len(a)) if m >> i & 1) <= t)
        assert f(a[:], t) == want % (10**9 + 7)


@test("Two Pointers:greedy-pair")
def _(ns):
    f = ns["num_boats"]
    assert f([1, 2], 3) == 1 and f([3, 2, 2, 1], 3) == 3 and f([3, 5, 3, 4], 5) == 4
    r = random.Random(85)

    def exact(p, limit):
        n = len(p)
        best = [0] + [99] * ((1 << n) - 1)
        for mask in range(1, 1 << n):
            i = (mask & -mask).bit_length() - 1
            rest = mask & ~(1 << i)
            best[mask] = best[rest] + 1
            for j in range(i + 1, n):
                if rest >> j & 1 and p[i] + p[j] <= limit:
                    best[mask] = min(best[mask], best[rest & ~(1 << j)] + 1)
        return best[-1]

    for _ in range(200):
        limit = r.randint(3, 9)
        p = [r.randint(1, limit) for _ in range(r.randint(1, 8))]
        assert f(p[:], limit) == exact(p, limit)


@test("Two Pointers:running-max")
def _(ns):
    f = ns["trap"]
    assert f([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6 and f([4, 2, 0, 3, 2, 5]) == 9 and f([]) == 0
    r = random.Random(86)
    for _ in range(300):
        h = [r.randint(0, 6) for _ in range(r.randint(0, 10))]
        want = sum(max(0, min(max(h[:i + 1]), max(h[i:])) - h[i]) for i in range(len(h)))
        assert f(h) == want


# ---- sliding window -------------------------------------------------------------------------------------------------

@test("Sliding Window:running-best")
def _(ns):
    f = ns["max_profit"]
    assert f([7, 1, 5, 3, 6, 4]) == 5 and f([7, 6, 4, 3, 1]) == 0
    r = random.Random(90)
    for _ in range(200):
        p = [r.randint(0, 9) for _ in range(r.randint(1, 9))]
        assert f(p) == max([0] + [p[j] - p[i] for i in range(len(p)) for j in range(i + 1, len(p))])


@test("Sliding Window:fixed-sum")
def _(ns):
    f = ns["count_windows_at_least"]
    assert f([2, 2, 2, 2, 5, 5, 5, 8], 3, 4) == 3
    r = random.Random(91)
    for _ in range(200):
        a = [r.randint(0, 9) for _ in range(r.randint(3, 12))]
        k = r.randint(1, 3)
        t = r.randint(0, 9)
        assert f(a, k, t) == sum(sum(a[i:i + k]) >= k * t for i in range(len(a) - k + 1))


@test("Sliding Window:window-max")
def _(ns):
    f = ns["longest_unique"]
    assert f("abcabcbb") == 3 and f("bbbbb") == 1 and f("pwwkew") == 3 and f("") == 0 and f("abba") == 2
    r = random.Random(92)
    for _ in range(300):
        s = "".join(r.choice("abc") for _ in range(r.randint(0, 10)))
        assert f(s) == max([0] + [j - i for i in range(len(s)) for j in range(i, len(s) + 1) if len(set(s[i:j])) == j - i])


@test("Sliding Window:fixed-window")
def _(ns):
    f = ns["check_inclusion"]
    assert f("ab", "eidbaooo") is True and f("ab", "eidboaoo") is False
    r = random.Random(93)
    for _ in range(300):
        p = "".join(r.choice("abc") for _ in range(r.randint(1, 3)))
        t = "".join(r.choice("abc") for _ in range(r.randint(0, 8)))
        want = any(sorted(t[i:i + len(p)]) == sorted(p) for i in range(len(t) - len(p) + 1))
        assert f(p, t) is want


@test("Sliding Window:at-most-k")
def _(ns):
    f = ns["longest_at_most_k_distinct"]
    assert f([1, 2, 1], 2) == 3 and f([0, 1, 2, 2], 2) == 3 and f([1, 2, 3], 1) == 1
    r = random.Random(94)
    for _ in range(300):
        a = [r.randint(0, 3) for _ in range(r.randint(0, 10))]
        k = r.randint(0, 3)
        want = max([0] + [j - i for i in range(len(a)) for j in range(i, len(a) + 1) if len(set(a[i:j])) <= k])
        assert f(a, k) == want


@test("Sliding Window:window-sort")
def _(ns):
    f = ns["closest_k"]
    assert f([1, 2, 3, 4, 5], 4, 3) == [1, 2, 3, 4] and f([1, 1, 2, 3, 4, 5], 4, -1) == [1, 1, 2, 3]
    r = random.Random(95)
    for _ in range(300):
        a = sorted(r.randint(-9, 9) for _ in range(r.randint(1, 12)))
        k = r.randint(1, len(a))
        x = r.randint(-12, 12)
        assert f(a, k, x) == sorted(sorted(a, key=lambda v: (abs(v - x), v))[:k])


@test("Sliding Window:count-windows")
def _(ns):
    f = ns["subarrays_with_k_distinct"]
    assert f([1, 2, 1, 2, 3], 2) == 7 and f([1, 2, 1, 3, 4], 3) == 3
    r = random.Random(96)
    for _ in range(300):
        a = [r.randint(0, 3) for _ in range(r.randint(1, 10))]
        k = r.randint(1, 3)
        assert f(a, k) == sum(len(set(a[i:j])) == k for i in range(len(a)) for j in range(i + 1, len(a) + 1))


@test("Sliding Window:window-min")
def _(ns):
    f = ns["min_window"]
    assert f("ADOBECODEBANC", "ABC") == "BANC" and f("a", "a") == "a" and f("a", "aa") == ""
    r = random.Random(97)
    from collections import Counter

    for _ in range(300):
        s = "".join(r.choice("abc") for _ in range(r.randint(1, 10)))
        t = "".join(r.choice("abc") for _ in range(r.randint(1, 3)))
        need = Counter(t)
        best = min((len(s[i:j]) for i in range(len(s)) for j in range(i + 1, len(s) + 1) if not need - Counter(s[i:j])), default=None)
        got = f(s, t)
        if best is None:
            assert got == ""
        else:
            assert len(got) == best and not need - Counter(got) and got in s


@test("Sliding Window:mono-deque")
def _(ns):
    f = ns["max_sliding_window"]
    assert f([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7] and f([1], 1) == [1]
    r = random.Random(98)
    for _ in range(300):
        a = [r.randint(-5, 5) for _ in range(r.randint(1, 12))]
        k = r.randint(1, len(a))
        assert f(a, k) == [max(a[i:i + k]) for i in range(len(a) - k + 1)]


# ---- stack ----------------------------------------------------------------------------------------------------------

@test("Stack:simulate-stack")
def _(ns):
    f = ns["asteroid_collision"]
    assert f([5, 10, -5]) == [5, 10] and f([8, -8]) == [] and f([10, 2, -5]) == [10] and f([-2, -1, 1, 2]) == [-2, -1, 1, 2]
    r = random.Random(100)

    def brute(a):
        a = a[:]
        changed = True
        while changed:
            changed = False
            for i in range(len(a) - 1):
                if a[i] > 0 > a[i + 1]:
                    if a[i] > -a[i + 1]:
                        del a[i + 1]
                    elif a[i] < -a[i + 1]:
                        del a[i]
                    else:
                        del a[i:i + 2]
                    changed = True
                    break
        return a

    for _ in range(300):
        a = [r.choice([-1, 1]) * r.randint(1, 6) for _ in range(r.randint(0, 9))]
        assert f(a) == brute(a), a


@test("Stack:matching")
def _(ns):
    f = ns["is_valid"]
    assert f("()[]{}") is True and f("(]") is False and f("([)]") is False and f("{[]}") is True and f("((") is False and f(")") is False
    r = random.Random(101)
    for _ in range(300):
        s = "".join(r.choice("()[]{}") for _ in range(r.randint(0, 8)))
        t = s
        while True:
            u = t.replace("()", "").replace("[]", "").replace("{}", "")
            if u == t:
                break
            t = u
        assert f(s) is (t == "")


@test("Stack:design-queue-stack")
def _(ns):
    Q = ns["MyQueue"]
    r = random.Random(102)
    q, model = Q(), []
    for _ in range(500):
        op = r.randint(0, 3)
        if op == 0 or not model:
            v = r.randint(0, 99)
            q.push(v)
            model.append(v)
        elif op == 1:
            assert q.pop() == model.pop(0)
        elif op == 2:
            assert q.peek() == model[0]
        else:
            assert q.empty() is False
    while model:
        assert q.pop() == model.pop(0)
    assert q.empty() is True


@test("Stack:aux-stack")
def _(ns):
    S = ns["MinStack"]
    r = random.Random(103)
    s, model = S(), []
    for _ in range(500):
        op = r.randint(0, 2)
        if op == 0 or not model:
            v = r.randint(-9, 9)
            s.push(v)
            model.append(v)
        elif op == 1:
            s.pop()
            model.pop()
        if model:
            assert s.top() == model[-1] and s.get_min() == min(model)


@test("Stack:expression")
def _(ns):
    f = ns["eval_rpn"]
    assert f(["2", "1", "+", "3", "*"]) == 9 and f(["4", "13", "5", "/", "+"]) == 6 and f(["3", "-4", "/"]) == 0
    assert f(["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]) == 22
    r = random.Random(104)

    def gen(depth):
        if depth == 0 or r.random() < 0.3:
            v = r.randint(-9, 9)
            return [str(v)], v
        a, av = gen(depth - 1)
        b, bv = gen(depth - 1)
        op = r.choice("+-*/")
        if op == "/" and bv == 0:
            op = "+"
        value = {"+": av + bv, "-": av - bv, "*": av * bv, "/": int(av / bv) if bv else 0}[op]
        return a + b + [op], value

    for _ in range(300):
        tokens, value = gen(3)
        assert f(tokens) == value, tokens


@test("Stack:mono-stack")
def _(ns):
    f = ns["daily_temperatures"]
    assert f([73, 74, 75, 71, 69, 72, 76, 73]) == [1, 1, 4, 2, 1, 1, 0, 0]
    r = random.Random(105)
    for _ in range(300):
        t = [r.randint(30, 40) for _ in range(r.randint(1, 12))]
        want = [next((j - i for j in range(i + 1, len(t)) if t[j] > t[i]), 0) for i in range(len(t))]
        assert f(t) == want


@test("Stack:nested")
def _(ns):
    f = ns["decode_string"]
    assert f("3[a]2[bc]") == "aaabcbc" and f("3[a2[c]]") == "accaccacc" and f("2[abc]3[cd]ef") == "abcabccdcdcdef" and f("10[a]") == "a" * 10


@test("Stack:calculator")
def _(ns):
    f = ns["calculate"]
    assert f("3+2*2") == 7 and f(" 3/2 ") == 1 and f(" 3+5 / 2 ") == 5 and f("14-3/2") == 13 and f("42") == 42
    r = random.Random(106)
    for _ in range(300):
        nums = [r.randint(1, 20) for _ in range(r.randint(1, 5))]
        ops = [r.choice("+-*/") for _ in range(len(nums) - 1)]
        text = str(nums[0]) + "".join(f"{o}{n}" for o, n in zip(ops, nums[1:]))
        terms, cur, sign = [], nums[0], 1
        for o, n in zip(ops, nums[1:]):
            if o == "*":
                cur *= n
            elif o == "/":
                cur = int(cur / n)
            else:
                terms.append(sign * cur)
                cur, sign = n, 1 if o == "+" else -1
        terms.append(sign * cur)
        assert f(text) == sum(terms), text


@test("Stack:mono-contrib")
def _(ns):
    f = ns["sum_subarray_mins"]
    assert f([3, 1, 2, 4]) == 17 and f([11, 81, 94, 43, 3]) == 444
    r = random.Random(107)
    for _ in range(300):
        a = [r.randint(1, 5) for _ in range(r.randint(1, 9))]
        assert f(a) == sum(min(a[i:j]) for i in range(len(a)) for j in range(i + 1, len(a) + 1)) % (10**9 + 7)


# ---- binary search --------------------------------------------------------------------------------------------------

@test("Binary Search:classic")
def _(ns):
    f = ns["search"]
    r = random.Random(110)
    for _ in range(300):
        a = sorted(r.sample(range(-20, 20), r.randint(0, 12)))
        t = r.randint(-22, 22)
        assert f(a, t) == (a.index(t) if t in a else -1)


@test("Binary Search:insert-pos")
def _(ns):
    import bisect

    r = random.Random(111)
    for _ in range(300):
        a = sorted(r.randint(0, 9) for _ in range(r.randint(0, 12)))
        t = r.randint(-1, 10)
        assert ns["lower_bound"](a, t) == bisect.bisect_left(a, t) and ns["upper_bound"](a, t) == bisect.bisect_right(a, t)


@test("Binary Search:by-count")
def _(ns):
    f = ns["arrange_coins"]
    assert [f(n) for n in (0, 1, 2, 5, 8, 10)] == [0, 1, 1, 2, 3, 4]
    for n in list(range(0, 300)) + [2**31 - 1]:
        k = 0
        while (k + 1) * (k + 2) // 2 <= n:
            k += 1
        assert f(n) == k, n


@test("Binary Search:on-answer")
def _(ns):
    f = ns["min_eating_speed"]
    assert f([3, 6, 7, 11], 8) == 4 and f([30, 11, 23, 4, 20], 5) == 30 and f([30, 11, 23, 4, 20], 6) == 23
    r = random.Random(112)
    for _ in range(200):
        piles = [r.randint(1, 20) for _ in range(r.randint(1, 6))]
        h = r.randint(len(piles), len(piles) + 12)
        want = next(k for k in range(1, 21) if sum(-(-p // k) for p in piles) <= h)
        assert f(piles, h) == want


@test("Binary Search:rotated")
def _(ns):
    r = random.Random(113)
    for _ in range(300):
        a = sorted(r.sample(range(-15, 15), r.randint(1, 10)))
        k = r.randrange(len(a))
        rot = a[k:] + a[:k]
        assert ns["find_min"](rot) == min(a)
        t = r.randint(-16, 16)
        got = ns["search_rotated"](rot, t)
        assert got == (rot.index(t) if t in rot else -1)


@test("Binary Search:weighted")
def _(ns):
    P = ns["WeightedPicker"]
    p = P([3, 1, 5])
    assert [p.pick(r) for r in range(9)] == [0, 0, 0, 1, 2, 2, 2, 2, 2]
    seen = {p.pick() for _ in range(200)}
    assert seen == {0, 1, 2}


@test("Binary Search:partition")
def _(ns):
    f = ns["find_median"]
    r = random.Random(114)
    for _ in range(300):
        a = sorted(r.randint(-9, 9) for _ in range(r.randint(0, 7)))
        b = sorted(r.randint(-9, 9) for _ in range(r.randint(0 if a else 1, 7)))
        m = sorted(a + b)
        n = len(m)
        want = m[n // 2] if n % 2 else (m[n // 2 - 1] + m[n // 2]) / 2
        assert f(a, b) == want, (a, b)


@test("Binary Search:peak")
def _(ns):
    f = ns["find_peak"]
    r = random.Random(115)
    for _ in range(300):
        a = [r.randint(0, 9) for _ in range(r.randint(1, 10))]
        a = [x * 2 + (i % 2) for i, x in enumerate(a)]
        a = [v for i, v in enumerate(a) if i == 0 or v != a[i - 1]] or [0]
        i = f(a)
        assert (i == 0 or a[i - 1] < a[i]) and (i == len(a) - 1 or a[i] > a[i + 1]), (a, i)


# ---- linked list ----------------------------------------------------------------------------------------------------

@test("Linked List:reverse")
def _(ns):
    r = random.Random(120)
    for _ in range(200):
        v = [r.randint(0, 9) for _ in range(r.randint(0, 9))]
        assert _ll_vals(ns["reverse_list"](_ll(v))) == v[::-1]
    for _ in range(200):
        v = [r.randint(0, 9) for _ in range(r.randint(1, 9))]
        left = r.randint(1, len(v))
        right = r.randint(left, len(v))
        want = v[:left - 1] + v[left - 1:right][::-1] + v[right:]
        assert _ll_vals(ns["reverse_between"](_ll(v), left, right)) == want


@test("Linked List:dummy-merge")
def _(ns):
    r = random.Random(121)
    for _ in range(200):
        a = sorted(r.randint(0, 9) for _ in range(r.randint(0, 6)))
        b = sorted(r.randint(0, 9) for _ in range(r.randint(0, 6)))
        assert _ll_vals(ns["merge_two_lists"](_ll(a), _ll(b))) == sorted(a + b)


@test("Linked List:fast-slow")
def _(ns):
    r = random.Random(122)
    for _ in range(300):
        n = r.randint(1, 10)
        nodes = [ListNode(i) for i in range(n)]
        for a, b in zip(nodes, nodes[1:]):
            a.next = b
        pos = r.randint(-1, n - 1)
        if pos >= 0:
            nodes[-1].next = nodes[pos]
        assert ns["has_cycle"](nodes[0]) is (pos >= 0)
        assert ns["cycle_start"](nodes[0]) is (nodes[pos] if pos >= 0 else None)
        if pos < 0:
            assert ns["middle"](nodes[0]) is nodes[n // 2]


@test("Linked List:splice")
def _(ns):
    r = random.Random(123)
    for _ in range(300):
        v = [r.randint(0, 3) for _ in range(r.randint(0, 9))]
        x = r.randint(0, 3)
        assert _ll_vals(ns["remove_elements"](_ll(v), x)) == [y for y in v if y != x]


@test("Linked List:gap")
def _(ns):
    r = random.Random(124)
    for _ in range(300):
        v = [r.randint(0, 9) for _ in range(r.randint(1, 10))]
        n = r.randint(1, len(v))
        assert _ll_vals(ns["remove_nth_from_end"](_ll(v), n)) == v[:len(v) - n] + v[len(v) - n + 1:]


@test("Linked List:clone-map")
def _(ns):
    class N:
        def __init__(self, x, next=None, random=None):
            self.val, self.next, self.random = x, next, random

    ns["Node"] = N
    r = random.Random(125)
    for _ in range(200):
        n = r.randint(1, 8)
        nodes = [N(r.randint(0, 9)) for _ in range(n)]
        for a, b in zip(nodes, nodes[1:]):
            a.next = b
        picks = [r.choice([None] + list(range(n))) for _ in range(n)]
        for node, k in zip(nodes, picks):
            node.random = None if k is None else nodes[k]
        copy = ns["copy_random_list"](nodes[0])
        cs = []
        while copy:
            cs.append(copy)
            copy = copy.next
        assert len(cs) == n and not ({id(c) for c in cs} & {id(x) for x in nodes})
        assert [None if c.random is None else cs.index(c.random) for c in cs] == picks


@test("Linked List:design-list")
def _(ns):
    Q = ns["RingQueue"]
    r = random.Random(126)
    for _ in range(100):
        k = r.randint(1, 5)
        q, model = Q(k), []
        for _ in range(60):
            op = r.randint(0, 3)
            if op == 0:
                v = r.randint(0, 99)
                ok = len(model) < k
                assert q.enqueue(v) is ok
                if ok:
                    model.append(v)
            elif op == 1:
                assert q.dequeue() is bool(model)
                if model:
                    model.pop(0)
            elif op == 2:
                assert q.front() == (model[0] if model else -1)
            else:
                assert q.rear() == (model[-1] if model else -1)


@test("Linked List:lru")
def _(ns):
    L = ns["LRUCache"]
    r = random.Random(127)
    for _ in range(100):
        cap = r.randint(1, 4)
        c, order = L(cap), []
        for _ in range(60):
            k = r.randint(0, 6)
            if r.random() < 0.5:
                v = r.randint(0, 99)
                c.put(k, v)
                order = [(a, b) for a, b in order if a != k] + [(k, v)]
                if len(order) > cap:
                    order.pop(0)
            else:
                want = next((b for a, b in order if a == k), -1)
                assert c.get(k) == want
                if want != -1:
                    order = [(a, b) for a, b in order if a != k] + [(k, want)]


@test("Linked List:kway-merge")
def _(ns):
    r = random.Random(128)
    for _ in range(200):
        lists = [sorted(r.randint(-5, 5) for _ in range(r.randint(0, 5))) for _ in range(r.randint(0, 6))]
        assert _ll_vals(ns["merge_k_lists"]([_ll(v) for v in lists])) == sorted(x for v in lists for x in v)


# ---- trees ----------------------------------------------------------------------------------------------------------

import page_tests as _pt  # noqa: E402


@test("Trees:dfs")
def _(ns):
    r = random.Random(130)

    def mirror(t):
        return None if t is None else (t.val, mirror(t.right), mirror(t.left))

    for _ in range(200):
        t = _pt._random_tree(r, r.randint(0, 15))
        want, h = mirror(t), _pt._height(t)
        assert ns["max_depth"](t) == h
        assert _shape(ns["invert_tree"](t)) == want


@test("Trees:dfs-return")
def _(ns):
    r = random.Random(131)
    for _ in range(200):
        t = _pt._random_tree(r, r.randint(1, 12))
        assert ns["diameter"](t) == max(_pt._tree_distances(t).values())


@test("Trees:bst-walk")
def _(ns):
    f = ns["lowest_common_ancestor"]
    r = random.Random(132)
    for _ in range(300):
        t = _pt._random_bst(r, r.randint(2, 15))
        p, q = r.sample(_pt._preorder(t), 2)

        def path(target):
            out, cur = [], t
            while True:
                out.append(cur)
                if cur is target:
                    return out
                cur = cur.left if target.val < cur.val else cur.right

        a, b = path(p), path(q)
        assert f(t, p, q) is [x for x, y in zip(a, b) if x is y][-1]


@test("Trees:bst-edit")
def _(ns):
    r = random.Random(133)
    for _ in range(300):
        keys = r.sample(range(30), r.randint(0, 12))
        root = None
        for k in keys:
            root = ns["insert"](root, k)
        assert _pt._inorder_vals(root) == sorted(keys)
        if keys:
            gone = r.choice(keys)
            root = ns["delete"](root, gone)
            assert _pt._inorder_vals(root) == sorted(set(keys) - {gone})
        assert ns["delete"](root, 99) is root or root is None


@test("Trees:bfs-levels")
def _(ns):
    r = random.Random(134)
    for _ in range(200):
        t = _pt._random_tree(r, r.randint(0, 15))
        assert ns["level_order"](t) == _pt._levels(t)


@test("Trees:tree-as-graph")
def _(ns):
    f = ns["min_time_to_collect"]
    assert f(7, [[0, 1], [0, 2], [1, 4], [1, 5], [2, 3], [2, 6]], [False, False, True, False, True, True, False]) == 8
    assert f(7, [[0, 1], [0, 2], [1, 4], [1, 5], [2, 3], [2, 6]], [False] * 7) == 0
    r = random.Random(135)
    for _ in range(200):
        n = r.randint(1, 9)
        edges = [[r.randrange(i), i] for i in range(1, n)]
        apples = [r.random() < 0.4 for _ in range(n)]
        parent = {i: p for p, i in edges}

        def needed(v):
            while v in parent:
                yield v
                v = parent[v]

        used = {v for v in range(n) if apples[v] for v in needed(v)}
        assert f(n, edges, apples) == 2 * len(used)


@test("Trees:dfs-carry")
def _(ns):
    r = random.Random(136)

    def count(t, seen):
        return 0 if t is None else (all(v <= t.val for v in seen)) + count(t.left, seen + [t.val]) + count(t.right, seen + [t.val])

    for _ in range(200):
        t = _pt._random_tree(r, r.randint(1, 14), -5, 5)
        assert ns["good_nodes"](t) == count(t, [])


@test("Trees:inorder")
def _(ns):
    r = random.Random(137)
    for _ in range(200):
        n = r.randint(1, 14)
        t = _pt._random_bst(r, n)
        k = r.randint(1, n)
        assert ns["kth_smallest"](t, k) == _pt._inorder_vals(t)[k - 1]


@test("Trees:from-traversals")
def _(ns):
    r = random.Random(138)
    for _ in range(200):
        t = _pt._random_tree(r, r.randint(1, 14), -30, 30, distinct=True)
        pre = [x.val for x in _pt._preorder(t)]
        assert _shape(ns["build_tree"](pre, _pt._inorder_vals(t))) == _shape(t)


@test("Trees:catalan")
def _(ns):
    assert [ns["num_trees"](n) for n in range(1, 8)] == [1, 2, 5, 14, 42, 132, 429]
    for n in range(1, 6):
        trees = ns["generate_trees"](1, n)
        assert len(trees) == ns["num_trees"](n) and len({_shape(t) for t in trees}) == len(trees)
        assert all(_pt._inorder_vals(t) == list(range(1, n + 1)) for t in trees)


@test("Trees:dfs-edit")
def _(ns):
    r = random.Random(139)

    def prune(t, target):
        if t is None:
            return None
        left, right = prune(t.left, target), prune(t.right, target)
        return None if left is None and right is None and t.val == target else (t.val, left, right)

    for _ in range(200):
        t = _pt._random_tree(r, r.randint(1, 14), 1, 3)
        target = r.randint(1, 3)
        assert _shape(ns["remove_leaf_nodes"](t, target)) == prune(t, target)


@test("Trees:serialize")
def _(ns):
    r = random.Random(140)
    for _ in range(200):
        t = _pt._random_tree(r, r.randint(0, 14), -1000, 1000)
        want = _shape(t)
        assert _shape(ns["deserialize"](ns["serialize"](t))) == want


# ---- heap -----------------------------------------------------------------------------------------------------------

@test("Heap / Priority Queue:size-k")
def _(ns):
    r = random.Random(150)
    for _ in range(100):
        k = r.randint(1, 5)
        nums = [r.randint(-9, 9) for _ in range(r.randint(max(0, k - 1), k + 3))]
        h, seen = ns["KthLargest"](k, nums[:]), nums[:]
        for _ in range(15):
            x = r.randint(-9, 9)
            seen.append(x)
            assert h.add(x) == sorted(seen)[-k]


@test("Heap / Priority Queue:pool")
def _(ns):
    f = ns["last_stone_weight"]
    assert f([2, 7, 4, 1, 8, 1]) == 1 and f([1]) == 1 and f([2, 2]) == 0
    r = random.Random(151)
    for _ in range(200):
        s = [r.randint(1, 20) for _ in range(r.randint(1, 8))]
        left = sorted(s)
        while len(left) > 1:
            y, x = left.pop(), left.pop()
            if y != x:
                left.append(y - x)
                left.sort()
        assert f(s[:]) == (left[0] if left else 0)


@test("Heap / Priority Queue:quickselect")
def _(ns):
    f = ns["find_kth_largest"]
    r = random.Random(152)
    for _ in range(300):
        a = [r.randint(-6, 6) for _ in range(r.randint(1, 12))]
        k = r.randint(1, len(a))
        assert f(a[:], k) == sorted(a)[-k]


@test("Heap / Priority Queue:cooldown")
def _(ns):
    f = ns["least_interval"]
    assert f(list("AAABBB"), 2) == 8 and f(list("AAABBB"), 0) == 6 and f(list("AAAAAABCDEFG"), 2) == 16
    from collections import Counter

    r = random.Random(153)
    for _ in range(300):
        tasks = [r.choice("ABCD") for _ in range(r.randint(1, 14))]
        n = r.randint(0, 4)
        counts = Counter(tasks).values()
        most = max(counts)
        want = max(len(tasks), (most - 1) * (n + 1) + sum(c == most for c in counts))
        assert f(tasks, n) == want


@test("Heap / Priority Queue:schedule-sim")
def _(ns):
    f = ns["get_order"]
    assert f([[1, 2], [2, 4], [3, 2], [4, 1]]) == [0, 2, 3, 1] and f([[7, 10], [7, 12], [7, 5], [7, 4], [7, 2]]) == [4, 3, 2, 0, 1]
    r = random.Random(154)
    for _ in range(200):
        tasks = [[r.randint(1, 12), r.randint(1, 5)] for _ in range(r.randint(1, 8))]
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
        assert f([x[:] for x in tasks]) == want


@test("Heap / Priority Queue:two-heaps")
def _(ns):
    r = random.Random(155)
    for _ in range(100):
        m, seen = ns["MedianFinder"](), []
        for _ in range(20):
            x = r.randint(-9, 9)
            m.add_num(x)
            seen.append(x)
            s = sorted(seen)
            mid = len(s) // 2
            assert m.find_median() == (s[mid] if len(s) % 2 else (s[mid - 1] + s[mid]) / 2)


@test("Heap / Priority Queue:greedy-heap")
def _(ns):
    f = ns["find_maximized_capital"]
    assert f(2, 0, [1, 2, 3], [0, 1, 1]) == 4 and f(3, 0, [1, 2, 3], [0, 1, 2]) == 6
    r = random.Random(156)
    for _ in range(200):
        n = r.randint(1, 8)
        profits = [r.randint(0, 9) for _ in range(n)]
        capital = [r.randint(0, 10) for _ in range(n)]
        k, w = r.randint(1, 5), r.randint(0, 5)
        money, left = w, set(range(n))
        for _ in range(k):
            ok = [i for i in left if capital[i] <= money]
            if not ok:
                break
            i = max(ok, key=lambda x: profits[x])
            money += profits[i]
            left.discard(i)
        assert f(k, w, profits[:], capital[:]) == money


# ---- backtracking ---------------------------------------------------------------------------------------------------

import itertools as _it  # noqa: E402


@test("Backtracking:include-exclude")
def _(ns):
    for n in range(0, 7):
        got = ns["subsets"](list(range(n)))
        assert len(got) == 2**n and len({tuple(g) for g in got}) == 2**n


@test("Backtracking:reuse")
def _(ns):
    f = ns["combination_sum"]
    assert sorted(map(sorted, f([2, 3, 6, 7], 7))) == [[2, 2, 3], [7]]
    r = random.Random(160)
    for _ in range(100):
        c = sorted(r.sample(range(1, 8), r.randint(1, 4)))
        t = r.randint(1, 12)
        want = {tuple(sorted(x)) for k in range(1, t + 1) for x in _it.combinations_with_replacement(c, k) if sum(x) == t}
        got = f(c[:], t)
        assert {tuple(sorted(x)) for x in got} == want and len(got) == len(want)


@test("Backtracking:skip-dups")
def _(ns):
    f = ns["combination_sum2"]
    assert sorted(f([10, 1, 2, 7, 6, 1, 5], 8)) == [[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]]
    r = random.Random(161)
    for _ in range(150):
        c = [r.randint(1, 5) for _ in range(r.randint(1, 8))]
        t = r.randint(1, 10)
        want = {tuple(sorted(x)) for k in range(1, len(c) + 1) for x in _it.combinations(c, k) if sum(x) == t}
        got = f(c[:], t)
        assert {tuple(x) for x in got} == want and len(got) == len(want)


@test("Backtracking:permute")
def _(ns):
    f = ns["permutations"]
    for n in range(0, 6):
        got = f(list(range(n)))
        assert sorted(map(tuple, got)) == sorted(_it.permutations(range(n)))


@test("Backtracking:construct")
def _(ns):
    f = ns["generate_parentheses"]
    assert sorted(f(3)) == sorted(["((()))", "(()())", "(())()", "()(())", "()()()"])
    assert [len(f(n)) for n in range(1, 8)] == [1, 2, 5, 14, 42, 132, 429]


@test("Backtracking:grid")
def _(ns):
    f = ns["exist"]
    b = [["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]]
    assert f([r[:] for r in b], "ABCCED") is True and f([r[:] for r in b], "SEE") is True and f([r[:] for r in b], "ABCB") is False
    r = random.Random(162)

    def brute(g, w):
        rows, cols = len(g), len(g[0])

        def go(i, j, k, used):
            if g[i][j] != w[k]:
                return False
            if k == len(w) - 1:
                return True
            return any(0 <= a < rows and 0 <= c < cols and (a, c) not in used and go(a, c, k + 1, used | {(i, j)}) for a, c in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)))

        return any(go(i, j, 0, frozenset()) for i in range(rows) for j in range(cols))

    for _ in range(150):
        g = [[r.choice("ab") for _ in range(r.randint(1, 3))]]
        g = [[r.choice("ab") for _ in range(len(g[0]))] for _ in range(r.randint(1, 3))]
        w = "".join(r.choice("ab") for _ in range(r.randint(1, 5)))
        assert f([row[:] for row in g], w) is brute(g, w)


@test("Backtracking:partition-k")
def _(ns):
    f = ns["can_make_square"]
    assert f([1, 1, 2, 2, 2]) is True and f([3, 3, 3, 3, 4]) is False
    assert f([6, 3, 2, 2, 8, 9, 6, 12, 1, 12, 12, 12, 3, 6, 6]) is False
    r = random.Random(163)
    for _ in range(150):
        s = [r.randint(1, 6) for _ in range(r.randint(4, 9))]
        want = False
        total = sum(s)
        if total % 4 == 0:
            side = total // 4
            want = any(all(sum(s[i] for i in range(len(s)) if a[i] == g) == side for g in range(4)) for a in _it.product(range(4), repeat=len(s)))
        assert f(s[:]) is want


@test("Backtracking:n-queens")
def _(ns):
    f = ns["solve_n_queens"]
    assert [len(f(n)) for n in range(1, 8)] == [1, 0, 0, 2, 10, 4, 40]
    for board in f(6):
        cols = [row.index("Q") for row in board]
        assert len(set(cols)) == 6 and len({r - c for r, c in enumerate(cols)}) == 6 and len({r + c for r, c in enumerate(cols)}) == 6


@test("Backtracking:split-memo")
def _(ns):
    f = ns["word_break"]
    assert sorted(f("catsanddog", ["cat", "cats", "and", "sand", "dog"])) == ["cat sand dog", "cats and dog"]
    r = random.Random(164)

    def every(s, words):
        if not s:
            return [[]]
        return [[w] + rest for w in words if s.startswith(w) for rest in every(s[len(w):], words)]

    for _ in range(150):
        words = sorted({"".join(r.choice("ab") for _ in range(r.randint(1, 3))) for _ in range(r.randint(1, 4))})
        s = "".join(r.choice("ab") for _ in range(r.randint(1, 8)))
        assert sorted(f(s, words)) == sorted(" ".join(x) for x in every(s, words))
    assert f("a" * 40 + "b", ["a", "aa", "aaa"]) == []


@test("Backtracking:combinations-k")
def _(ns):
    f = ns["combine"]
    assert f(4, 2) == [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]
    for n in range(1, 8):
        for k in range(1, n + 1):
            got = f(n, k)
            assert sorted(map(tuple, got)) == sorted(_it.combinations(range(1, n + 1), k)) and len(got) == len({tuple(g) for g in got})


@test("Backtracking:bitmask-subsets")
def _(ns):
    f, g = ns["all_subsets"], ns["count_subsets"]
    for n in range(0, 8):
        got = f(list(range(n)))
        assert len(got) == 2**n and len({tuple(x) for x in got}) == 2**n
    r = random.Random(165)
    for _ in range(100):
        a = [r.randint(1, 9) for _ in range(r.randint(0, 9))]
        want = sum(1 for k in range(len(a) + 1) for c in _it.combinations(a, k) if sum(c) % 3 == 0)
        assert g(a, lambda x: sum(x) % 3 == 0) == want


@test("Backtracking:letter-product")
def _(ns):
    f, h = ns["letter_combinations"], ns["letter_case_permutations"]
    assert f("") == [] and sorted(f("23")) == ["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"]
    assert len(f("7979")) == 4 * 4 * 4 * 4
    assert sorted(h("a1b2")) == ["A1B2", "A1b2", "a1B2", "a1b2"]
    assert h("12") == ["12"] and len(h("abcde")) == 32


@test("Backtracking:min-removals")
def _(ns):
    f = ns["remove_invalid_parentheses"]
    assert sorted(f("()())()")) == ["(())()", "()()()"] and sorted(f("(a)())()")) == ["(a())()", "(a)()()"]
    assert f(")(") == [""]
    r = random.Random(166)

    def good(t):
        d = 0
        for ch in t:
            d += (ch == "(") - (ch == ")")
            if d < 0:
                return False
        return d == 0

    for _ in range(200):
        s = "".join(r.choice("()a") for _ in range(r.randint(0, 9)))
        pos = [i for i, ch in enumerate(s) if ch in "()"]
        best, found = None, set()
        for mask in range(1 << len(pos)):
            gone = {pos[i] for i in range(len(pos)) if mask >> i & 1}
            t = "".join(ch for i, ch in enumerate(s) if i not in gone)
            if good(t) and (best is None or len(gone) < best):
                best, found = len(gone), set()
            if good(t) and len(gone) == best:
                found.add(t)
        got = f(s)
        assert sorted(got) == sorted(found) and len(got) == len(set(got))


@test("Backtracking:operators")
def _(ns):
    f = ns["add_operators"]
    assert sorted(f("123", 6)) == ["1*2*3", "1+2+3"] and sorted(f("232", 8)) == ["2*3+2", "2+3*2"]
    assert sorted(f("105", 5)) == ["1*0+5", "10-5"] and sorted(f("00", 0)) == ["0*0", "0+0", "0-0"]
    assert f("3456237490", 9191) == []
    r = random.Random(167)
    for _ in range(80):
        num = "".join(r.choice("0123456789") for _ in range(r.randint(1, 5)))
        target = r.randint(-20, 60)
        want = set()
        for ops in _it.product(["", "+", "-", "*"], repeat=len(num) - 1):
            expr = num[0] + "".join(o + c for o, c in zip(ops, num[1:]))
            nums = expr.replace("+", " ").replace("-", " ").replace("*", " ").split()
            if any(len(x) > 1 and x[0] == "0" for x in nums):
                continue
            if eval(expr) == target:
                want.add(expr)
        got = f(num, target)
        assert sorted(got) == sorted(want) and len(got) == len(set(got)), (num, target)


@test("Backtracking:segments")
def _(ns):
    f = ns["restore_ip_addresses"]
    assert sorted(f("25525511135")) == ["255.255.11.135", "255.255.111.35"]
    assert f("0000") == ["0.0.0.0"] and sorted(f("101023")) == sorted(
        ["1.0.10.23", "1.0.102.3", "10.1.0.23", "10.10.2.3", "101.0.2.3"])
    r = random.Random(168)
    for _ in range(150):
        s = "".join(r.choice("0125") for _ in range(r.randint(1, 12)))
        want = set()
        for cuts in _it.combinations(range(1, len(s)), 3):
            parts = [s[a:b] for a, b in zip((0,) + cuts, cuts + (len(s),))]
            if all((len(x) == 1 or x[0] != "0") and int(x) <= 255 for x in parts):
                want.add(".".join(parts))
        got = f(s)
        assert sorted(got) == sorted(want) and len(got) == len(set(got))


@test("Backtracking:sudoku")
def _(ns):
    f = ns["solve_sudoku"]
    puzzles = [
        ["53..7....", "6..195...", ".98....6.", "8...6...3", "4..8.3..1", "7...2...6", ".6....28.", "...419..5", "....8..79"],
        ["..9748...", "7........", ".2.1.9...", "..7...24.", ".64.1.59.", ".98...3..", "...8.3.2.", "........6", "...2759.."],
    ]
    for rows in puzzles + [["." * 9] * 9]:
        board = [list(row) for row in rows]
        f(board)
        digits = set("123456789")
        for i in range(9):
            assert set(board[i]) == digits and {board[r][i] for r in range(9)} == digits
            assert {board[i // 3 * 3 + a][i % 3 * 3 + b] for a in range(3) for b in range(3)} == digits
        for r in range(9):
            for c in range(9):
                assert rows[r][c] in (".", board[r][c]), "a given digit was changed"


@test("Backtracking:kth-permutation")
def _(ns):
    f = ns["get_permutation"]
    for n in range(1, 7):
        every = ["".join(map(str, p)) for p in _it.permutations(range(1, n + 1))]
        assert [f(n, k) for k in range(1, len(every) + 1)] == every
    assert f(9, 362880) == "987654321"


@test("Backtracking:kth-permutation#Next permutation (in place)")
def _(ns):
    f = ns["next_permutation"]
    r = random.Random(169)
    for _ in range(300):
        a = [r.randint(0, 3) for _ in range(r.randint(0, 7))]
        bigger = [p for p in set(_it.permutations(a)) if list(p) > a]
        want = list(min(bigger)) if bigger else sorted(a)
        b = a[:]
        f(b)
        assert b == want, (a, b, want)


@test("Backtracking:path-undo")
def _(ns):
    f = ns["all_paths"]
    assert sorted(f([[1, 2], [3], [3], []])) == [[0, 1, 3], [0, 2, 3]]
    r = random.Random(171)
    for _ in range(150):
        n = r.randint(2, 7)
        g = [[j for j in range(i + 1, n) if r.random() < 0.5] for i in range(n)]
        want, stack = [], [(0,)]
        while stack:
            p = stack.pop()
            if p[-1] == n - 1:
                want.append(list(p))
            else:
                stack += [p + (v,) for v in g[p[-1]]]
        got = f([row[:] for row in g])
        assert sorted(got) == sorted(want)
        assert len({id(x) for x in got}) == len(got), "every path must be its own list"


@test("Backtracking:meet-in-the-middle")
def _(ns):
    f = ns["closest_subset_sum"]
    assert f([5, -7, 3, 5], 6) == 0 and f([7, -9, 15, -2], -5) == 1 and f([1, 2, 3], -7) == 7
    r = random.Random(172)
    for _ in range(200):
        a = [r.randint(-12, 12) for _ in range(r.randint(1, 11))]
        goal = r.randint(-40, 40)
        want = min(abs(sum(c) - goal) for k in range(len(a) + 1) for c in _it.combinations(a, k))
        assert f(a[:], goal) == want, (a, goal)


@test("Backtracking:bound-prune")
def _(ns):
    f = ns["distribute_cookies"]
    assert f([8, 15, 10, 20, 8], 2) == 31 and f([6, 1, 3, 2, 2, 4, 1, 2], 3) == 7 and f([5], 1) == 5
    r = random.Random(173)
    for _ in range(120):
        a = [r.randint(1, 9) for _ in range(r.randint(1, 8))]
        k = r.randint(1, 4)
        want = min(max(sum(a[i] for i in range(len(a)) if x[i] == g) for g in range(k)) for x in _it.product(range(k), repeat=len(a)))
        assert f(a[:], k) == want, (a, k)


@test("Backtracking:game-memo")
def _(ns):
    f = ns["can_i_win"]
    assert f(10, 11) is False and f(10, 0) is True and f(10, 40) is False and f(4, 6) is True
    for m in range(1, 8):
        for total in range(1, 30):
            if m * (m + 1) // 2 < total:
                assert f(m, total) is False
                continue

            def win(used, remaining):
                return any(x >= remaining or not win(used | {x}, remaining - x) for x in range(1, m + 1) if x not in used)

            assert f(m, total) is win(frozenset(), total), (m, total)


@test("Backtracking:gray-code")
def _(ns):
    f = ns["gray_code"]
    assert f(2) == [0, 1, 3, 2]
    for n in range(1, 11):
        g = f(n)
        assert g[0] == 0 and sorted(g) == list(range(2**n))
        assert all(bin(g[i] ^ g[(i + 1) % len(g)]).count("1") == 1 for i in range(len(g)))


@test("Backtracking:n-queens#Bitmasks")
def _(ns):
    f = ns["total_n_queens"]
    assert [f(n) for n in range(1, 9)] == [1, 0, 0, 2, 10, 4, 40, 92]


@test("Backtracking:multiset-counts")
def _(ns):
    f = ns["num_tile_possibilities"]
    assert f("AAB") == 8 and f("AAABBC") == 188 and f("V") == 1
    r = random.Random(174)
    for _ in range(100):
        t = "".join(r.choice("abc") for _ in range(r.randint(1, 6)))
        want = {"".join(p) for k in range(1, len(t) + 1) for p in _it.permutations(t, k)}
        assert f(t) == len(want)


@test("Backtracking:position-rule")
def _(ns):
    f = ns["count_arrangements"]
    assert [f(n) for n in range(1, 7)] == [1, 2, 3, 8, 10, 36]
    for n in range(1, 9):
        want = sum(1 for p in _it.permutations(range(1, n + 1)) if all(v % i == 0 or i % v == 0 for i, v in enumerate(p, 1)))
        assert f(n) == want


@test("Backtracking:digit-walk")
def _(ns):
    f = ns["nums_same_consec_diff"]
    assert sorted(f(3, 7)) == [181, 292, 707, 818, 929] and sorted(f(2, 1))[:3] == [10, 12, 21]
    for n in range(2, 6):
        for k in range(0, 10):
            want = [x for x in range(10 ** (n - 1), 10**n) if all(abs(int(a) - int(b)) == k for a, b in zip(str(x), str(x)[1:]))]
            got = f(n, k)
            assert sorted(got) == want and len(got) == len(set(got)), (n, k)


@test("Backtracking:lexi-walk")
def _(ns):
    f = ns["lexical_order"]
    assert f(13) == [1, 10, 11, 12, 13, 2, 3, 4, 5, 6, 7, 8, 9]
    for n in list(range(1, 400)) + [1000, 1001, 12345, 99999, 100000]:
        assert f(n) == sorted(range(1, n + 1), key=str), n


@test("Backtracking:lexi-walk#K-th in dictionary order")
def _(ns):
    f = ns["find_kth_number"]
    assert f(13, 2) == 10 and f(1, 1) == 1
    for n in (9, 13, 100, 101, 1234, 20000):
        order = sorted(range(1, n + 1), key=str)
        for k in list(range(1, min(n, 60) + 1)) + [n, n // 2 + 1]:
            assert f(n, k) == order[k - 1], (n, k)
    assert f(10**9, 10**9) == 999999999


@test("Backtracking:split-combine")
def _(ns):
    f = ns["diff_ways_to_compute"]
    assert f("2-1-1") == [0, 2] and f("2*3-4*5") == [-34, -14, -10, -10, 10]
    r = random.Random(175)

    def brute(toks):
        if len(toks) == 1:
            return [toks[0]]
        out = []
        for i in range(1, len(toks), 2):
            for a in brute(toks[:i]):
                for b in brute(toks[i + 1:]):
                    out.append(a + b if toks[i] == "+" else a - b if toks[i] == "-" else a * b)
        return out

    for _ in range(100):
        k = r.randint(1, 5)
        toks = [r.randint(0, 20)]
        for _ in range(k):
            toks += [r.choice("+-*"), r.randint(0, 20)]
        expr = "".join(map(str, toks))
        assert f(expr) == sorted(brute(toks))


@test("Backtracking:split-combine#All binary search trees")
def _(ns):
    f = ns["generate_trees"]
    assert f(0) == [] and [len(f(n)) for n in range(1, 7)] == [1, 2, 5, 14, 42, 132]

    def inorder(t):
        return inorder(t.left) + [t.val] + inorder(t.right) if t else []

    def shape(t):
        return None if t is None else (t.val, shape(t.left), shape(t.right))

    for n in range(1, 6):
        trees = f(n)
        assert all(inorder(t) == list(range(1, n + 1)) for t in trees)
        assert len({shape(t) for t in trees}) == len(trees)


@test("Backtracking:eulerian")
def _(ns):
    f = ns["find_itinerary"]
    assert f([["MUC", "LHR"], ["JFK", "MUC"], ["SFO", "SJC"], ["LHR", "SFO"]]) == ["JFK", "MUC", "LHR", "SFO", "SJC"]
    assert f([["JFK", "SFO"], ["JFK", "ATL"], ["SFO", "ATL"], ["ATL", "JFK"], ["ATL", "SFO"]]) == ["JFK", "ATL", "JFK", "SFO", "ATL", "SFO"]
    r = random.Random(176)
    for _ in range(150):
        cities = ["JFK", "AAA", "BBB", "CCC"]
        walk = ["JFK"]
        for _ in range(r.randint(1, 7)):
            walk.append(r.choice(cities))
        tickets = [[a, b] for a, b in zip(walk, walk[1:])]
        r.shuffle(tickets)

        def best(city, left, path):
            if not left:
                return path
            for t in sorted(set(map(tuple, left))):
                if t[0] == city:
                    rest = [list(x) for x in left]
                    rest.remove(list(t))
                    got = best(t[1], rest, path + [t[1]])
                    if got:
                        return got
            return None

        assert f([t[:] for t in tickets]) == best("JFK", tickets, ["JFK"]), tickets


@test("Backtracking:eulerian#De Bruijn sequence (the safe)")
def _(ns):
    f = ns["crack_safe"]
    assert f(1, 2) in ("01", "10")
    for n, k in ((1, 4), (2, 2), (2, 3), (3, 2), (3, 3), (4, 2), (2, 10)):
        s = f(n, k)
        assert len(s) == k**n + n - 1
        assert {s[i:i + n] for i in range(len(s) - n + 1)} == {"".join(p) for p in _it.product("0123456789"[:k], repeat=n)}


@test("Backtracking:all-shortest")
def _(ns):
    f = ns["find_ladders"]
    got = f("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"])
    assert sorted(got) == [["hit", "hot", "dot", "dog", "cog"], ["hit", "hot", "lot", "log", "cog"]]
    assert f("hit", "cog", ["hot", "dot", "dog", "lot", "log"]) == []
    r = random.Random(177)
    for _ in range(120):
        words = list({"".join(r.choice("abc") for _ in range(3)) for _ in range(r.randint(1, 9))})
        begin, end = "".join(r.choice("abc") for _ in range(3)), r.choice(words)
        if begin == end:
            continue
        pool = set(words)
        found, best = [], [10**9]

        def go(path):
            w = path[-1]
            if len(path) > best[0]:
                return
            if w == end:
                if len(path) < best[0]:
                    best[0], found[:] = len(path), []
                found.append(path[:])
                return
            for v in pool:
                if v not in path and sum(a != b for a, b in zip(w, v)) == 1:
                    path.append(v)
                    go(path)
                    path.pop()

        go([begin])
        assert sorted(f(begin, end, words)) == sorted(found), (begin, end, words)


@test("Backtracking:best-walk")
def _(ns):
    f = ns["get_maximum_gold"]
    assert f([[0, 6, 0], [5, 8, 7], [0, 9, 0]]) == 24
    assert f([[1, 0, 7], [2, 0, 6], [3, 4, 5], [0, 3, 0], [9, 0, 20]]) == 28
    r = random.Random(178)

    def brute(g):
        rows, cols = len(g), len(g[0])

        def go(i, j, seen):
            best = 0
            for a, b in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                if 0 <= a < rows and 0 <= b < cols and g[a][b] and (a, b) not in seen:
                    best = max(best, go(a, b, seen | {(a, b)}))
            return g[i][j] + best

        return max((go(i, j, frozenset({(i, j)})) for i in range(rows) for j in range(cols) if g[i][j]), default=0)

    for _ in range(150):
        g = _grid(r, r.randint(1, 4), r.randint(1, 4), [0, 0, 1, 2, 5])
        assert f([row[:] for row in g]) == brute(g)


@test("Backtracking:best-walk#Graph with a time limit")
def _(ns):
    f = ns["maximal_path_quality"]
    assert f([0, 32, 10, 43], [[0, 1, 10], [1, 2, 15], [0, 3, 10]], 49) == 75
    assert f([5, 10, 15, 20], [[0, 1, 10], [1, 2, 10], [0, 3, 10]], 30) == 25
    assert f([1, 2, 3, 4], [[0, 1, 10], [1, 2, 11], [2, 3, 12], [1, 3, 13]], 50) == 7
    r = random.Random(179)
    for _ in range(100):
        n = r.randint(1, 5)
        values = [r.randint(0, 20) for _ in range(n)]
        edges = [[a, b, r.randint(1, 6)] for a in range(n) for b in range(a + 1, n) if r.random() < 0.6]
        limit = r.randint(1, 16)
        best = 0
        stack = [(0, 0, frozenset({0}))]
        seen = set()
        while stack:
            st = stack.pop()
            if st in seen:
                continue
            seen.add(st)
            u, t, vis = st
            if u == 0:
                best = max(best, sum(values[i] for i in vis))
            for a, b, w in edges:
                for x, y in ((a, b), (b, a)):
                    if x == u and t + w <= limit:
                        stack.append((y, t + w, vis | {y}))
        assert f(values, [e[:] for e in edges], limit) == best


@test("Backtracking:verbal-sum")
def _(ns):
    f = ns["is_solvable"]
    assert f(["SEND", "MORE"], "MONEY") is True and f(["SIX", "SEVEN", "SEVEN"], "TWENTY") is True
    assert f(["LEET", "CODE"], "POINT") is False and f(["A", "B"], "A") is True
    r = random.Random(180)
    for _ in range(80):
        words = ["".join(r.choice("abcd") for _ in range(r.randint(1, 3))) for _ in range(r.randint(1, 2))]
        result = "".join(r.choice("abcd") for _ in range(r.randint(1, 4)))
        letters = sorted(set("".join(words) + result))
        lead = {w[0] for w in words + [result] if len(w) > 1}

        def value(w, m):
            return int("".join(str(m[c]) for c in w))

        want = any(
            all(not (m[c] == 0 and c in lead) for c in letters) and sum(value(w, m) for w in words) == value(result, m)
            for p in _it.permutations(range(10), len(letters))
            for m in [dict(zip(letters, p))]
        )
        assert f(words[:], result) is want, (words, result)


@test("Backtracking:pyramid")
def _(ns):
    f = ns["pyramid_transition"]
    assert f("BCD", ["BCC", "CDE", "CEA", "FFF"]) is True
    assert f("AAAA", ["AAB", "AAC", "BCD", "BBE", "DEF"]) is False
    r = random.Random(181)

    def brute(row, rules):
        if len(row) == 1:
            return True
        opts = [[t[2] for t in rules if t[:2] == row[i:i + 2]] for i in range(len(row) - 1)]
        return any(brute("".join(c), rules) for c in _it.product(*opts))

    for _ in range(150):
        rules = list({"".join(r.choice("ABC") for _ in range(3)) for _ in range(r.randint(1, 10))})
        row = "".join(r.choice("ABC") for _ in range(r.randint(2, 5)))
        assert f(row, rules[:]) is brute(row, rules), (row, rules)


@test("Backtracking:best-subset")
def _(ns):
    f = ns["max_score_words"]
    s2 = [1, 0, 9, 5, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    assert f(["dog", "cat", "dad", "good"], list("abcdddgoo"), s2) == 23
    r = random.Random(182)
    for _ in range(120):
        words = ["".join(r.choice("abc") for _ in range(r.randint(1, 3))) for _ in range(r.randint(1, 6))]
        letters = [r.choice("abc") for _ in range(r.randint(0, 8))]
        sc = [r.randint(0, 9) for _ in range(26)]
        best = 0
        for mask in range(1 << len(words)):
            used = [c for i in range(len(words)) if mask >> i & 1 for c in words[i]]
            if all(used.count(c) <= letters.count(c) for c in set(used)):
                best = max(best, sum(sc[ord(c) - 97] for c in used))
        assert f(words, letters[:], sc) == best


@test("Backtracking:submask")
def _(ns):
    f = ns["min_sessions"]
    assert f([1, 2, 3], 3) == 2 and f([3, 1, 3, 1, 1], 8) == 2 and f([1, 2, 3, 4, 5], 15) == 1
    r = random.Random(183)
    for _ in range(100):
        limit = r.randint(3, 9)
        tasks = [r.randint(1, limit) for _ in range(r.randint(1, 7))]

        def brute(i, bins):
            if i == len(tasks):
                return len(bins)
            best = len(tasks) + 1
            for b in range(len(bins)):
                if bins[b] + tasks[i] <= limit:
                    bins[b] += tasks[i]
                    best = min(best, brute(i + 1, bins))
                    bins[b] -= tasks[i]
            return min(best, brute(i + 1, bins + [tasks[i]]))

        assert f(tasks[:], limit) == brute(0, []), (tasks, limit)


@test("Backtracking:mask-assign")
def _(ns):
    f = ns["max_compatibility_sum"]
    assert f([[1, 1, 0], [1, 0, 1], [0, 0, 1]], [[1, 0, 0], [0, 0, 1], [1, 1, 0]]) == 8
    assert f([[0, 0], [0, 0], [0, 0]][:2], [[1, 1], [1, 1]]) == 0
    r = random.Random(184)
    for _ in range(100):
        n, q = r.randint(1, 6), r.randint(1, 4)
        a = [[r.randint(0, 1) for _ in range(q)] for _ in range(n)]
        b = [[r.randint(0, 1) for _ in range(q)] for _ in range(n)]
        want = max(sum(sum(x == y for x, y in zip(a[i], b[p[i]])) for i in range(n)) for p in _it.permutations(range(n)))
        assert f(a, b) == want


@test("Backtracking:unique-split")
def _(ns):
    f = ns["max_unique_split"]
    assert f("ababccc") == 5 and f("aba") == 2 and f("aa") == 1
    r = random.Random(185)
    for _ in range(150):
        s = "".join(r.choice("abc") for _ in range(r.randint(1, 11)))
        best = 0
        for mask in range(1 << (len(s) - 1)):
            cuts = [0] + [i + 1 for i in range(len(s) - 1) if mask >> i & 1] + [len(s)]
            parts = [s[a:b] for a, b in zip(cuts, cuts[1:])]
            if len(set(parts)) == len(parts):
                best = max(best, len(parts))
        assert f(s) == best, s


@test("Backtracking:lazy-iterator")
def _(ns):
    cls = ns["CombinationIterator"]
    it = cls("abc", 2)
    assert [it.next(), it.hasNext(), it.next(), it.hasNext(), it.next(), it.hasNext()] == ["ab", True, "ac", True, "bc", False]
    for n in range(1, 8):
        for k in range(1, n + 1):
            chars = "abcdefgh"[:n]
            it, got = cls(chars, k), []
            while it.hasNext():
                got.append(it.next())
            assert got == ["".join(c) for c in _it.combinations(chars, k)]


# ---- tries ----------------------------------------------------------------------------------------------------------

@test("Tries:trie")
def _(ns):
    r = random.Random(170)
    for _ in range(100):
        t, words = ns["Trie"](), set()
        for _ in range(30):
            w = "".join(r.choice("abc") for _ in range(r.randint(1, 4)))
            op = r.randint(0, 2)
            if op == 0:
                t.insert(w)
                words.add(w)
            elif op == 1:
                assert t.search(w) is (w in words)
            else:
                assert t.starts_with(w) is any(x.startswith(w) for x in words)


@test("Tries:trie-dfs")
def _(ns):
    r = random.Random(171)

    def matches(p, w):
        return len(p) == len(w) and all(a in (".", b) for a, b in zip(p, w))

    for _ in range(100):
        d, words = ns["WordDictionary"](), []
        for _ in range(30):
            if r.random() < 0.4:
                w = "".join(r.choice("abc") for _ in range(r.randint(1, 4)))
                d.add_word(w)
                words.append(w)
            else:
                q = "".join(r.choice("abc.") for _ in range(r.randint(1, 4)))
                assert d.search(q) is any(matches(q, w) for w in words)


@test("Tries:trie-grid")
def _(ns):
    f = ns["find_words"]
    board = [["o", "a", "a", "n"], ["e", "t", "a", "e"], ["i", "h", "k", "r"], ["i", "f", "l", "v"]]
    assert sorted(f(board, ["oath", "pea", "eat", "rain"])) == ["eat", "oath"]
    r = random.Random(172)

    def has(g, w):
        rows, cols = len(g), len(g[0])

        def go(i, j, k, used):
            if g[i][j] != w[k]:
                return False
            if k == len(w) - 1:
                return True
            return any(0 <= a < rows and 0 <= c < cols and (a, c) not in used and go(a, c, k + 1, used | {(i, j)}) for a, c in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)))

        return any(go(i, j, 0, frozenset()) for i in range(rows) for j in range(cols))

    for _ in range(150):
        g = [[r.choice("abc") for _ in range(r.randint(1, 3))]]
        g = [[r.choice("abc") for _ in range(len(g[0]))] for _ in range(r.randint(1, 3))]
        words = sorted({"".join(r.choice("abc") for _ in range(r.randint(1, 4))) for _ in range(r.randint(1, 6))})
        got = f([row[:] for row in g], words[:])
        assert sorted(got) == [w for w in words if has(g, w)]


# ---- math and geometry ----------------------------------------------------------------------------------------------

@test("Math & Geometry:number-format")
def _(ns):
    f, g = ns["convert_to_title"], ns["title_to_number"]
    assert f(1) == "A" and f(26) == "Z" and f(27) == "AA" and f(701) == "ZY" and f(703) == "AAA" and f(2**31 - 1) == "FXSHRXW"
    for n in range(1, 3000):
        assert g(f(n)) == n


@test("Math & Geometry:number-theory")
def _(ns):
    import math

    r = random.Random(180)
    for _ in range(300):
        a, b = r.randint(0, 200), r.randint(0, 200)
        assert ns["gcd"](a, b) == math.gcd(a, b)
    for n in (0, 1, 2, 3, 30, 100, 541):
        assert ns["sieve"](n) == [p for p in range(2, n + 1) if all(p % d for d in range(2, p))]
    assert ns["gcd_of_strings"]("ABCABC", "ABC") == "ABC" and ns["gcd_of_strings"]("LEET", "CODE") == ""


@test("Math & Geometry:formula")
def _(ns):
    f = ns["count_odds"]
    for low in range(0, 20):
        for high in range(low, 25):
            assert f(low, high) == sum(x % 2 for x in range(low, high + 1))


@test("Math & Geometry:matrix-sim")
def _(ns):
    f = ns["transpose"]
    assert f([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]] and f([[1]]) == [[1]]


@test("Math & Geometry:matrix-inplace")
def _(ns):
    r = random.Random(181)
    for n in range(1, 7):
        m = [[r.randint(0, 9) for _ in range(n)] for _ in range(n)]
        want = [list(row) for row in zip(*m[::-1])]
        assert ns["rotate"](m) is None and m == want


@test("Math & Geometry:spiral")
def _(ns):
    f = ns["spiral_order"]
    assert f([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == [1, 2, 3, 6, 9, 8, 7, 4, 5] and f([[1, 2, 3, 4]]) == [1, 2, 3, 4] and f([[1], [2], [3]]) == [1, 2, 3]
    r = random.Random(182)
    for _ in range(200):
        rows, cols = r.randint(1, 6), r.randint(1, 6)
        m = [[i * cols + j for j in range(cols)] for i in range(rows)]
        got = f([row[:] for row in m])
        assert sorted(got) == list(range(rows * cols))
        assert got[:cols] == m[0]


@test("Math & Geometry:markers")
def _(ns):
    r = random.Random(183)
    for _ in range(300):
        rows, cols = r.randint(1, 5), r.randint(1, 5)
        m = [[0 if r.random() < 0.2 else r.randint(1, 9) for _ in range(cols)] for _ in range(rows)]
        zr = {i for i in range(rows) for j in range(cols) if m[i][j] == 0}
        zc = {j for i in range(rows) for j in range(cols) if m[i][j] == 0}
        want = [[0 if i in zr or j in zc else m[i][j] for j in range(cols)] for i in range(rows)]
        ns["set_zeroes"](m)
        assert m == want


@test("Math & Geometry:number-cycle")
def _(ns):
    f = ns["is_happy"]

    def happy(n):
        seen = set()
        while n != 1 and n not in seen:
            seen.add(n)
            n = sum(int(c) ** 2 for c in str(n))
        return n == 1

    for n in list(range(1, 400)) + [2147483647]:
        assert f(n) is happy(n)


@test("Math & Geometry:digits")
def _(ns):
    r = random.Random(184)
    for _ in range(300):
        d = [r.choice([9, 9, r.randint(0, 9)]) for _ in range(r.randint(1, 8))]
        if d[0] == 0 and len(d) > 1:
            d[0] = 1
        assert int("".join(map(str, ns["plus_one"](d[:])))) == int("".join(map(str, d))) + 1
        a, b = str(r.randint(0, 10**9)), str(r.randint(0, 10**9))
        assert ns["add_strings"](a, b) == str(int(a) + int(b))


@test("Math & Geometry:fast-pow")
def _(ns):
    import math

    f = ns["my_pow"]
    assert f(2.0, 10) == 1024.0 and f(2.0, -2) == 0.25 and f(5.0, 0) == 1.0
    r = random.Random(185)
    for _ in range(300):
        x, n = r.choice([0.5, 1.5, 2.0, -2.0, 3.0]), r.randint(-10, 10)
        assert math.isclose(f(x, n), x**n, rel_tol=1e-9)
    assert math.isclose(f(1.0000000001, 2**31 - 1), 1.0000000001 ** (2**31 - 1), rel_tol=1e-5)


@test("Math & Geometry:point-counts")
def _(ns):
    D = ns["DetectSquares"]
    d = D()
    for p in ([3, 10], [11, 2], [3, 2]):
        d.add(p)
    assert d.count([11, 10]) == 1 and d.count([14, 8]) == 0
    d.add([11, 2])
    assert d.count([11, 10]) == 2


@test("Math & Geometry:median")
def _(ns):
    f = ns["min_operations"]
    assert f([[2, 4], [6, 8]], 2) == 4 and f([[1, 5], [2, 3]], 1) == 5 and f([[1, 2], [3, 4]], 2) == -1
    r = random.Random(186)
    for _ in range(200):
        x = r.randint(1, 3)
        g = [[r.randint(0, 9) for _ in range(r.randint(1, 3))]]
        g = [[r.randint(0, 9) for _ in range(len(g[0]))] for _ in range(r.randint(1, 3))]
        vals = [v for row in g for v in row]
        best = None
        for t in range(0, 10):
            if all((v - t) % x == 0 for v in vals):
                cost = sum(abs(v - t) // x for v in vals)
                best = cost if best is None else min(best, cost)
        assert f(g, x) == (best if best is not None else -1)


@test("Math & Geometry:lex-order")
def _(ns):
    f = ns["lexical_order"]
    assert f(13) == [1, 10, 11, 12, 13, 2, 3, 4, 5, 6, 7, 8, 9]
    for n in list(range(1, 200)) + [5000]:
        assert f(n) == sorted(range(1, n + 1), key=str)


# ---- bit manipulation -----------------------------------------------------------------------------------------------

@test("Bit Manipulation:xor")
def _(ns):
    r = random.Random(190)
    for _ in range(200):
        vals = r.sample(range(-50, 50), r.randint(1, 8))
        nums = vals + vals[1:]
        r.shuffle(nums)
        assert ns["single_number"](nums) == vals[0]
        n = r.randint(1, 20)
        arr = list(range(n + 1))
        gone = arr.pop(r.randrange(n + 1))
        r.shuffle(arr)
        assert ns["missing_number"](arr) == gone


@test("Bit Manipulation:bit-count")
def _(ns):
    r = random.Random(191)
    for _ in range(200):
        n = r.randint(0, 2**31 - 1)
        assert ns["hamming_weight"](n) == bin(n).count("1")
    assert ns["count_bits"](5) == [0, 1, 1, 2, 1, 2] and ns["count_bits"](0) == [0]


@test("Bit Manipulation:shift")
def _(ns):
    f = ns["reverse_bits"]
    assert f(43261596) == 964176192 and f(1) == 2**31 and f(0) == 0
    r = random.Random(192)
    for _ in range(200):
        n = r.randint(0, 2**32 - 1)
        assert f(n) == int(f"{n:032b}"[::-1], 2)


@test("Bit Manipulation:add-bits")
def _(ns):
    f = ns["get_sum"]
    r = random.Random(193)
    for _ in range(500):
        a, b = r.randint(-1000, 1000), r.randint(-1000, 1000)
        assert f(a, b) == a + b
    assert f(-(2**31), 2**31 - 1) == -1


@test("Bit Manipulation:digit-extract")
def _(ns):
    f = ns["reverse_integer"]
    assert f(123) == 321 and f(-123) == -321 and f(120) == 21 and f(1534236469) == 0 and f(-2147483648) == 0
    r = random.Random(194)
    for _ in range(300):
        x = r.randint(-(2**31), 2**31 - 1)
        want = (-1 if x < 0 else 1) * int(str(abs(x))[::-1])
        assert f(x) == (want if -(2**31) <= want <= 2**31 - 1 else 0)


@test("Bit Manipulation:prefix-xor")
def _(ns):
    f = ns["xor_queries"]
    assert f([1, 3, 4, 8], [[0, 1], [1, 2], [0, 3], [3, 3]]) == [2, 7, 14, 8]
    r = random.Random(195)
    for _ in range(200):
        a = [r.randint(0, 31) for _ in range(r.randint(1, 8))]
        qs = [sorted((r.randrange(len(a)), r.randrange(len(a)))) for _ in range(5)]
        from functools import reduce

        assert f(a, qs) == [reduce(lambda x, y: x ^ y, a[l:r_ + 1]) for l, r_ in qs]


# ---- extras: lessons for techniques with no must-learn problem (decision 32). A variant's key is "<id>#<tab name>".


def _random_graph(r, n, p, directed=False):
    g = {u: [] for u in range(n)}
    for u in range(n):
        for v in range(n):
            if u != v and r.random() < p and (directed or u < v):
                g[u].append(v)
                if not directed:
                    g[v].append(u)
    return g


def _reachable(g, s):
    seen, stack = {s}, [s]
    while stack:
        u = stack.pop()
        for v in g[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return seen


@test("Graphs:dfs")
def _(ns):
    f = ns["dfs_recursive"]
    assert f({0: [1, 2], 1: [3], 2: [3], 3: []}, 0) == [0, 1, 3, 2]
    r = random.Random(301)
    for _ in range(200):
        g = _random_graph(r, r.randint(1, 8), 0.3, directed=True)
        order = f(g, 0)
        assert len(order) == len(set(order)) and set(order) == _reachable(g, 0)


@test("Graphs:dfs#Iterative (explicit stack)")
def _(ns):
    f = ns["dfs_iterative"]
    assert f({0: [1, 2], 1: [3], 2: [3], 3: []}, 0) == [0, 1, 3, 2]
    # the same visiting order as the recursive version
    def rec(g, s):
        seen, order = set(), []

        def visit(u):
            seen.add(u)
            order.append(u)
            for v in g[u]:
                if v not in seen:
                    visit(v)

        visit(s)
        return order

    r = random.Random(302)
    for _ in range(300):
        g = _random_graph(r, r.randint(1, 9), 0.3, directed=True)
        assert f(g, 0) == rec(g, 0)
    chain = {i: [i + 1] for i in range(5000)}
    chain[5000] = []
    assert len(f(chain, 0)) == 5001  # deeper than the recursion limit


@test("Graphs:bfs-levels")
def _(ns):
    f = ns["bfs_levels"]
    assert f({0: [1, 2], 1: [3], 2: [3], 3: []}, 0) == {0: 0, 1: 1, 2: 1, 3: 2}
    r = random.Random(303)
    for _ in range(200):
        g = _random_graph(r, r.randint(1, 8), 0.3, directed=True)
        got = f(g, 0)
        # relaxation to a fixed point as an independent model
        want = {0: 0}
        changed = True
        while changed:
            changed = False
            for u, d in list(want.items()):
                for v in g[u]:
                    if v not in want or want[v] > d + 1:
                        want[v] = d + 1
                        changed = True
        assert got == want


@test("Graphs:bidir-bfs")
def _(ns):
    f = ns["bidirectional_steps"]
    path = {i: [j for j in (i - 1, i + 1) if 0 <= j < 6] for i in range(6)}
    assert f(path, 0, 5) == 5 and f(path, 3, 3) == 0
    assert f({0: [], 1: []}, 0, 1) == -1
    r = random.Random(304)
    for _ in range(400):
        n = r.randint(2, 9)
        g = _random_graph(r, n, 0.25)
        a, b = r.randrange(n), r.randrange(n)
        dist = {a: 0}
        queue = deque([a])
        while queue:
            u = queue.popleft()
            for v in g[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    queue.append(v)
        assert f(g, a, b) == dist.get(b, -1)


@test("Graphs:topo-layers")
def _(ns):
    f = ns["topo_layers"]
    assert [sorted(x) for x in f(4, [(0, 1), (0, 2), (1, 3), (2, 3)])] == [[0], [1, 2], [3]]
    assert f(2, [(0, 1), (1, 0)]) is None and f(3, []) == [[0, 1, 2]]
    r = random.Random(305)
    for _ in range(300):
        n = r.randint(1, 8)
        edges = [(a, b) for a in range(n) for b in range(a + 1, n) if r.random() < 0.3]
        got = f(n, edges)
        depth = [0] * n
        for b in range(n):  # nodes are numbered in a topological order
            for a, bb in edges:
                if bb == b:
                    depth[b] = max(depth[b], depth[a] + 1)
        want = [[u for u in range(n) if depth[u] == d] for d in range(max(depth) + 1)]
        assert [sorted(layer) for layer in got] == want


@test("Advanced Graphs:zero-one-bfs")
def _(ns):
    f = ns["zero_one_bfs"]
    g = {0: [(1, 0), (2, 1)], 1: [(2, 0)], 2: []}
    assert f(g, 0) == {0: 0, 1: 0, 2: 0}
    r = random.Random(306)
    inf = float("inf")
    for _ in range(300):
        n = r.randint(1, 7)
        g = {u: [(v, r.randint(0, 1)) for v in range(n) if v != u and r.random() < 0.35] for u in range(n)}
        want = {u: inf for u in range(n)}
        want[0] = 0
        for _ in range(n):  # Bellman-Ford as the model
            for u in range(n):
                for v, w in g[u]:
                    want[v] = min(want[v], want[u] + w)
        assert f(g, 0) == want


# ---- extras of the DP pages


def _min_cost_model(cost):
    n = len(cost)
    best = [0] * (n + 1)
    for i in range(2, n + 1):
        best[i] = min(best[i - 1] + cost[i - 1], best[i - 2] + cost[i - 2])
    return best[n]


def _check_min_cost(ns):
    f = ns["min_cost_climbing"]
    assert f([10, 15, 20]) == 15 and f([1, 100, 1, 1, 1, 100, 1, 1, 100, 1]) == 6
    r = random.Random(401)
    for _ in range(200):
        c = [r.randint(0, 20) for _ in range(r.randint(2, 14))]
        assert f(c) == _min_cost_model(c)


@test("1-D Dynamic Programming:memo-vs-table")
def _(ns):
    _check_min_cost(ns)


@test("1-D Dynamic Programming:memo-vs-table#Bottom-up (table)")
def _(ns):
    _check_min_cost(ns)
    assert ns["min_cost_climbing"]([1] * 5000) == 2500  # no recursion limit


def _edit_model(a, b):
    t = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        for j in range(len(b) + 1):
            if i == 0 or j == 0:
                t[i][j] = i + j
            elif a[i - 1] == b[j - 1]:
                t[i][j] = t[i - 1][j - 1]
            else:
                t[i][j] = 1 + min(t[i - 1][j], t[i][j - 1], t[i - 1][j - 1])
    return t[-1][-1]


def _check_edit(ns):
    f = ns["edit_distance"]
    assert f("horse", "ros") == 3 and f("intention", "execution") == 5 and f("", "abc") == 3 and f("abc", "") == 3 and f("", "") == 0
    r = random.Random(402)
    for _ in range(300):
        a = "".join(r.choice("abc") for _ in range(r.randint(0, 7)))
        b = "".join(r.choice("abc") for _ in range(r.randint(0, 7)))
        assert f(a, b) == _edit_model(a, b), (a, b)


@test("1-D Dynamic Programming:rolling-row")
def _(ns):
    _check_edit(ns)


@test("1-D Dynamic Programming:rolling-row#One row and a diagonal")
def _(ns):
    _check_edit(ns)


@test("1-D Dynamic Programming:reconstruct")
def _(ns):
    f = ns["largest_divisible_subset"]
    assert len(f([1, 2, 3])) == 2 and f([1, 2, 4, 8]) == [1, 2, 4, 8] and f([]) == []
    r = random.Random(403)
    for _ in range(300):
        nums = r.sample(range(1, 40), r.randint(0, 9))
        got = f(list(nums))
        assert set(got) <= set(nums) and len(got) == len(set(got))
        assert all(b % a == 0 for a, b in zip(got, got[1:])), got  # a chain: each divides the next
        # brute force: the best size over every subset that is a chain
        best = 0
        for mask in range(1 << len(nums)):
            sub = sorted(nums[i] for i in range(len(nums)) if mask >> i & 1)
            if all(b % a == 0 for a, b in zip(sub, sub[1:])):
                best = max(best, len(sub))
        assert len(got) == best, (nums, got, best)


@test("1-D Dynamic Programming:window-dp")
def _(ns):
    f = ns["new_21_game"]
    assert abs(f(10, 1, 10) - 1.0) < 1e-9 and abs(f(6, 1, 10) - 0.6) < 1e-9 and abs(f(21, 17, 10) - 0.73278) < 1e-5
    r = random.Random(404)
    for _ in range(200):
        k, w = r.randint(0, 12), r.randint(1, 8)
        n = r.randint(0, k + w + 2)
        # model: probability of each total, O(n * w)
        p = [0.0] * (k + w + 1)
        p[0] = 1.0
        for i in range(k):
            for d in range(1, w + 1):
                p[i + d] += p[i] / w
        want = sum(p[k:n + 1]) if k > 0 else 1.0
        assert abs(f(n, k, w) - want) < 1e-9, (n, k, w)


@test("1-D Dynamic Programming:window-dp#Monotonic deque (range-max transition)")
def _(ns):
    f = ns["constrained_subset_sum"]
    assert f([10, 2, -10, 5, 20], 2) == 37 and f([-1, -2, -3], 1) == -1 and f([10, -2, -10, -5, 20], 2) == 23
    r = random.Random(405)
    for _ in range(300):
        nums = [r.randint(-9, 9) for _ in range(r.randint(1, 9))]
        k = r.randint(1, 4)
        dp = list(nums)
        for i in range(len(nums)):
            for j in range(max(0, i - k), i):
                dp[i] = max(dp[i], dp[j] + nums[i])
        assert f(nums, k) == max(dp), (nums, k)


@test("2-D Dynamic Programming:tree-dp")
def _(ns):
    f = ns["rob"]

    def build(vals, shape):
        nodes = [TreeNode(v) for v in vals]
        for i in range(1, len(nodes)):
            parent = nodes[shape[i - 1] % i]
            if parent.left is None:
                parent.left = nodes[i]
            elif parent.right is None:
                parent.right = nodes[i]
            else:  # both taken: attach below the left child's chain
                p = parent.left
                while p.left is not None:
                    p = p.left
                p.left = nodes[i]
        return nodes

    assert f(None) == 0
    r = random.Random(406)
    for _ in range(300):
        n = r.randint(1, 9)
        vals = [r.randint(0, 9) for _ in range(n)]
        nodes = build(vals, [r.randrange(100) for _ in range(n)])
        edges = [(i, j) for i, a in enumerate(nodes) for j, b in enumerate(nodes) if a.left is b or a.right is b]
        want = 0
        for mask in range(1 << n):
            if all(not (mask >> i & 1 and mask >> j & 1) for i, j in edges):
                want = max(want, sum(vals[i] for i in range(n) if mask >> i & 1))
        assert f(nodes[0]) == want, (vals, edges)


# ---- greedy (extras) ------------------------------------------------------------------------------------------------

def _is_perm_of(a, b):
    return sorted(a) == sorted(b)


@test("Greedy:kadane#Circular array")
def _(ns):
    f = ns["max_subarray_circular"]
    assert f([1, -2, 3, -2]) == 3 and f([5, -3, 5]) == 10 and f([-3, -2, -3]) == -2
    r = random.Random(190)
    for _ in range(300):
        a = [r.randint(-6, 6) for _ in range(r.randint(1, 8))]
        n = len(a)
        want = max(sum(a[(i + j) % n] for j in range(k)) for i in range(n) for k in range(1, n + 1))
        assert f(a[:]) == want, a


@test("Greedy:kadane#Maximum product")
def _(ns):
    f = ns["max_product"]
    assert f([2, 3, -2, 4]) == 6 and f([-2, 0, -1]) == 0
    r = random.Random(191)
    for _ in range(300):
        a = [r.randint(-3, 3) for _ in range(r.randint(1, 7))]
        want = max(_prod(a[i:j]) for i in range(len(a)) for j in range(i + 1, len(a) + 1))
        assert f(a[:]) == want, a


def _prod(xs):
    out = 1
    for x in xs:
        out *= x
    return out


@test("Greedy:rank-match")
def _(ns):
    f = ns["find_content_children"]
    assert f([1, 2, 3], [1, 1]) == 1 and f([1, 2], [1, 2, 3]) == 2
    r = random.Random(192)
    for _ in range(200):
        g = [r.randint(1, 5) for _ in range(r.randint(0, 5))]
        s = [r.randint(1, 5) for _ in range(r.randint(0, 5))]
        want = 0
        for k in range(min(len(g), len(s)), 0, -1):
            if any(all(a <= b for a, b in zip(sorted(cg), sorted(cs))) for cg in _it.combinations(g, k) for cs in _it.combinations(s, k)):
                want = k
                break
        assert f(g[:], s[:]) == want, (g, s)


@test("Greedy:rank-match#Pair the lightest with the heaviest")
def _(ns):
    f = ns["num_rescue_boats"]
    assert f([1, 2], 3) == 1 and f([3, 2, 2, 1], 3) == 3 and f([3, 5, 3, 4], 5) == 4
    r = random.Random(193)
    for _ in range(200):
        limit = r.randint(3, 9)
        p = [r.randint(1, limit) for _ in range(r.randint(1, 7))]

        def brute(rest):
            if not rest:
                return 0
            first, tail = rest[0], rest[1:]
            best = 1 + brute(tail)
            for i, x in enumerate(tail):
                if first + x <= limit:
                    best = min(best, 1 + brute(tail[:i] + tail[i + 1:]))
            return best

        assert f(p[:], limit) == brute(p), (p, limit)


@test("Greedy:comparator-sort")
def _(ns):
    f = ns["largest_number"]
    assert f([10, 2]) == "210" and f([3, 30, 34, 5, 9]) == "9534330" and f([0, 0]) == "0"
    r = random.Random(194)
    for _ in range(200):
        a = [r.choice([0, 1, 2, 9, 10, 11, 12, 34, 30, 3, 99]) for _ in range(r.randint(1, 6))]
        want = max("".join(map(str, p)) for p in _it.permutations(a))
        want = "0" if set(want) == {"0"} else want
        assert f(a[:]) == want, a


@test("Greedy:comparator-sort#Queue reconstruction")
def _(ns):
    f = ns["reconstruct_queue"]
    assert f([[7, 0], [4, 4], [7, 1], [5, 0], [6, 1], [5, 2]]) == [[5, 0], [7, 0], [5, 2], [6, 1], [4, 4], [7, 1]]
    r = random.Random(195)
    for _ in range(100):
        n = r.randint(1, 7)
        heights = [r.randint(1, 5) for _ in range(n)]
        order = heights[:]
        r.shuffle(order)
        people = [[h, sum(1 for x in order[:i] if x >= h)] for i, h in enumerate(order)]
        r.shuffle(people)
        got = f([p[:] for p in people])
        assert sorted(map(tuple, got)) == sorted(map(tuple, people))
        assert all(sum(1 for x in got[:i] if x[0] >= h) == k for i, (h, k) in enumerate(got))


@test("Greedy:gain-diff")
def _(ns):
    f = ns["two_city_sched_cost"]
    assert f([[10, 20], [30, 200], [400, 50], [30, 20]]) == 110
    r = random.Random(196)
    for _ in range(200):
        n = 2 * r.randint(1, 4)
        c = [[r.randint(1, 30), r.randint(1, 30)] for _ in range(n)]
        want = min(sum(c[i][0] if i in a else c[i][1] for i in range(n)) for a in _it.combinations(range(n), n // 2))
        assert f([x[:] for x in c]) == want


@test("Greedy:gain-diff#Put marbles in bags")
def _(ns):
    f = ns["put_marbles"]
    assert f([1, 3, 5, 1], 2) == 4 and f([1, 3], 2) == 0
    r = random.Random(197)
    for _ in range(200):
        w = [r.randint(1, 9) for _ in range(r.randint(1, 8))]
        k = r.randint(1, len(w))
        scores = []
        for cuts in _it.combinations(range(1, len(w)), k - 1):
            bounds = [0] + list(cuts) + [len(w)]
            scores.append(sum(w[a] + w[b - 1] for a, b in zip(bounds, bounds[1:])))
        assert f(w[:], k) == max(scores) - min(scores)


@test("Greedy:interval-stab")
def _(ns):
    f = ns["find_min_arrow_shots"]
    assert f([[10, 16], [2, 8], [1, 6], [7, 12]]) == 2 and f([[1, 2], [3, 4], [5, 6], [7, 8]]) == 4 and f([[1, 2], [2, 3], [3, 4], [4, 5]]) == 2
    r = random.Random(198)
    for _ in range(200):
        iv = []
        for _ in range(r.randint(1, 6)):
            a = r.randint(0, 8)
            iv.append([a, a + r.randint(0, 4)])
        pts = range(0, 13)
        want = min(k for k in range(1, len(iv) + 1) if any(all(any(a <= p <= b for p in ps) for a, b in iv) for ps in _it.combinations(pts, k)))
        assert f([x[:] for x in iv]) == want, iv


@test("Greedy:interval-stab#Fewest removals (keep the most)")
def _(ns):
    f = ns["erase_overlap_intervals"]
    assert f([[1, 2], [2, 3], [3, 4], [1, 3]]) == 1 and f([[1, 2], [1, 2], [1, 2]]) == 2 and f([[1, 2], [2, 3]]) == 0
    r = random.Random(199)
    for _ in range(200):
        iv = []
        for _ in range(r.randint(1, 7)):
            a = r.randint(0, 8)
            iv.append([a, a + r.randint(1, 4)])
        best = max(len(c) for k in range(len(iv) + 1) for c in _it.combinations(iv, k)
                   if all(a[1] <= b[0] or b[1] <= a[0] for a, b in _it.combinations(c, 2)))
        assert f([x[:] for x in iv]) == len(iv) - best


@test("Greedy:interval-cover")
def _(ns):
    f = ns["video_stitching"]
    assert f([[0, 2], [4, 6], [8, 10], [1, 9], [1, 5], [5, 9]], 10) == 3 and f([[0, 1], [1, 2]], 5) == -1
    r = random.Random(200)
    for _ in range(200):
        t = r.randint(1, 8)
        clips = []
        for _ in range(r.randint(1, 6)):
            a = r.randint(0, t)
            clips.append([a, min(t + 2, a + r.randint(1, 5))])

        def covers(c):
            reach = 0
            for a, b in sorted(c):
                if a > reach:
                    break
                reach = max(reach, b)
            return reach >= t

        want = next((k for k in range(1, len(clips) + 1) if any(covers(c) for c in _it.combinations(clips, k))), -1)
        assert f([x[:] for x in clips], t) == want, (clips, t)


@test("Greedy:interval-cover#Garden taps")
def _(ns):
    f = ns["min_taps"]
    assert f(5, [3, 4, 1, 1, 0, 0]) == 1 and f(3, [0, 0, 0, 0]) == -1
    r = random.Random(201)
    for _ in range(200):
        n = r.randint(1, 7)
        ranges = [r.randint(0, 3) for _ in range(n + 1)]
        want = -1
        for k in range(1, n + 2):
            ok = False
            for c in _it.combinations(range(n + 1), k):
                covered = [False] * n
                for i in c:
                    for x in range(max(0, i - ranges[i]), min(n, i + ranges[i])):
                        covered[x] = True
                if all(covered):
                    ok = True
                    break
            if ok:
                want = k
                break
        assert f(n, ranges[:]) == want, (n, ranges)


@test("Greedy:earliest-deadline")
def _(ns):
    f = ns["max_events"]
    assert f([[1, 2], [2, 3], [3, 4]]) == 3 and f([[1, 2], [2, 3], [3, 4], [1, 2]]) == 4
    r = random.Random(202)
    for _ in range(200):
        ev = []
        for _ in range(r.randint(1, 6)):
            a = r.randint(1, 6)
            ev.append([a, a + r.randint(0, 3)])
        best = 0
        for k in range(len(ev), 0, -1):
            if any(any(len(set(days)) == k for days in _it.product(*[range(a, b + 1) for a, b in c])) for c in _it.combinations(ev, k)):
                best = k
                break
        assert f([e[:] for e in ev]) == best, ev


@test("Greedy:regret-heap")
def _(ns):
    f = ns["schedule_course"]
    assert f([[100, 200], [200, 1300], [1000, 1250], [2000, 3200]]) == 3 and f([[1, 2]]) == 1 and f([[3, 2], [4, 3]]) == 0
    r = random.Random(203)
    for _ in range(200):
        c = [[r.randint(1, 5), r.randint(1, 12)] for _ in range(r.randint(1, 7))]
        best = 0
        for k in range(len(c), 0, -1):
            ok = False
            for sub in _it.combinations(c, k):
                t = 0
                good = True
                for d, dl in sorted(sub, key=lambda x: x[1]):
                    t += d
                    if t > dl:
                        good = False
                        break
                if good:
                    ok = True
                    break
            if ok:
                best = k
                break
        assert f([x[:] for x in c]) == best, c


@test("Greedy:regret-heap#Refuel stops")
def _(ns):
    f = ns["min_refuel_stops"]
    assert f(1, 1, []) == 0 and f(100, 1, [[10, 100]]) == -1 and f(100, 10, [[10, 60], [20, 30], [30, 30], [60, 40]]) == 2
    r = random.Random(204)
    for _ in range(200):
        target = r.randint(5, 30)
        pos = sorted(r.sample(range(1, target), r.randint(0, min(5, target - 1))))
        st = [[p, r.randint(1, 15)] for p in pos]
        fuel = r.randint(1, 12)
        want = -1
        for k in range(len(st) + 1):
            for sub in _it.combinations(st, k):
                tank, prev, ok = fuel, 0, True
                for p, g in list(sub) + [[target, 0]]:
                    tank -= p - prev
                    if tank < 0:
                        ok = False
                        break
                    tank += g
                    prev = p
                if ok:
                    want = k
                    break
            if want != -1:
                break
        assert f(target, fuel, [s[:] for s in st]) == want, (target, fuel, st)


@test("Greedy:regret-heap#Bricks and ladders")
def _(ns):
    f = ns["furthest_building"]
    assert f([4, 2, 7, 6, 9, 14, 12], 5, 1) == 4 and f([4, 12, 2, 7, 3, 18, 20, 3, 19], 10, 2) == 7 and f([14, 3, 19, 3], 17, 0) == 3
    r = random.Random(205)
    for _ in range(200):
        h = [r.randint(1, 9) for _ in range(r.randint(1, 8))]
        bricks, ladders = r.randint(0, 8), r.randint(0, 3)
        best = 0
        for end in range(len(h)):
            climbs = sorted((max(0, h[i + 1] - h[i]) for i in range(end)), reverse=True)
            if sum(climbs[ladders:]) <= bricks:
                best = end
        assert f(h[:], bricks, ladders) == best, (h, bricks, ladders)


@test("Greedy:unlock-best")
def _(ns):
    f = ns["find_maximized_capital"]
    assert f(2, 0, [1, 2, 3], [0, 1, 1]) == 4 and f(3, 0, [1, 2, 3], [0, 1, 2]) == 6
    r = random.Random(206)
    for _ in range(200):
        n = r.randint(1, 6)
        profits = [r.randint(0, 6) for _ in range(n)]
        capital = [r.randint(0, 8) for _ in range(n)]
        k, w = r.randint(1, 4), r.randint(0, 4)

        def best(left, w, k):
            if k == 0:
                return w
            out = w
            for i in left:
                if capital[i] <= w:
                    out = max(out, best(left - {i}, w + profits[i], k - 1))
            return out

        assert f(k, w, profits[:], capital[:]) == best(frozenset(range(n)), w, k)


def _valid_spaced(s, k=2):
    return all(s[i] != s[j] for i in range(len(s)) for j in range(i + 1, min(len(s), i + k)))


@test("Greedy:cooldown-heap")
def _(ns):
    f = ns["reorganize_string"]
    assert f("aab") in ("aba",) and f("aaab") == ""
    r = random.Random(207)
    for _ in range(300):
        s = "".join(r.choice("abc") for _ in range(r.randint(1, 8)))
        feasible = max(s.count(c) for c in set(s)) <= (len(s) + 1) // 2
        got = f(s)
        if feasible:
            assert _is_perm_of(got, s) and _valid_spaced(got), (s, got)
        else:
            assert got == "", s


@test("Greedy:cooldown-heap#Task scheduler (formula)")
def _(ns):
    f = ns["least_interval"]
    assert f(list("AAABBB"), 2) == 8 and f(list("AAABBB"), 0) == 6 and f(list("AAAAAABCDEFG"), 2) == 16
    r = random.Random(208)
    for _ in range(80):
        tasks = [r.choice("ABC") for _ in range(r.randint(1, 6))]
        n = r.randint(0, 3)
        letters = sorted(set(tasks))
        start = tuple(tasks.count(c) for c in letters)
        # breadth first over (remaining counts, time of last use): the fewest time units
        seen, frontier, t = set(), {(start, (-10,) * len(letters))}, 0
        while True:
            t += 1
            nxt = set()
            done = False
            for cnt, last in frontier:
                moves = [None] + [i for i in range(len(letters)) if cnt[i] and t - last[i] > n]
                for m in moves:
                    c2, l2 = list(cnt), list(last)
                    if m is not None:
                        c2[m] -= 1
                        l2[m] = t
                    if not any(c2):
                        done = True
                    nxt.add((tuple(c2), tuple(l2)))
            if done:
                break
            frontier = nxt
        assert f(tasks[:], n) == t, (tasks, n)


@test("Greedy:jump-bfs")
def _(ns):
    f = ns["can_reach"]
    assert f([4, 2, 3, 0, 3, 1, 2], 5) is True and f([3, 0, 2, 1, 2], 2) is False
    r = random.Random(209)
    for _ in range(300):
        a = [r.randint(0, 4) for _ in range(r.randint(1, 8))]
        s = r.randrange(len(a))
        adj = {i: [j for j in (i + a[i], i - a[i]) if 0 <= j < len(a)] for i in range(len(a))}
        seen, st = {s}, [s]
        while st:
            u = st.pop()
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    st.append(v)
        assert f(a[:], s) is any(a[i] == 0 for i in seen)


@test("Greedy:jump-bfs#Jump game IV (equal values teleport)")
def _(ns):
    f = ns["min_jumps"]
    assert f([100, -23, -23, 404, 100, 23, 23, 23, 3, 404]) == 3 and f([7]) == 0 and f([7, 6, 9, 6, 9, 6, 9, 7]) == 1
    r = random.Random(210)
    for _ in range(200):
        a = [r.randint(0, 3) for _ in range(r.randint(1, 9))]
        n = len(a)
        dist = {0: 0}
        q = [0]
        for u in q:
            for v in [u - 1, u + 1] + [j for j in range(n) if a[j] == a[u]]:
                if 0 <= v < n and v not in dist:
                    dist[v] = dist[u] + 1
                    q.append(v)
        assert f(a[:]) == dist[n - 1], a


@test("Greedy:reach-number")
def _(ns):
    f = ns["reach_number"]
    assert f(2) == 3 and f(3) == 2 and f(-2) == 3 and f(0) == 0
    for target in range(-25, 26):
        reach, k = {0}, 0
        while target not in reach:
            k += 1
            reach = {x + s * k for x in reach for s in (1, -1)}
        assert f(target) == k, target


@test("Greedy:reach-number#Broken calculator (work backwards)")
def _(ns):
    f = ns["broken_calc"]
    assert f(2, 3) == 2 and f(5, 8) == 2 and f(3, 10) == 3 and f(1024, 1) == 1023
    for start in range(1, 12):
        for target in range(1, 40):
            dist, q = {start: 0}, [start]
            for u in q:
                for v in (u * 2, u - 1):
                    if 1 <= v <= 100 and v not in dist:
                        dist[v] = dist[u] + 1
                        q.append(v)
            assert f(start, target) == dist[target], (start, target)


@test("Greedy:jump-window")
def _(ns):
    f = ns["max_result"]
    assert f([1, -1, -2, 4, -7, 3], 2) == 7 and f([10, -5, -2, 4, 0, 3], 3) == 17 and f([1, -5, -20, 4, -1, 3, -6, -3], 2) == 0
    r = random.Random(211)
    for _ in range(300):
        a = [r.randint(-9, 9) for _ in range(r.randint(1, 10))]
        k = r.randint(1, 4)
        best = [0] * len(a)
        best[0] = a[0]
        for i in range(1, len(a)):
            best[i] = a[i] + max(best[j] for j in range(max(0, i - k), i))
        assert f(a[:], k) == best[-1], (a, k)


@test("Greedy:min-start")
def _(ns):
    f = ns["min_start_value"]
    assert f([-3, 2, -3, 4, 2]) == 5 and f([1, 2]) == 1 and f([1, -2, -3]) == 5
    r = random.Random(212)
    for _ in range(200):
        a = [r.randint(-6, 6) for _ in range(r.randint(1, 8))]
        s = 1
        while True:
            t, ok = s, True
            for x in a:
                t += x
                if t < 1:
                    ok = False
            if ok:
                break
            s += 1
        assert f(a[:]) == s


@test("Greedy:min-start#Minimum initial energy (order by gap)")
def _(ns):
    f = ns["minimum_effort"]
    assert f([[1, 2], [2, 4], [4, 8]]) == 8 and f([[1, 3], [2, 4], [10, 11], [10, 12], [8, 9]]) == 32
    r = random.Random(213)
    for _ in range(200):
        tasks = []
        for _ in range(r.randint(1, 5)):
            a = r.randint(1, 6)
            tasks.append([a, a + r.randint(0, 5)])
        best = min(max(max(0, 0), 0) or _need(p) for p in _it.permutations(tasks))
        assert f([t[:] for t in tasks]) == best, tasks


def _need(order):
    """Smallest starting energy for the tasks done in this order."""
    need = 0
    spent = 0
    for actual, minimum in order:
        need = max(need, spent + minimum)
        spent += actual
    return need


@test("Greedy:two-end-tokens")
def _(ns):
    f = ns["bag_of_tokens_score"]
    assert f([100], 50) == 0 and f([100, 200], 150) == 1 and f([100, 200, 300, 400], 200) == 2
    r = random.Random(214)
    for _ in range(200):
        t = [r.randint(1, 9) for _ in range(r.randint(0, 6))]
        p = r.randint(0, 12)

        def best(used, power, score):
            out = score
            for i in range(len(t)):
                if i in used:
                    continue
                if power >= t[i]:
                    out = max(out, best(used | {i}, power - t[i], score + 1))
                if score > 0:
                    out = max(out, best(used | {i}, power + t[i], score - 1))
            return out

        assert f(t[:], p) == best(frozenset(), p, 0), (t, p)


@test("Greedy:best-pair-running")
def _(ns):
    f = ns["max_score_sightseeing_pair"]
    assert f([8, 1, 5, 2, 6]) == 11 and f([1, 2]) == 2
    r = random.Random(215)
    for _ in range(200):
        a = [r.randint(1, 20) for _ in range(r.randint(2, 9))]
        assert f(a[:]) == max(a[i] + a[j] + i - j for i in range(len(a)) for j in range(i + 1, len(a)))


def _stock_best(prices, fee=0, cooldown=0, k=None):
    """Exhaustive: every sequence of actions, day by day."""
    n = len(prices)

    def go(day, holding, rest, left):
        if day == n:
            return 0
        best = go(day + 1, holding, max(0, rest - 1), left)  # do nothing
        if holding:
            best = max(best, prices[day] - fee + go(day + 1, False, cooldown, left))
        elif rest == 0 and (left is None or left > 0):
            best = max(best, -prices[day] + go(day + 1, True, 0, None if left is None else left - 1))
        return best

    return go(0, False, 0, k)


@test("Greedy:stock-states")
def _(ns):
    f = ns["max_profit_fee"]
    assert f([1, 3, 2, 8, 4, 9], 2) == 8 and f([1, 3, 7, 5, 10, 3], 3) == 6
    r = random.Random(216)
    for _ in range(150):
        p = [r.randint(1, 12) for _ in range(r.randint(1, 8))]
        fee = r.randint(0, 4)
        assert f(p[:], fee) == _stock_best(p, fee=fee), (p, fee)


@test("Greedy:stock-states#With a cooldown")
def _(ns):
    f = ns["max_profit_cooldown"]
    assert f([1, 2, 3, 0, 2]) == 3 and f([1]) == 0
    r = random.Random(217)
    for _ in range(150):
        p = [r.randint(1, 12) for _ in range(r.randint(1, 8))]
        assert f(p[:]) == _stock_best(p, cooldown=1), p


@test("Greedy:stock-states#At most k transactions")
def _(ns):
    f = ns["max_profit_k"]
    assert f(2, [2, 4, 1]) == 2 and f(2, [3, 2, 6, 5, 0, 3]) == 7 and f(2, [3, 3, 5, 0, 0, 3, 1, 4]) == 6
    r = random.Random(218)
    for _ in range(150):
        p = [r.randint(1, 12) for _ in range(r.randint(1, 8))]
        k = r.randint(1, 3)
        assert f(k, p[:]) == _stock_best(p, k=k), (k, p)


@test("Greedy:weighted-intervals")
def _(ns):
    f = ns["job_scheduling"]
    assert f([1, 2, 3, 3], [3, 4, 5, 6], [50, 10, 40, 70]) == 120 and f([1, 1, 1], [2, 3, 4], [5, 6, 4]) == 6
    r = random.Random(219)
    for _ in range(200):
        jobs = []
        for _ in range(r.randint(1, 7)):
            a = r.randint(1, 8)
            jobs.append((a, a + r.randint(1, 4), r.randint(1, 9)))
        best = max(sum(j[2] for j in c) for k in range(len(jobs) + 1) for c in _it.combinations(jobs, k)
                   if all(a[1] <= b[0] or b[1] <= a[0] for a, b in _it.combinations(c, 2)))
        s, e, p = zip(*jobs)
        assert f(list(s), list(e), list(p)) == best, jobs


@test("Greedy:knapsack-01")
def _(ns):
    f = ns["can_partition"]
    assert f([1, 5, 11, 5]) is True and f([1, 2, 3, 5]) is False and f([2]) is False
    r = random.Random(220)
    for _ in range(300):
        a = [r.randint(1, 9) for _ in range(r.randint(1, 9))]
        total = sum(a)
        want = total % 2 == 0 and any(sum(c) == total // 2 for k in range(len(a) + 1) for c in _it.combinations(a, k))
        assert f(a[:]) is want, a


@test("Greedy:knapsack-01#Count the ways (target sum)")
def _(ns):
    f = ns["find_target_sum_ways"]
    assert f([1, 1, 1, 1, 1], 3) == 5 and f([1], 1) == 1
    r = random.Random(221)
    for _ in range(200):
        a = [r.randint(0, 5) for _ in range(r.randint(1, 7))]
        t = r.randint(-8, 8)
        want = sum(1 for signs in _it.product((1, -1), repeat=len(a)) if sum(s * x for s, x in zip(signs, a)) == t)
        assert f(a[:], t) == want


@test("Greedy:wildcard")
def _(ns):
    import re
    f = ns["is_match"]
    assert f("aa", "a") is False and f("aa", "*") is True and f("cb", "?a") is False and f("adceb", "*a*b") is True
    r = random.Random(222)
    for _ in range(600):
        s = "".join(r.choice("ab") for _ in range(r.randint(0, 7)))
        p = "".join(r.choice("ab?*") for _ in range(r.randint(0, 7)))
        rx = "".join("." if c == "?" else ".*" if c == "*" else c for c in p)
        assert f(s, p) is (re.fullmatch(rx, s) is not None), (s, p)


@test("Greedy:remove-k-digits")
def _(ns):
    f = ns["remove_k_digits"]
    assert f("1432219", 3) == "1219" and f("10200", 1) == "200" and f("10", 2) == "0"
    r = random.Random(223)
    for _ in range(300):
        num = "".join(r.choice("0123") for _ in range(r.randint(1, 7)))
        k = r.randint(0, len(num))
        keep = len(num) - k
        want = str(min(int("".join(c) or "0") for c in _it.combinations(num, keep)))
        assert f(num, k) == want, (num, k)


@test("Greedy:remove-k-digits#Remove duplicate letters")
def _(ns):
    f = ns["remove_duplicate_letters"]
    assert f("bcabc") == "abc" and f("cbacdcbc") == "acdb"
    r = random.Random(224)
    for _ in range(200):
        s = "".join(r.choice("abcd") for _ in range(r.randint(1, 8)))
        letters = set(s)
        want = min("".join(c) for k in range(len(letters), len(letters) + 1) for c in _it.combinations(s, k) if set(c) == letters)
        assert f(s) == want, s


@test("Greedy:remove-k-digits#Most competitive subsequence")
def _(ns):
    f = ns["most_competitive"]
    assert f([3, 5, 2, 6], 2) == [2, 6] and f([2, 4, 3, 3, 5, 4, 9, 6], 4) == [2, 3, 3, 4]
    r = random.Random(225)
    for _ in range(200):
        a = [r.randint(1, 6) for _ in range(r.randint(1, 8))]
        k = r.randint(1, len(a))
        assert f(a[:], k) == list(min(_it.combinations(a, k))), (a, k)


def _bal(s):
    d = 0
    for ch in s:
        d += 1 if ch == "(" else -1
        if d < 0:
            return False
    return d == 0


def _fewest_insertions(s, valid, limit=7):
    seen, frontier = {s}, {s}
    for depth in range(limit + 1):
        if any(valid(t) for t in frontier):
            return depth
        nxt = set()
        for t in frontier:
            for i in range(len(t) + 1):
                for ch in "()":
                    u = t[:i] + ch + t[i:]
                    if u not in seen:
                        seen.add(u)
                        nxt.add(u)
        frontier = nxt
    return None


@test("Greedy:bracket-repair")
def _(ns):
    f = ns["min_add_to_make_valid"]
    assert f("())") == 1 and f("(((") == 3 and f("()") == 0
    r = random.Random(226)
    for _ in range(150):
        s = "".join(r.choice("()") for _ in range(r.randint(0, 6)))
        assert f(s) == _fewest_insertions(s, _bal), s


@test("Greedy:bracket-repair#Each ( needs two )")
def _(ns):
    f = ns["min_insertions"]
    assert f("(()))") == 1 and f("())") == 0 and f("))())(") == 3 and f("((((((") == 12

    def valid2(t):  # every ( is closed by exactly two ) later on
        i, stack = 0, 0
        while i < len(t):
            if t[i] == "(":
                stack += 1
                i += 1
            else:
                if t[i:i + 2] != "))" or stack == 0:
                    return False
                stack -= 1
                i += 2
        return stack == 0

    r = random.Random(227)
    for _ in range(100):
        s = "".join(r.choice("()") for _ in range(r.randint(0, 4)))
        assert f(s) == _fewest_insertions(s, valid2, 9), s


@test("Greedy:create-maximum")
def _(ns):
    f = ns["max_number"]
    assert f([3, 4, 6, 5], [9, 1, 2, 5, 8, 3], 5) == [9, 8, 6, 5, 3] and f([6, 7], [6, 0, 4], 5) == [6, 7, 6, 0, 4]
    r = random.Random(228)

    def merges(a, b):
        if not a:
            yield list(b)
            return
        if not b:
            yield list(a)
            return
        for rest in merges(a[1:], b):
            yield [a[0]] + rest
        for rest in merges(a, b[1:]):
            yield [b[0]] + rest

    for _ in range(80):
        a = [r.randint(0, 9) for _ in range(r.randint(1, 4))]
        b = [r.randint(0, 9) for _ in range(r.randint(1, 4))]
        k = r.randint(1, len(a) + len(b))
        want = max(m for i in range(0, k + 1) if i <= len(a) and k - i <= len(b)
                   for ca in _it.combinations(a, i) for cb in _it.combinations(b, k - i)
                   for m in merges(list(ca), list(cb)))
        assert f(a[:], b[:], k) == want, (a, b, k)


@test("Greedy:di-string")
def _(ns):
    f = ns["di_string_match"]
    for pat in ("IDID", "III", "DDI", "", "D", "IIDDI"):
        got = f(pat)
        assert sorted(got) == list(range(len(pat) + 1))
        assert all((got[i] < got[i + 1]) == (c == "I") for i, c in enumerate(pat)), pat


@test("Greedy:di-string#Smallest number from the pattern")
def _(ns):
    f = ns["smallest_number"]
    assert f("IIIDIDDD") == "123549876" and f("DDD") == "4321"
    r = random.Random(229)
    for _ in range(200):
        pat = "".join(r.choice("ID") for _ in range(r.randint(1, 7)))
        want = min("".join(map(str, p)) for p in _it.permutations(range(1, len(pat) + 2))
                   if all((p[i] < p[i + 1]) == (c == "I") for i, c in enumerate(pat)))
        assert f(pat) == want, pat


@test("Greedy:break-palindrome")
def _(ns):
    f = ns["break_palindrome"]
    assert f("abccba") == "aaccba" and f("a") == "" and f("aa") == "ab" and f("aba") == "abb"
    r = random.Random(230)
    for _ in range(200):
        half = "".join(r.choice("abc") for _ in range(r.randint(1, 4)))
        p = half + (r.choice("abc") if r.random() < 0.5 else "") + half[::-1]
        cands = [p[:i] + c + p[i + 1:] for i in range(len(p)) for c in "abcdefghijklmnopqrstuvwxyz" if c != p[i]]
        cands = [c for c in cands if c != c[::-1]]
        assert f(p) == (min(cands) if cands else ""), p


@test("Greedy:parity-sort")
def _(ns):
    f = ns["largest_integer"]
    assert f(1234) == 3412 and f(65875) == 87655
    r = random.Random(231)
    for _ in range(200):
        num = r.randint(1, 99999)
        digits = list(str(num))
        best = 0
        for p in set(_it.permutations(digits)):
            if all((int(a) % 2) == (int(b) % 2) for a, b in zip(p, digits)):
                best = max(best, int("".join(p)))
        assert f(num) == best


@test("Greedy:digit-sum-target")
def _(ns):
    f = ns["make_integer_beautiful"]
    assert f(16, 6) == 4 and f(467, 6) == 33 and f(1, 1) == 0
    r = random.Random(232)
    for _ in range(300):
        n = r.randint(1, 5000)
        t = r.randint(1, 20)
        x = 0
        while sum(map(int, str(n + x))) > t:
            x += 1
        assert f(n, t) == x, (n, t)


@test("Greedy:cut-when-forced")
def _(ns):
    f = ns["partition_string"]
    assert f("abacaba") == 4 and f("ssssss") == 6 and f("abc") == 1
    r = random.Random(233)
    for _ in range(200):
        s = "".join(r.choice("abc") for _ in range(r.randint(1, 9)))
        want = min(len(parts) for mask in range(1 << (len(s) - 1))
                   for parts in [[s[a:b] for a, b in zip([0] + [i + 1 for i in range(len(s) - 1) if mask >> i & 1],
                                                          [i + 1 for i in range(len(s) - 1) if mask >> i & 1] + [len(s)])]]
                   if all(len(set(x)) == len(x) for x in parts))
        assert f(s) == want, s


@test("Greedy:cut-when-forced#Range at most k (sort first)")
def _(ns):
    f = ns["partition_array"]
    assert f([3, 6, 1, 2, 5], 2) == 2 and f([1, 2, 3], 1) == 2 and f([2, 2, 4, 5], 0) == 3
    r = random.Random(234)
    for _ in range(200):
        a = [r.randint(0, 9) for _ in range(r.randint(1, 7))]
        k = r.randint(0, 4)
        best = len(a)

        def go(i, groups):
            nonlocal best
            if len(groups) >= best:
                return
            if i == len(a):
                best = len(groups)
                return
            for g in groups:
                if max(g + [a[i]]) - min(g + [a[i]]) <= k:
                    g.append(a[i])
                    go(i + 1, groups)
                    g.pop()
            groups.append([a[i]])
            go(i + 1, groups)
            groups.pop()

        go(0, [])
        assert f(a[:], k) == best, (a, k)


@test("Greedy:two-pass")
def _(ns):
    f = ns["candy"]
    assert f([1, 0, 2]) == 5 and f([1, 2, 2]) == 4 and f([1]) == 1
    r = random.Random(235)
    for _ in range(300):
        a = [r.randint(1, 5) for _ in range(r.randint(1, 7))]
        c = [1] * len(a)
        changed = True
        while changed:  # the fixed point of the rules
            changed = False
            for i in range(len(a)):
                for j in (i - 1, i + 1):
                    if 0 <= j < len(a) and a[i] > a[j] and c[i] <= c[j]:
                        c[i] = c[j] + 1
                        changed = True
        assert f(a[:]) == sum(c), a


@test("Greedy:two-pass#Distance to the nearest target")
def _(ns):
    f = ns["shortest_to_char"]
    assert f("loveleetcode", "e") == [3, 2, 1, 0, 1, 0, 0, 1, 2, 2, 1, 0] and f("aaab", "b") == [3, 2, 1, 0]
    r = random.Random(236)
    for _ in range(200):
        s = "".join(r.choice("abc") for _ in range(r.randint(1, 9)))
        if "a" not in s:
            continue
        assert f(s, "a") == [min(abs(i - j) for j in range(len(s)) if s[j] == "a") for i in range(len(s))]


@test("Greedy:two-pass#Longest mountain (runs)")
def _(ns):
    f = ns["longest_mountain"]
    assert f([2, 1, 4, 7, 3, 2, 5]) == 5 and f([2, 2, 2]) == 0 and f([1, 2, 3]) == 0
    r = random.Random(237)
    for _ in range(300):
        a = [r.randint(0, 4) for _ in range(r.randint(1, 10))]
        best = 0
        for i in range(len(a)):
            for j in range(i + 2, len(a)):
                seg = a[i:j + 1]
                peak = seg.index(max(seg))
                if 0 < peak < len(seg) - 1 and all(seg[k] < seg[k + 1] for k in range(peak)) \
                        and all(seg[k] > seg[k + 1] for k in range(peak, len(seg) - 1)):
                    best = max(best, len(seg))
        assert f(a[:]) == best, a


@test("Greedy:palindrome-counts")
def _(ns):
    f = ns["longest_palindrome"]
    assert f("abccccdd") == 7 and f("a") == 1 and f("aaaa") == 4
    r = random.Random(238)
    for _ in range(200):
        s = "".join(r.choice("abcd") for _ in range(r.randint(1, 8)))
        best = 0
        for k in range(len(s) + 1):
            for c in _it.combinations(s, k):
                if sum(1 for x in set(c) if c.count(x) % 2) <= 1:
                    best = max(best, k)
        assert f(s) == best, s


@test("Greedy:distinct-frequencies")
def _(ns):
    f = ns["min_deletions"]
    assert f("aab") == 0 and f("aaabbbcc") == 2 and f("ceabaacb") == 2
    r = random.Random(239)
    for _ in range(200):
        s = "".join(r.choice("abcd") for _ in range(r.randint(1, 8)))
        letters = sorted(set(s))
        cnt = [s.count(c) for c in letters]
        best = len(s)
        for keep in _it.product(*[range(c + 1) for c in cnt]):
            pos = [k for k in keep if k]
            if len(pos) == len(set(pos)):
                best = min(best, sum(cnt) - sum(keep))
        assert f(s) == best, s


@test("Greedy:split-2-3")
def _(ns):
    f = ns["minimum_rounds"]
    assert f([2, 2, 3, 3, 2, 4, 4, 4, 4, 4]) == 4 and f([2, 3, 3]) == -1
    for c in range(2, 30):
        want = min(a + b for a in range(c // 2 + 1) for b in range(c // 3 + 1) if 2 * a + 3 * b == c)
        assert f([7] * c) == want, c


@test("Greedy:bucket-freq")
def _(ns):
    f = ns["frequency_sort"]
    r = random.Random(240)
    for _ in range(200):
        s = "".join(r.choice("abcde") for _ in range(r.randint(0, 12)))
        got = f(s)
        assert _is_perm_of(got, s)
        runs = [(ch, len(list(g))) for ch, g in _it.groupby(got)]
        assert len({ch for ch, _ in runs}) == len(runs)  # equal letters stay together
        counts = [n for _, n in runs]
        assert counts == sorted(counts, reverse=True)


@test("Greedy:bucket-freq#H-index")
def _(ns):
    f = ns["h_index"]
    assert f([3, 0, 6, 1, 5]) == 3 and f([1, 3, 1]) == 1 and f([100]) == 1 and f([0]) == 0
    r = random.Random(241)
    for _ in range(300):
        c = [r.randint(0, 8) for _ in range(r.randint(1, 8))]
        assert f(c[:]) == max(h for h in range(len(c) + 1) if sum(1 for x in c if x >= h) >= h)


@test("Greedy:residue-counts")
def _(ns):
    f = ns["can_arrange"]
    assert f([1, 2, 3, 4, 5, 10, 6, 7, 8, 9], 5) is True and f([1, 2, 3, 4, 5, 6], 7) is True and f([1, 2, 3, 4, 5, 6], 10) is False
    r = random.Random(242)

    def brute(a, k):
        if not a:
            return True
        first, rest = a[0], a[1:]
        return any((first + x) % k == 0 and brute(rest[:i] + rest[i + 1:], k) for i, x in enumerate(rest))

    for _ in range(300):
        k = r.randint(2, 6)
        a = [r.randint(-9, 9) for _ in range(2 * r.randint(0, 4))]
        assert f(a[:], k) is brute(a, k), (a, k)


@test("Greedy:residue-counts#Smallest missing value (MEX)")
def _(ns):
    f = ns["find_smallest_integer"]
    assert f([1, -10, 7, 13, 6, 8], 5) == 4 and f([1, -10, 7, 13, 6, 8], 7) == 2
    r = random.Random(243)
    for _ in range(200):
        v = r.randint(1, 5)
        a = [r.randint(-9, 9) for _ in range(r.randint(0, 8))]
        m = 0
        pool = [x % v for x in a]
        while m % v in pool:
            pool.remove(m % v)
            m += 1
        assert f(a[:], v) == m


@test("Greedy:highest-bit")
def _(ns):
    f = ns["find_maximum_xor"]
    assert f([3, 10, 5, 25, 2, 8]) == 28 and f([14, 70, 53, 83, 49, 91, 36, 80, 92, 51, 66, 70]) == 127 and f([0]) == 0
    r = random.Random(244)
    for _ in range(300):
        a = [r.randint(0, 200) for _ in range(r.randint(1, 8))]
        assert f(a[:]) == max(x ^ y for x in a for y in a)


@test("Greedy:bit-decisions")
def _(ns):
    f = ns["min_flips"]
    assert f(2, 6, 5) == 3 and f(4, 2, 7) == 1 and f(1, 2, 3) == 0
    r = random.Random(245)
    for _ in range(300):
        a, b, c = r.randint(1, 63), r.randint(1, 63), r.randint(1, 63)
        want = bin((a | b) ^ c).count("1")  # a lower bound ...
        best = min(bin(a ^ x).count("1") + bin(b ^ y).count("1") for x in range(64) for y in range(64) if x | y == c) if c < 64 else want
        assert f(a, b, c) == best, (a, b, c)


@test("Greedy:bit-decisions#Reduce to zero by adding or removing powers of two")
def _(ns):
    f = ns["min_operations"]
    assert f(39) == 3 and f(54) == 3 and f(1) == 1
    dist, q = {0: 0}, [0]
    for u in q:
        for p in range(10):
            for v in (u + (1 << p), u - (1 << p)):
                if 0 <= v <= 2000 and v not in dist:
                    dist[v] = dist[u] + 1
                    q.append(v)
    for n in range(1, 300):
        assert f(n) == dist[n], n


@test("Greedy:cash-counts")
def _(ns):
    f = ns["lemonade_change"]
    assert f([5, 5, 5, 10, 20]) is True and f([5, 5, 10, 10, 20]) is False and f([10]) is False
    r = random.Random(246)
    for _ in range(300):
        bills = [r.choice([5, 5, 10, 20]) for _ in range(r.randint(1, 8))]

        def go(i, fives, tens):
            if fives < 0 or tens < 0:
                return False
            if i == len(bills):
                return True
            b = bills[i]
            if b == 5:
                return go(i + 1, fives + 1, tens)
            if b == 10:
                return go(i + 1, fives - 1, tens + 1)
            return go(i + 1, fives - 1, tens - 1) or go(i + 1, fives - 3, tens)

        assert f(bills[:]) is go(0, 0, 0), bills


@test("Greedy:positive-differences")
def _(ns):
    f = ns["min_number_operations"]
    assert f([1, 2, 3, 2, 1]) == 3 and f([3, 1, 5, 4, 2]) == 7 and f([1, 1, 1, 1]) == 1
    r = random.Random(247)
    for _ in range(60):
        t = tuple(r.randint(0, 3) for _ in range(r.randint(1, 4)))
        dist, q = {(0,) * len(t): 0}, [(0,) * len(t)]
        for u in q:
            for i in range(len(t)):
                for j in range(i, len(t)):
                    v = tuple(x + 1 if i <= k <= j else x for k, x in enumerate(u))
                    if all(a <= 3 for a in v) and v not in dist:
                        dist[v] = dist[u] + 1
                        q.append(v)
        assert f(list(t)) == dist[t], t


@test("Greedy:pair-double")
def _(ns):
    f = ns["can_reorder_doubled"]
    assert f([3, 1, 3, 6]) is False and f([2, 1, 2, 6]) is False and f([4, -2, 2, -4]) is True and f([0, 0]) is True and f([0]) is False
    r = random.Random(248)

    def brute(a):
        if not a:
            return True
        x, rest = a[0], a[1:]
        return any(y == 2 * x and brute(rest[:i] + rest[i + 1:]) for i, y in enumerate(rest)) or \
            any(x == 2 * y and brute(rest[:i] + rest[i + 1:]) for i, y in enumerate(rest))

    for _ in range(300):
        a = [r.choice([-4, -2, -1, 0, 1, 2, 4, 8]) for _ in range(2 * r.randint(0, 3))]
        assert f(a[:]) is brute(a), a


@test("Greedy:window-subtract")
def _(ns):
    f = ns["check_array"]
    assert f([2, 2, 3, 1, 1, 0], 3) is True and f([1, 3, 1, 1], 2) is False
    r = random.Random(249)
    for _ in range(300):
        a = [r.randint(0, 3) for _ in range(r.randint(1, 6))]
        k = r.randint(1, 3)
        seen = {}

        def go(t):
            if not any(t):
                return True
            if t in seen:
                return seen[t]
            ok = False
            for i in range(len(t) - k + 1):
                if all(t[i + j] > 0 for j in range(k)):
                    nt = tuple(x - 1 if i <= p < i + k else x for p, x in enumerate(t))
                    if go(nt):
                        ok = True
                        break
            seen[t] = ok
            return ok

        assert f(a[:], k) is go(tuple(a)), (a, k)


@test("Greedy:two-largest")
def _(ns):
    f = ns["fill_cups"]
    assert f([1, 4, 2]) == 4 and f([5, 4, 4]) == 7 and f([5, 0, 0]) == 5
    r = random.Random(250)
    for _ in range(100):
        a = [r.randint(0, 5) for _ in range(3)]
        dist, q = {tuple(a): 0}, [tuple(a)]
        for u in q:
            for i in range(3):
                for j in range(i, 3):
                    v = list(u)
                    v[i] = max(0, v[i] - 1)
                    if j != i:
                        v[j] = max(0, v[j] - 1)
                    v = tuple(v)
                    if v not in dist:
                        dist[v] = dist[u] + 1
                        q.append(v)
        assert f(a[:]) == dist[(0, 0, 0)], a


@test("Greedy:two-largest#Stones (three piles)")
def _(ns):
    f = ns["maximum_score"]
    assert f(2, 4, 6) == 6 and f(4, 4, 6) == 7 and f(1, 8, 8) == 8
    r = random.Random(251)
    for _ in range(100):
        a, b, c = r.randint(0, 6), r.randint(0, 6), r.randint(0, 6)

        def go(x, y, z):
            best = 0
            for i, j in ((0, 1), (0, 2), (1, 2)):
                v = [x, y, z]
                if v[i] and v[j]:
                    v[i] -= 1
                    v[j] -= 1
                    best = max(best, 1 + go(*v))
            return best

        assert f(a, b, c) == go(a, b, c)


@test("Greedy:two-largest#Halve the array sum (heap)")
def _(ns):
    f = ns["halve_array"]
    assert f([5, 19, 8, 1]) == 3 and f([3, 8, 20]) == 3
    r = random.Random(252)
    for _ in range(100):
        a = [r.randint(1, 20) for _ in range(r.randint(1, 4))]
        half = sum(a) / 2
        dist = {tuple(a): 0}
        q = [tuple(float(x) for x in a)]
        dist = {q[0]: 0}
        ans = None
        for u in q:
            if sum(u) <= half + 1e-9:
                ans = dist[u]
                break
            for i in range(len(u)):
                v = list(u)
                v[i] /= 2
                v = tuple(v)
                if v not in dist:
                    dist[v] = dist[u] + 1
                    q.append(v)
        assert f(a[:]) == ans, a


@test("Greedy:leaves-first")
def _(ns):
    f = ns["min_camera_cover"]

    def tree(vals):
        return _tree(vals)

    assert f(tree([0, 0, None, 0, 0])) == 1 and f(tree([0, 0, None, 0, None, 0, None, None, 0])) == 2
    r = random.Random(253)
    for _ in range(100):
        n = r.randint(1, 8)
        nodes = [TreeNode(0) for _ in range(n)]
        parent = {}
        for i in range(1, n):
            while True:
                p = r.randrange(i)
                side = r.choice(("left", "right"))
                if getattr(nodes[p], side) is None:
                    setattr(nodes[p], side, nodes[i])
                    parent[i] = p
                    break
        best = n
        for k in range(1, n + 1):
            for cams in _it.combinations(range(n), k):
                cov = set()
                for c in cams:
                    cov.add(c)
                    if c in parent:
                        cov.add(parent[c])
                    for ch in (nodes[c].left, nodes[c].right):
                        if ch is not None:
                            cov.add(nodes.index(ch))
                if len(cov) == n:
                    best = k
                    break
            else:
                continue
            break
        assert f(nodes[0]) == best


@test("Greedy:leaves-first#Distribute coins (excess flows up)")
def _(ns):
    f = ns["distribute_coins"]
    assert f(_tree([3, 0, 0])) == 2 and f(_tree([0, 3, 0])) == 3 and f(_tree([1, 0, 2])) == 2
    r = random.Random(254)
    for _ in range(60):
        n = r.randint(1, 5)
        nodes = [TreeNode(0) for _ in range(n)]
        edges = []
        for i in range(1, n):
            while True:
                p = r.randrange(i)
                side = r.choice(("left", "right"))
                if getattr(nodes[p], side) is None:
                    setattr(nodes[p], side, nodes[i])
                    edges.append((p, i))
                    break
        coins = [0] * n
        for _ in range(n):
            coins[r.randrange(n)] += 1
        for nd, c in zip(nodes, coins):
            nd.val = c
        start = tuple(coins)
        goal = (1,) * n
        dist, q = {start: 0}, [start]
        for u in q:
            if u == goal:
                break
            for a, b in edges:
                for x, y in ((a, b), (b, a)):
                    if u[x] > 0:
                        v = list(u)
                        v[x] -= 1
                        v[y] += 1
                        v = tuple(v)
                        if v not in dist:
                            dist[v] = dist[u] + 1
                            q.append(v)
        assert f(nodes[0]) == dist[goal], (coins, edges)
