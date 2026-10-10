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


# ---- intervals (extras) ---------------------------------------------------------------------------------------------

def _merge_pairs(iv):
    out = []
    for s, e in sorted(iv):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out


@test("Intervals:merge#Insert an interval")
def _(ns):
    f = ns["insert"]
    assert f([[1, 3], [6, 9]], [2, 5]) == [[1, 5], [6, 9]] and f([], [5, 7]) == [[5, 7]]
    r = random.Random(300)
    for _ in range(300):
        pts = sorted(r.sample(range(0, 30), 2 * r.randint(0, 5)))
        iv = [[pts[i], pts[i + 1]] for i in range(0, len(pts), 2)]
        a = r.randint(0, 28)
        new = [a, a + r.randint(0, 5)]
        assert f([x[:] for x in iv], new[:]) == _merge_pairs(iv + [new])


@test("Intervals:merge#Count groups of overlapping ranges")
def _(ns):
    f = ns["count_ways"]
    assert f([[6, 10], [5, 15]]) == 2 and f([[1, 3], [10, 20], [2, 5], [4, 8]]) == 4
    r = random.Random(301)
    for _ in range(200):
        iv = []
        for _ in range(r.randint(1, 7)):
            a = r.randint(0, 15)
            iv.append([a, a + r.randint(0, 4)])
        parent = list(range(len(iv)))

        def find(x):
            while parent[x] != x:
                x = parent[x]
            return x

        for i in range(len(iv)):
            for j in range(i):
                if iv[i][0] <= iv[j][1] and iv[j][0] <= iv[i][1]:
                    parent[find(i)] = find(j)
        comps = len({find(i) for i in range(len(iv))})
        assert f([x[:] for x in iv]) == 2**comps


class _CalendarBrute:
    def __init__(self):
        self.b = []

    def book(self, s, e):
        self.b.append((s, e))
        t = sorted({x for iv in self.b for x in iv})
        return max((sum(1 for a, c in self.b if a <= x < c) for x in t), default=0)


@test("Intervals:calendar#At most two at once")
def _(ns):
    r = random.Random(302)
    for _ in range(100):
        cal, mine = ns["MyCalendarTwo"](), []
        for _ in range(r.randint(1, 10)):
            s = r.randint(0, 12)
            e = s + r.randint(1, 5)
            ok = all(sum(1 for a, c in mine if a <= x < c) < 2 for x in range(s, e))
            assert cal.book(s, e) is ok
            if ok:
                mine.append((s, e))


@test("Intervals:calendar#Largest overlap so far")
def _(ns):
    r = random.Random(303)
    for _ in range(100):
        cal, brute = ns["MyCalendarThree"](), _CalendarBrute()
        for _ in range(r.randint(1, 10)):
            s = r.randint(0, 12)
            e = s + r.randint(1, 5)
            assert cal.book(s, e) == brute.book(s, e)


@test("Intervals:intersect")
def _(ns):
    f = ns["interval_intersection"]
    assert f([[0, 2], [5, 10], [13, 23], [24, 25]], [[1, 5], [8, 12], [15, 24], [25, 26]]) == [[1, 2], [5, 5], [8, 10], [15, 23], [24, 24], [25, 25]]
    r = random.Random(304)

    def gen():
        pts = sorted(r.sample(range(0, 40), 2 * r.randint(0, 5)))
        return [[pts[i], pts[i + 1]] for i in range(0, len(pts), 2)]

    for _ in range(200):
        a, b = gen(), gen()
        want = _merge_pairs([[x, x] for x in range(0, 41)
                             if any(s <= x <= e for s, e in a) and any(s <= x <= e for s, e in b)])
        got = f([x[:] for x in a], [x[:] for x in b])
        pts = {x for s, e in got for x in range(s, e + 1)}
        assert pts == {x for x in range(0, 41) if any(s <= x <= e for s, e in a) and any(s <= x <= e for s, e in b)}
        assert all(s <= e for s, e in got) and got == sorted(got)


@test("Intervals:stab-k")
def _(ns):
    f = ns["intersection_size_two"]
    assert f([[1, 3], [3, 7], [8, 9]]) == 5 and f([[1, 3], [1, 4], [2, 5], [3, 5]]) == 3 and f([[1, 2], [2, 3], [2, 4], [4, 5]]) == 5
    r = random.Random(305)
    for _ in range(150):
        iv = []
        for _ in range(r.randint(1, 5)):
            a = r.randint(0, 8)
            iv.append([a, a + r.randint(1, 4)])
        pts = range(0, 14)
        want = next(k for k in range(2, 12) if any(all(sum(1 for p in ps if a <= p <= b) >= 2 for a, b in iv) for ps in _it.combinations(pts, k)))
        assert f([x[:] for x in iv]) == want, iv


@test("Intervals:room-heap")
def _(ns):
    f = ns["most_booked"]
    assert f(2, [[0, 10], [1, 5], [2, 7], [3, 4]]) == 0 and f(3, [[1, 20], [2, 10], [3, 5], [4, 9], [6, 8]]) == 1
    r = random.Random(306)
    for _ in range(200):
        n = r.randint(1, 3)
        starts = r.sample(range(0, 30), r.randint(1, 7))
        meet = [[s, s + r.randint(1, 8)] for s in starts]
        free_at, used = [0] * n, [0] * n
        for s, e in sorted(meet):
            avail = [i for i in range(n) if free_at[i] <= s]
            if avail:
                room = avail[0]
                free_at[room] = e
            else:
                room = min(range(n), key=lambda i: (free_at[i], i))
                free_at[room] += e - s
            used[room] += 1
        assert f(n, [m[:] for m in meet]) == used.index(max(used))


@test("Intervals:room-heap#Smallest unoccupied chair")
def _(ns):
    f = ns["smallest_chair"]
    assert f([[1, 4], [2, 3], [4, 6]], 1) == 1 and f([[3, 10], [1, 5], [2, 6]], 0) == 2
    r = random.Random(307)
    for _ in range(200):
        n = r.randint(1, 6)
        arrivals = r.sample(range(0, 30), n)
        times = [[a, a + r.randint(1, 10)] for a in arrivals]
        target = r.randrange(n)
        chairs = [0] * n  # time each chair becomes free
        want = None
        for i in sorted(range(n), key=lambda i: times[i][0]):
            c = next(c for c in range(n) if chairs[c] <= times[i][0])
            chairs[c] = times[i][1]
            if i == target:
                want = c
        assert f([t[:] for t in times], target) == want


@test("Intervals:difference-array")
def _(ns):
    f = ns["corp_flight_bookings"]
    assert f([[1, 2, 10], [2, 3, 20], [2, 5, 25]], 5) == [10, 55, 45, 25, 25]
    r = random.Random(308)
    for _ in range(200):
        n = r.randint(1, 8)
        b = []
        for _ in range(r.randint(0, 6)):
            a = r.randint(1, n)
            b.append([a, r.randint(a, n), r.randint(1, 9)])
        want = [sum(s for x, y, s in b if x <= i <= y) for i in range(1, n + 1)]
        assert f([x[:] for x in b], n) == want


@test("Intervals:difference-array#Car pooling (events by time)")
def _(ns):
    f = ns["car_pooling"]
    assert f([[2, 1, 5], [3, 3, 7]], 4) is False and f([[2, 1, 5], [3, 3, 7]], 5) is True and f([[3, 2, 7], [3, 7, 9], [8, 3, 9]], 11) is True
    r = random.Random(309)
    for _ in range(200):
        trips = []
        for _ in range(r.randint(1, 6)):
            s = r.randint(0, 8)
            trips.append([r.randint(1, 4), s, s + r.randint(1, 5)])
        cap = r.randint(1, 8)
        want = all(sum(p for p, a, b in trips if a <= t < b) <= cap for t in range(0, 15))
        assert f([t[:] for t in trips], cap) is want


@test("Intervals:difference-array#Two dimensions")
def _(ns):
    f = ns["range_add_queries"]
    assert f(3, [[1, 1, 2, 2], [0, 0, 1, 1]]) == [[1, 1, 0], [1, 2, 1], [0, 1, 1]]
    r = random.Random(310)
    for _ in range(100):
        n = r.randint(1, 6)
        qs = []
        for _ in range(r.randint(0, 5)):
            a, b = sorted((r.randrange(n), r.randrange(n)))
            c, d = sorted((r.randrange(n), r.randrange(n)))
            qs.append([a, c, b, d])
        want = [[sum(1 for r1, c1, r2, c2 in qs if r1 <= i <= r2 and c1 <= j <= c2) for j in range(n)] for i in range(n)]
        assert f(n, [q[:] for q in qs]) == want


def _skyline_brute(b):
    if not b:
        return []
    hi = max(r for _, r, _ in b)
    out, prev = [], 0
    for x in range(0, hi + 1):
        h = max([bh for l, r, bh in b if l <= x < r] or [0])
        if h != prev:
            out.append([x, h])
            prev = h
    return out


@test("Intervals:skyline")
def _(ns):
    f = ns["get_skyline"]
    assert f([[2, 9, 10], [3, 7, 15], [5, 12, 12], [15, 20, 10], [19, 24, 8]]) == [[2, 10], [3, 15], [7, 12], [12, 0], [15, 10], [20, 8], [24, 0]]
    r = random.Random(311)
    for _ in range(300):
        b = []
        for _ in range(r.randint(1, 6)):
            l = r.randint(0, 10)
            b.append([l, l + r.randint(1, 6), r.randint(1, 8)])
        b.sort()
        assert f([x[:] for x in b]) == _skyline_brute(b), b


@test("Intervals:skyline#Falling squares (range assign and max)")
def _(ns):
    f = ns["falling_squares"]
    assert f([[1, 2], [2, 3], [6, 1]]) == [2, 5, 5] and f([[100, 100], [200, 100]]) == [100, 100]
    r = random.Random(312)
    for _ in range(200):
        pos = [[r.randint(0, 8), r.randint(1, 4)] for _ in range(r.randint(1, 6))]
        h, out, top = {}, [], 0
        for left, size in pos:
            base = max([h.get(x, 0) for x in range(left, left + size)] or [0])
            for x in range(left, left + size):
                h[x] = base + size
            top = max(top, base + size)
            out.append(top)
        assert f([p[:] for p in pos]) == out


@test("Intervals:flowers")
def _(ns):
    f = ns["full_bloom_flowers"]
    assert f([[1, 6], [3, 7], [9, 12], [4, 13]], [2, 3, 7, 11]) == [1, 2, 2, 2]
    r = random.Random(313)
    for _ in range(200):
        fl = []
        for _ in range(r.randint(0, 6)):
            a = r.randint(1, 10)
            fl.append([a, a + r.randint(0, 6)])
        ppl = [r.randint(0, 18) for _ in range(r.randint(1, 6))]
        assert f([x[:] for x in fl], ppl[:]) == [sum(1 for a, b in fl if a <= t <= b) for t in ppl]


@test("Intervals:flowers#Maximum population year")
def _(ns):
    f = ns["maximum_population"]
    assert f([[1993, 1999], [2000, 2010]]) == 1993 and f([[1950, 1961], [1960, 1971], [1970, 1981]]) == 1960
    r = random.Random(314)
    for _ in range(200):
        logs = []
        for _ in range(r.randint(1, 7)):
            a = r.randint(1950, 2045)
            logs.append([a, a + r.randint(1, 5)])
        counts = {y: sum(1 for a, b in logs if a <= y < b) for y in range(1950, 2051)}
        best = max(counts.values())
        assert f([l[:] for l in logs]) == min(y for y, c in counts.items() if c == best)


@test("Intervals:bucket-counts")
def _(ns):
    t = ns["TweetCounts"]()
    t.recordTweet("t3", 0)
    t.recordTweet("t3", 60)
    t.recordTweet("t3", 10)
    assert t.getTweetCountsPerFrequency("minute", "t3", 0, 59) == [2]
    assert t.getTweetCountsPerFrequency("minute", "t3", 0, 60) == [2, 1]
    r = random.Random(315)
    for _ in range(100):
        t, rec = ns["TweetCounts"](), []
        for _ in range(r.randint(0, 12)):
            x = r.randint(0, 200)
            rec.append(x)
            t.recordTweet("a", x)
        lo = r.randint(0, 100)
        hi = lo + r.randint(0, 150)
        size = r.choice([("minute", 60), ("hour", 3600)])
        want = [0] * ((hi - lo) // size[1] + 1)
        for x in rec:
            if lo <= x <= hi:
                want[(x - lo) // size[1]] += 1
        assert t.getTweetCountsPerFrequency(size[0], "a", lo, hi) == want


@test("Intervals:interval-set")
def _(ns):
    r = random.Random(316)
    for _ in range(100):
        sr, seen = ns["SummaryRanges"](), set()
        for _ in range(r.randint(1, 15)):
            v = r.randint(0, 15)
            sr.addNum(v)
            seen.add(v)
            want = []
            for x in sorted(seen):
                if want and want[-1][1] == x - 1:
                    want[-1][1] = x
                else:
                    want.append([x, x])
            assert sr.getIntervals() == want


@test("Intervals:interval-set#Range module (half-open ranges)")
def _(ns):
    r = random.Random(317)
    for _ in range(100):
        m, cells = ns["RangeModule"](), set()
        for _ in range(r.randint(1, 15)):
            a = r.randint(0, 15)
            b = a + r.randint(1, 5)
            op = r.choice("aqr")
            if op == "a":
                m.addRange(a, b)
                cells |= set(range(a, b))
            elif op == "r":
                m.removeRange(a, b)
                cells -= set(range(a, b))
            else:
                assert m.queryRange(a, b) is (set(range(a, b)) <= cells)


@test("Intervals:free-days")
def _(ns):
    f = ns["count_days"]
    assert f(10, [[5, 7], [1, 3], [9, 10]]) == 2 and f(5, [[2, 4], [1, 3]]) == 1 and f(6, [[1, 6]]) == 0
    r = random.Random(318)
    for _ in range(200):
        days = r.randint(1, 15)
        m = []
        for _ in range(r.randint(0, 5)):
            a = r.randint(1, days)
            m.append([a, r.randint(a, days)])
        used = {d for a, b in m for d in range(a, b + 1)}
        assert f(days, [x[:] for x in m]) == days - len(used)


@test("Intervals:rectangle")
def _(ns):
    f = ns["compute_area"]
    assert f(-3, 0, 3, 4, 0, -1, 9, 2) == 45 and f(-2, -2, 2, 2, -2, -2, 2, 2) == 16
    r = random.Random(319)
    for _ in range(300):
        def rect():
            x, y = r.randint(-4, 3), r.randint(-4, 3)
            return x, y, x + r.randint(1, 5), y + r.randint(1, 5)
        a, b = rect(), rect()
        cells = set()
        for x1, y1, x2, y2 in (a, b):
            cells |= {(x, y) for x in range(x1, x2) for y in range(y1, y2)}
        assert f(*a, *b) == len(cells)


@test("Intervals:rectangle#Union area of many rectangles")
def _(ns):
    f = ns["rectangle_area"]
    assert f([[0, 0, 2, 2], [1, 0, 2, 3], [1, 0, 3, 1]]) == 6 and f([[0, 0, 1000000000, 1000000000]]) == 49
    r = random.Random(320)
    for _ in range(200):
        rects = []
        for _ in range(r.randint(1, 5)):
            x, y = r.randint(0, 6), r.randint(0, 6)
            rects.append([x, y, x + r.randint(1, 5), y + r.randint(1, 5)])
        cells = {(x, y) for x1, y1, x2, y2 in rects for x in range(x1, x2) for y in range(y1, y2)}
        assert f([x[:] for x in rects]) == len(cells)


@test("Intervals:rectangle#Projection area of 3-D shapes")
def _(ns):
    f = ns["projection_area"]
    assert f([[1, 2], [3, 4]]) == 17 and f([[2]]) == 5 and f([[1, 0], [0, 2]]) == 8
    r = random.Random(321)
    for _ in range(200):
        g = _grid(r, r.randint(1, 4), r.randint(1, 4), [0, 1, 2, 3])
        vox = {(i, j, k) for i, row in enumerate(g) for j, v in enumerate(row) for k in range(v)}
        want = len({(i, j) for i, j, _ in vox}) + len({(i, k) for i, _, k in vox}) + len({(j, k) for _, j, k in vox})
        assert f([row[:] for row in g]) == want


@test("Intervals:offline-queries")
def _(ns):
    f = ns["min_interval"]
    assert f([[1, 4], [2, 4], [3, 6], [4, 4]], [2, 3, 4, 5]) == [3, 3, 1, 4]
    assert f([[2, 3], [2, 5], [1, 8], [20, 25]], [2, 19, 5, 22]) == [2, -1, 4, 6]
    r = random.Random(322)
    for _ in range(200):
        iv = []
        for _ in range(r.randint(1, 6)):
            a = r.randint(1, 12)
            iv.append([a, a + r.randint(0, 6)])
        q = [r.randint(1, 20) for _ in range(r.randint(1, 6))]
        want = [min([b - a + 1 for a, b in iv if a <= x <= b] or [-1]) for x in q]
        assert f([x[:] for x in iv], q[:]) == want


@test("Intervals:circular")
def _(ns):
    f = ns["find_min_difference"]
    assert f(["23:59", "00:00"]) == 1 and f(["00:00", "23:59", "00:00"]) == 0
    r = random.Random(323)
    for _ in range(200):
        pts = ["%02d:%02d" % (r.randint(0, 23), r.randint(0, 59)) for _ in range(r.randint(2, 6))]
        mins = [int(p[:2]) * 60 + int(p[3:]) for p in pts]
        want = min(min(abs(a - b), 1440 - abs(a - b)) for a, b in _it.combinations(mins, 2))
        assert f(pts[:]) == want


@test("Intervals:circular#Visible points (window of angles)")
def _(ns):
    f = ns["visible_points"]
    assert f([[2, 1], [2, 2], [3, 3]], 90, [1, 1]) == 3 and f([[2, 1], [2, 2], [3, 4], [1, 1]], 90, [1, 1]) == 4
    r = random.Random(324)
    import math
    for _ in range(200):
        pts = [[r.randint(-4, 4), r.randint(-4, 4)] for _ in range(r.randint(1, 7))]
        loc = [r.randint(-2, 2), r.randint(-2, 2)]
        ang = r.choice([0, 30, 45, 90, 135, 180, 270])
        here = sum(1 for p in pts if p == loc)
        dirs = [math.degrees(math.atan2(p[1] - loc[1], p[0] - loc[0])) % 360 for p in pts if p != loc]
        best = 0
        for a in dirs:
            best = max(best, sum(1 for d in dirs if (d - a) % 360 <= ang + 1e-7 or (d - a) % 360 >= 360 - 1e-7))
        assert f([p[:] for p in pts], ang, loc[:]) == best + here, (pts, loc, ang)


@test("Intervals:next-start")
def _(ns):
    f = ns["find_right_interval"]
    assert f([[1, 2]]) == [-1] and f([[3, 4], [2, 3], [1, 2]]) == [-1, 0, 1] and f([[1, 4], [2, 3], [3, 4]]) == [-1, 2, -1]
    r = random.Random(325)
    for _ in range(200):
        starts = r.sample(range(0, 20), r.randint(1, 6))
        iv = [[s, s + r.randint(0, 6)] for s in starts]
        want = []
        for _, e in iv:
            c = [(s, i) for i, (s, _) in enumerate(iv) if s >= e]
            want.append(min(c)[1] if c else -1)
        assert f([x[:] for x in iv]) == want


@test("Intervals:from-data")
def _(ns):
    f = ns["summary_ranges"]
    assert f([0, 1, 2, 4, 5, 7]) == ["0->2", "4->5", "7"] and f([]) == [] and f([-1]) == ["-1"]
    r = random.Random(326)
    for _ in range(200):
        nums = sorted(r.sample(range(-5, 15), r.randint(0, 10)))
        out = f(nums[:])
        got = []
        for s in out:
            if "->" in s:
                a, b = map(int, s.split("->"))
                got += list(range(a, b + 1))
            else:
                got.append(int(s))
        assert got == nums
        assert len(out) == sum(1 for i, x in enumerate(nums) if i == 0 or nums[i - 1] != x - 1)


@test("Intervals:from-data#Add bold tags (mark, then merge runs)")
def _(ns):
    f = ns["add_bold_tag"]
    assert f("abcxyz123", ["abc", "123"]) == "<b>abc</b>xyz<b>123</b>" and f("aaabbcc", ["aaa", "aab", "bc"]) == "<b>aaabbc</b>c"
    r = random.Random(327)
    for _ in range(200):
        s = "".join(r.choice("abc") for _ in range(r.randint(1, 10)))
        words = ["".join(r.choice("abc") for _ in range(r.randint(1, 3))) for _ in range(r.randint(1, 3))]
        mark = [any(s.startswith(w, i) for w in words for i in range(max(0, k - len(w) + 1), k + 1)) for k in range(len(s))]
        want, k = "", 0
        while k < len(s):
            if mark[k]:
                j = k
                while j < len(s) and mark[j]:
                    j += 1
                want += "<b>" + s[k:j] + "</b>"
                k = j
            else:
                want += s[k]
                k += 1
        assert f(s, words[:]) == want, (s, words)


@test("Intervals:from-data#Smallest range covering k lists (heap)")
def _(ns):
    f = ns["smallest_range"]
    assert f([[4, 10, 15, 24, 26], [0, 9, 12, 20], [5, 18, 22, 30]]) == [20, 24] and f([[1, 2, 3], [1, 2, 3], [1, 2, 3]]) == [1, 1]
    r = random.Random(328)
    for _ in range(200):
        lists = [sorted(r.sample(range(0, 20), r.randint(1, 5))) for _ in range(r.randint(1, 4))]
        best = None
        for lo in sorted({x for l in lists for x in l}):
            if all(any(x >= lo for x in l) for l in lists):
                hi = max(min(x for x in l if x >= lo) for l in lists)
                if best is None or hi - lo < best[1] - best[0]:
                    best = [lo, hi]
        assert f([l[:] for l in lists]) == best, lists


@test("Intervals:weighted-k")
def _(ns):
    f = ns["max_value"]
    assert f([[1, 2, 4], [3, 4, 3], [2, 3, 1]], 2) == 7 and f([[1, 2, 4], [3, 4, 3], [2, 3, 10]], 2) == 10 and f([[1, 1, 1], [2, 2, 2], [3, 3, 3], [4, 4, 4]], 3) == 9
    r = random.Random(329)
    for _ in range(200):
        ev = []
        for _ in range(r.randint(1, 7)):
            a = r.randint(1, 10)
            ev.append([a, a + r.randint(0, 3), r.randint(1, 9)])
        k = r.randint(1, 3)
        best = max(sum(e[2] for e in c) for j in range(k + 1) for c in _it.combinations(ev, j)
                   if all(a[1] < b[0] or b[1] < a[0] for a, b in _it.combinations(c, 2)))
        assert f([e[:] for e in ev], k) == best, (ev, k)


# ---- trees (extras) -------------------------------------------------------------------------------------------------

from page_tests import _inorder_vals, _preorder, _random_bst, _random_tree, _tree_copy, _tree_distances  # noqa: E402


def _rec_order(t, order):
    if t is None:
        return []
    if order == "in":
        return _rec_order(t.left, order) + [t.val] + _rec_order(t.right, order)
    if order == "pre":
        return [t.val] + _rec_order(t.left, order) + _rec_order(t.right, order)
    return _rec_order(t.left, order) + _rec_order(t.right, order) + [t.val]


def _levels(t):
    out, level = [], [t] if t else []
    while level:
        out.append(level)
        level = [c for n in level for c in (n.left, n.right) if c]
    return out


def _parents(t):
    par = {id(t): None} if t else {}
    for n in _preorder(t):
        for c in (n.left, n.right):
            if c:
                par[id(c)] = n
    return par


def _height_edges(t):
    return -1 if t is None else 1 + max(_height_edges(t.left), _height_edges(t.right))


@test("Trees:traversals-iterative")
def _(ns):
    f = ns["inorder"]
    assert f(None) == []
    r = random.Random(400)
    for _ in range(150):
        t = _random_tree(r, r.randint(0, 10))
        assert f(t) == _rec_order(t, "in")
    chain = cur = TreeNode(0)
    for i in range(1, 3000):
        cur.right = TreeNode(i)
        cur = cur.right
    assert f(chain) == list(range(3000)), "a deep tree must not use recursion"


@test("Trees:traversals-iterative#Preorder")
def _(ns):
    f = ns["preorder"]
    assert f(None) == []
    r = random.Random(401)
    for _ in range(150):
        t = _random_tree(r, r.randint(0, 10))
        assert f(t) == _rec_order(t, "pre")


@test("Trees:traversals-iterative#Postorder")
def _(ns):
    f = ns["postorder"]
    assert f(None) == []
    r = random.Random(402)
    for _ in range(150):
        t = _random_tree(r, r.randint(0, 10))
        assert f(t) == _rec_order(t, "post")


@test("Trees:traversals-iterative#Morris inorder (O(1) space)")
def _(ns):
    f = ns["morris_inorder"]
    r = random.Random(403)
    for _ in range(150):
        t = _random_tree(r, r.randint(0, 10))
        before = _shape(t)
        assert f(t) == _rec_order(t, "in")
        assert _shape(t) == before, "the threads must be removed again"


@test("Trees:bfs-levels#Zigzag")
def _(ns):
    f = ns["zigzag_level_order"]
    assert f(_tree([3, 9, 20, None, None, 15, 7])) == [[3], [20, 9], [15, 7]] and f(None) == []
    r = random.Random(404)
    for _ in range(100):
        t = _random_tree(r, r.randint(0, 10))
        want = [[n.val for n in lv][:: -1 if i % 2 else 1] for i, lv in enumerate(_levels(t))]
        assert f(t) == want


@test("Trees:bfs-levels#Right side view")
def _(ns):
    f = ns["right_side_view"]
    assert f(_tree([1, 2, 3, None, 5, None, 4])) == [1, 3, 4] and f(None) == []
    r = random.Random(405)
    for _ in range(100):
        t = _random_tree(r, r.randint(0, 10))
        assert f(t) == [lv[-1].val for lv in _levels(t)]


def _positions(t):
    out = {}

    def go(n, pos, depth):
        if n:
            out[id(n)] = (pos, depth)
            go(n.left, 2 * pos, depth + 1)
            go(n.right, 2 * pos + 1, depth + 1)

    go(t, 1, 0)
    return out


@test("Trees:bfs-levels#Maximum width")
def _(ns):
    f = ns["width_of_binary_tree"]
    assert f(_tree([1, 3, 2, 5, 3, None, 9])) == 4 and f(_tree([1, 3, 2, 5])) == 2
    r = random.Random(406)
    for _ in range(150):
        t = _random_tree(r, r.randint(1, 10))
        pos = _positions(t)
        want = 0
        for d in range(len(_levels(t))):
            ps = [p for p, dd in pos.values() if dd == d]
            want = max(want, max(ps) - min(ps) + 1)
        assert f(t) == want
    deep = cur = TreeNode(1)
    for _ in range(200):
        cur.left = TreeNode(1)
        cur = cur.left
    assert f(deep) == 1


@test("Trees:bfs-levels#Is complete")
def _(ns):
    f = ns["is_complete_tree"]
    assert f(_tree([1, 2, 3, 4, 5, 6])) is True and f(_tree([1, 2, 3, 4, 5, None, 7])) is False
    r = random.Random(407)
    for _ in range(200):
        t = _random_tree(r, r.randint(1, 9))
        n = len(_preorder(t))
        assert f(t) is ({p for p, _ in _positions(t).values()} == set(range(1, n + 1)))
    for n in range(1, 12):
        assert f(_tree(list(range(1, n + 1)))) is True


@test("Trees:bfs-levels#Next right pointers (O(1) space)")
def _(ns):
    f = ns["connect"]
    r = random.Random(408)
    for _ in range(100):
        t = _random_tree(r, r.randint(1, 11))
        for n in _preorder(t):
            n.next = None
        f(t)
        for lv in _levels(t):
            for a, b in zip(lv, lv[1:] + [None]):
                assert a.next is b


@test("Trees:bfs-levels#Cousins")
def _(ns):
    f = ns["is_cousins"]
    assert f(_tree([1, 2, 3, 4]), 4, 3) is False and f(_tree([1, 2, 3, None, 4, None, 5]), 5, 4) is True
    r = random.Random(409)
    for _ in range(200):
        t = _random_tree(r, r.randint(2, 9), distinct=True)
        nodes = _preorder(t)
        x, y = r.sample([n.val for n in nodes], 2)
        par, depth = {}, {}

        def go(n, p, d):
            if n:
                par[n.val], depth[n.val] = p, d
                go(n.left, n, d + 1)
                go(n.right, n, d + 1)

        go(t, None, 0)
        assert f(t, x, y) is (depth[x] == depth[y] and par[x] is not par[y])


@test("Trees:bfs-levels#Reverse odd levels")
def _(ns):
    f = ns["reverse_odd_levels"]
    r = random.Random(410)

    def perfect(d):
        if d == 0:
            return None
        return TreeNode(r.randint(0, 99), perfect(d - 1), perfect(d - 1))

    for _ in range(60):
        t = perfect(r.randint(1, 4))
        want = [[n.val for n in lv][:: -1 if i % 2 else 1] for i, lv in enumerate(_levels(t))]
        got = f(t)
        assert [[n.val for n in lv] for lv in _levels(got)] == want


@test("Trees:bfs-levels#Cousin sums")
def _(ns):
    f = ns["replace_value_in_tree"]
    r = random.Random(411)
    for _ in range(100):
        t = _random_tree(r, r.randint(1, 10), lo=0, hi=9)
        par = _parents(t)
        levels = _levels(t)
        want = {}
        for lv in levels:
            total = sum(n.val for n in lv)
            for n in lv:
                p = par[id(n)]
                sibs = sum(c.val for c in (p.left, p.right) if c) if p else n.val
                want[id(n)] = total - sibs
        got = f(t)
        assert all(n.val == want[id(n)] for n in _preorder(got))


def _boundary_alt(root):
    if root is None:
        return []

    def leaf(n):
        return n.left is None and n.right is None

    if leaf(root):
        return [root.val]
    out = [root.val]

    def left(n):
        if n is None or leaf(n):
            return
        out.append(n.val)
        left(n.left or n.right)

    def leaves(n):
        if n is None:
            return
        if leaf(n):
            out.append(n.val)
        leaves(n.left)
        leaves(n.right)

    def right(n):
        if n is None or leaf(n):
            return
        right(n.right or n.left)
        out.append(n.val)

    left(root.left)
    leaves(root.left)
    leaves(root.right)
    right(root.right)
    return out


@test("Trees:columns")
def _(ns):
    f = ns["vertical_traversal"]
    assert f(_tree([3, 9, 20, None, None, 15, 7])) == [[9], [3, 15], [20], [7]] and f(None) == []
    r = random.Random(412)
    for _ in range(150):
        t = _random_tree(r, r.randint(0, 10))
        cols = {}

        def go(n, row, col):
            if n:
                cols.setdefault(col, []).append((row, n.val))
                go(n.left, row + 1, col - 1)
                go(n.right, row + 1, col + 1)

        go(t, 0, 0)
        assert f(t) == [[v for _, v in sorted(cols[c])] for c in sorted(cols)]


@test("Trees:columns#Boundary of a binary tree")
def _(ns):
    f = ns["boundary_of_binary_tree"]
    assert f(_tree([1, None, 2, 3, 4])) == [1, 3, 4, 2] and f(_tree([1, 2, 3, 4, 5, 6, None, None, None, 7, 8, 9, 10])) == [1, 2, 4, 7, 8, 9, 10, 6, 3]
    r = random.Random(413)
    for _ in range(300):
        t = _random_tree(r, r.randint(0, 11))
        assert f(t) == _boundary_alt(t)


@test("Trees:dfs-return#Balanced tree")
def _(ns):
    f = ns["is_balanced"]
    assert f(_tree([3, 9, 20, None, None, 15, 7])) is True and f(_tree([1, 2, 2, 3, 3, None, None, 4, 4])) is False and f(None) is True
    r = random.Random(414)

    def ok(n):
        return n is None or (abs(_height_edges(n.left) - _height_edges(n.right)) <= 1 and ok(n.left) and ok(n.right))

    for _ in range(200):
        t = _random_tree(r, r.randint(0, 11))
        assert f(t) is ok(t)


def _path_nodes(par, a, b):
    """The nodes on the tree path from a to b (inclusive)."""
    up_a, x = [], a
    while x is not None:
        up_a.append(x)
        x = par[id(x)]
    ids = {id(n) for n in up_a}
    up_b, y = [], b
    while id(y) not in ids:
        up_b.append(y)
        y = par[id(y)]
    return up_a[: [id(n) for n in up_a].index(id(y)) + 1] + up_b[::-1]


@test("Trees:dfs-return#Maximum path sum")
def _(ns):
    f = ns["max_path_sum"]
    assert f(_tree([1, 2, 3])) == 6 and f(_tree([-10, 9, 20, None, None, 15, 7])) == 42 and f(_tree([-3])) == -3
    r = random.Random(415)
    for _ in range(200):
        t = _random_tree(r, r.randint(1, 9), lo=-9, hi=9)
        par = _parents(t)
        nodes = _preorder(t)
        want = max(sum(n.val for n in _path_nodes(par, a, b)) for a in nodes for b in nodes)
        assert f(t) == want


@test("Trees:dfs-return#House robber III")
def _(ns):
    f = ns["rob"]
    assert f(_tree([3, 2, 3, None, 3, None, 1])) == 7 and f(_tree([3, 4, 5, 1, 3, None, 1])) == 9
    r = random.Random(416)
    for _ in range(150):
        t = _random_tree(r, r.randint(1, 9), lo=0, hi=9)
        nodes = _preorder(t)
        idx = {id(n): i for i, n in enumerate(nodes)}
        edges = [(idx[id(n)], idx[id(c)]) for n in nodes for c in (n.left, n.right) if c]
        best = 0
        for mask in range(1 << len(nodes)):
            if all(not (mask >> a & 1 and mask >> b & 1) for a, b in edges):
                best = max(best, sum(nodes[i].val for i in range(len(nodes)) if mask >> i & 1))
        assert f(t) == best


@test("Trees:dfs-return#Largest BST subtree")
def _(ns):
    f = ns["largest_bst_subtree"]
    assert f(_tree([10, 5, 15, 1, 8, None, 7])) == 3 and f(None) == 0
    r = random.Random(417)

    def size_if_bst(n):
        vals = _inorder_vals(n)
        return len(vals) if all(a < b for a, b in zip(vals, vals[1:])) else 0

    for _ in range(200):
        t = _random_tree(r, r.randint(0, 10), lo=0, hi=12)
        assert f(t) == max([size_if_bst(n) for n in _preorder(t)] or [0])


@test("Trees:dfs-return#Longest univalue path")
def _(ns):
    f = ns["longest_univalue_path"]
    assert f(_tree([5, 4, 5, 1, 1, None, 5])) == 2 and f(_tree([1, 4, 5, 4, 4, None, 5])) == 2
    r = random.Random(418)
    for _ in range(200):
        t = _random_tree(r, r.randint(1, 10), lo=1, hi=2)
        par = _parents(t)
        nodes = _preorder(t)
        want = 0
        for a in nodes:
            for b in nodes:
                p = _path_nodes(par, a, b)
                if len({n.val for n in p}) == 1:
                    want = max(want, len(p) - 1)
        assert f(t) == want


@test("Trees:dfs-return#Good leaf pairs")
def _(ns):
    f = ns["count_pairs"]
    assert f(_tree([1, 2, 3, None, 4]), 3) == 1 and f(_tree([1, 2, 3, 4, 5, 6, 7]), 3) == 2
    r = random.Random(419)
    for _ in range(150):
        t = _random_tree(r, r.randint(1, 10))
        dist = _tree_distances(t)
        leaves = [n for n in _preorder(t) if n.left is None and n.right is None]
        k = r.randint(1, 5)
        want = sum(1 for a, b in _it.combinations(leaves, 2) if dist[(id(a), id(b))] <= k)
        assert f(t, k) == want


def _root_to_leaf(t):
    out = []

    def go(n, path):
        if n is None:
            return
        path = path + [n.val]
        if n.left is None and n.right is None:
            out.append(path)
        go(n.left, path)
        go(n.right, path)

    go(t, [])
    return out


@test("Trees:dfs-carry#Path sum II (all paths)")
def _(ns):
    f = ns["path_sum"]
    assert sorted(f(_tree([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1]), 22)) == [[5, 4, 11, 2], [5, 8, 4, 5]]
    r = random.Random(420)
    for _ in range(150):
        t = _random_tree(r, r.randint(0, 10), lo=0, hi=4)
        target = r.randint(0, 12)
        assert sorted(f(t, target)) == sorted(p for p in _root_to_leaf(t) if sum(p) == target)


@test("Trees:dfs-carry#Root-to-leaf numbers")
def _(ns):
    f = ns["sum_numbers"]
    assert f(_tree([1, 2, 3])) == 25 and f(_tree([4, 9, 0, 5, 1])) == 1026 and f(None) == 0
    r = random.Random(421)
    for _ in range(150):
        t = _random_tree(r, r.randint(0, 10), lo=0, hi=9)
        assert f(t) == sum(int("".join(map(str, p))) for p in _root_to_leaf(t))


@test("Trees:dfs-carry#Largest difference with an ancestor")
def _(ns):
    f = ns["max_ancestor_diff"]
    assert f(_tree([8, 3, 10, 1, 6, None, 14, None, None, 4, 7, 13])) == 7 and f(_tree([1, None, 2, None, 0, 3])) == 3
    r = random.Random(422)
    for _ in range(200):
        t = _random_tree(r, r.randint(1, 10), lo=0, hi=30)
        par = _parents(t)
        want = 0
        for n in _preorder(t):
            a = par[id(n)]
            while a is not None:
                want = max(want, abs(a.val - n.val))
                a = par[id(a)]
        assert f(t) == want


@test("Trees:dfs-carry#Pseudo-palindromic paths (bitmask)")
def _(ns):
    f = ns["pseudo_palindromic_paths"]
    assert f(_tree([2, 3, 1, 3, 1, None, 1])) == 2 and f(_tree([2, 1, 1, 1, 3, None, None, None, None, None, 1])) == 1
    r = random.Random(423)
    for _ in range(150):
        t = _random_tree(r, r.randint(1, 10), lo=1, hi=3)
        want = sum(1 for p in _root_to_leaf(t) if sum(1 for d in set(p) if p.count(d) % 2) <= 1)
        assert f(t) == want


@test("Trees:dfs-carry#Longest zigzag path")
def _(ns):
    f = ns["longest_zigzag"]
    assert f(_tree([1, None, 1, 1, 1, None, None, 1, 1, None, 1, None, None, None, 1])) == 3 and f(_tree([1])) == 0
    r = random.Random(424)
    for _ in range(200):
        t = _random_tree(r, r.randint(1, 11))
        want = 0
        for n in _preorder(t):
            for first in ("left", "right"):
                cur, side, steps = n, first, 0
                while getattr(cur, side) is not None:
                    cur = getattr(cur, side)
                    steps += 1
                    side = "right" if side == "left" else "left"
                want = max(want, steps)
        assert f(t) == want


@test("Trees:dfs-edit#Delete nodes, return the forest")
def _(ns):
    f = ns["del_nodes"]
    r = random.Random(425)
    for _ in range(150):
        t = _random_tree(r, r.randint(1, 10), distinct=True, lo=1, hi=30)
        vals = [n.val for n in _preorder(t)]
        gone = set(r.sample(vals, r.randint(0, min(3, len(vals)))))
        par = _parents(t)

        def cut(n):
            return (n.val, cut(n.left) if n.left and n.left.val not in gone else None,
                    cut(n.right) if n.right and n.right.val not in gone else None)

        want = sorted(
            repr(cut(n)) for n in _preorder(t)
            if n.val not in gone and (par[id(n)] is None or par[id(n)].val in gone)
        )
        got = sorted(repr(_shape(x)) for x in f(_tree_copy(t), list(gone)))
        assert got == want


@test("Trees:dfs-edit#Prune subtrees of zeros")
def _(ns):
    f = ns["prune_tree"]
    assert _shape(f(_tree([1, None, 0, 0, 1]))) == (1, None, (0, None, (1, None, None)))
    r = random.Random(426)

    def brute(n):
        if n is None:
            return None
        left, right = brute(n.left), brute(n.right)
        if left is None and right is None and n.val == 0:
            return None
        return (n.val, left, right)

    for _ in range(200):
        t = _random_tree(r, r.randint(1, 10), lo=0, hi=1)
        assert _shape(f(_tree_copy(t))) == brute(t)


@test("Trees:prefix-map")
def _(ns):
    f = ns["path_sum_iii"]
    assert f(_tree([10, 5, -3, 3, 2, None, 11, 3, -2, None, 1]), 8) == 3
    r = random.Random(427)
    for _ in range(150):
        t = _random_tree(r, r.randint(0, 10), lo=-3, hi=5)
        target = r.randint(-3, 8)

        def count(n):
            if n is None:
                return 0

            def down(m, s):
                if m is None:
                    return 0
                s += m.val
                return (s == target) + down(m.left, s) + down(m.right, s)

            return down(n, 0) + count(n.left) + count(n.right)

        assert f(t, target) == count(t)


@test("Trees:lca")
def _(ns):
    f = ns["lowest_common_ancestor"]
    r = random.Random(428)
    for _ in range(200):
        t = _random_tree(r, r.randint(1, 10), distinct=True, lo=1, hi=40)
        nodes = _preorder(t)
        p, q = r.choice(nodes), r.choice(nodes)
        par = _parents(t)
        anc = set()
        x = p
        while x is not None:
            anc.add(id(x))
            x = par[id(x)]
        y = q
        while id(y) not in anc:
            y = par[id(y)]
        assert f(t, p, q) is y


@test("Trees:lca#With parent pointers (two walkers)")
def _(ns):
    f = ns["lowest_common_ancestor_parent"]
    r = random.Random(429)
    for _ in range(200):
        t = _random_tree(r, r.randint(1, 10), distinct=True, lo=1, hi=40)
        par = _parents(t)
        nodes = _preorder(t)
        for n in nodes:
            n.parent = par[id(n)]
        p, q = r.choice(nodes), r.choice(nodes)
        anc = set()
        x = p
        while x is not None:
            anc.add(id(x))
            x = x.parent
        y = q
        while id(y) not in anc:
            y = y.parent
        assert f(p, q) is y


@test("Trees:lca#Deepest leaves")
def _(ns):
    f = ns["lca_deepest_leaves"]
    assert f(_tree([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])).val == 2 and f(_tree([1])).val == 1
    r = random.Random(430)
    for _ in range(200):
        t = _random_tree(r, r.randint(1, 11))
        levels = _levels(t)
        deepest = {id(n) for n in levels[-1]}
        best = None
        for n in _preorder(t):  # the deepest node whose subtree holds all the deepest leaves
            sub = {id(m) for m in _preorder(n)}
            if deepest <= sub:
                best = n
        assert f(t) is best


@test("Trees:lca#Directions between two nodes")
def _(ns):
    f = ns["get_directions"]
    assert f(_tree([5, 1, 2, 3, None, 6, 4]), 3, 6) == "UURL" and f(_tree([2, 1]), 2, 1) == "L"
    r = random.Random(431)
    for _ in range(200):
        t = _random_tree(r, r.randint(2, 10), distinct=True, lo=1, hi=40)
        nodes = _preorder(t)
        a, b = r.sample(nodes, 2)
        par = _parents(t)
        path = _path_nodes(par, a, b)
        out = []
        for u, v in zip(path, path[1:]):
            if par[id(u)] is v:
                out.append("U")
            else:
                out.append("L" if u.left is v else "R")
        assert f(t, a.val, b.val) == "".join(out)


@test("Trees:bst-bounds")
def _(ns):
    f = ns["is_valid_bst"]
    assert f(_tree([2, 1, 3])) is True and f(_tree([5, 1, 4, None, None, 3, 6])) is False and f(_tree([5, 4, 6, None, None, 3, 7])) is False
    r = random.Random(432)
    for _ in range(300):
        t = _random_tree(r, r.randint(0, 9), lo=0, hi=9)
        vals = _inorder_vals(t)
        assert f(t) is all(a < b for a, b in zip(vals, vals[1:]))


@test("Trees:bst-bounds#Build from preorder")
def _(ns):
    f = ns["bst_from_preorder"]
    r = random.Random(433)
    for _ in range(150):
        t = _random_bst(r, r.randint(1, 10))
        pre = [n.val for n in _preorder(t)]
        assert _shape(f(pre[:])) == _shape(t)


@test("Trees:bst-bounds#Verify a preorder list (stack)")
def _(ns):
    f = ns["verify_preorder"]
    assert f([5, 2, 1, 3, 6]) is True and f([5, 2, 6, 1, 3]) is False
    r = random.Random(434)
    for _ in range(300):
        seq = r.sample(range(0, 12), r.randint(1, 7))
        root = None
        for v in seq:  # insert in this order: the preorder of the result is the sequence iff it is a valid preorder
            if root is None:
                root = TreeNode(v)
                continue
            cur = root
            while True:
                side = "left" if v < cur.val else "right"
                if getattr(cur, side) is None:
                    setattr(cur, side, TreeNode(v))
                    break
                cur = getattr(cur, side)
        # a sequence is a BST preorder iff rebuilding by bounds consumes it all
        pre = [n.val for n in _preorder(root)]
        # an exact reference: valid iff the bounds recursion (low and high) consumes everything
        i = 0

        def build(lo, hi):
            nonlocal i
            if i == len(seq) or not lo < seq[i] < hi:
                return
            v = seq[i]
            i += 1
            build(lo, v)
            build(v, hi)

        build(float("-inf"), float("inf"))
        assert f(seq[:]) is (i == len(seq)), seq


@test("Trees:bst-bounds#Trim to a range")
def _(ns):
    f = ns["trim_bst"]
    r = random.Random(435)
    for _ in range(150):
        t = _random_bst(r, r.randint(1, 10))
        lo = r.randint(0, 30)
        hi = lo + r.randint(0, 30)
        want = [v for v in _inorder_vals(t) if lo <= v <= hi]
        got = f(_tree_copy(t), lo, hi)
        vals = _inorder_vals(got)
        assert vals == want and all(a < b for a, b in zip(vals, vals[1:]))


@test("Trees:bst-bounds#Range sum")
def _(ns):
    f = ns["range_sum_bst"]
    r = random.Random(436)
    for _ in range(150):
        t = _random_bst(r, r.randint(1, 10))
        lo = r.randint(0, 40)
        hi = lo + r.randint(0, 30)
        assert f(t, lo, hi) == sum(v for v in _inorder_vals(t) if lo <= v <= hi)


@test("Trees:bst-bounds#Nearest keys")
def _(ns):
    f = ns["closest_nodes"]
    r = random.Random(437)
    for _ in range(100):
        t = _random_bst(r, r.randint(1, 10))
        vals = _inorder_vals(t)
        qs = [r.randint(0, 60) for _ in range(5)]
        want = [[max([v for v in vals if v <= q], default=-1), min([v for v in vals if v >= q], default=-1)] for q in qs]
        assert f(t, qs) == want


@test("Trees:bst-iterator")
def _(ns):
    cls = ns["BSTIterator"]
    r = random.Random(438)
    for _ in range(100):
        t = _random_bst(r, r.randint(1, 10))
        it, got = cls(t), []
        while it.hasNext():
            got.append(it.next())
        assert got == _inorder_vals(t)


@test("Trees:bst-iterator#Two sum on a BST")
def _(ns):
    f = ns["find_target"]
    assert f(_tree([5, 3, 6, 2, 4, None, 7]), 9) is True and f(_tree([5, 3, 6, 2, 4, None, 7]), 28) is False
    r = random.Random(439)
    for _ in range(200):
        t = _random_bst(r, r.randint(1, 9))
        vals = _inorder_vals(t)
        k = r.randint(0, 120)
        assert f(t, k) is any(a + b == k for a, b in _it.combinations(vals, 2))


def _bst_with_duplicates(values):
    root = None
    for v in values:
        node = TreeNode(v)
        if root is None:
            root = node
            continue
        cur = root
        while True:
            side = "left" if v <= cur.val else "right"
            if getattr(cur, side) is None:
                setattr(cur, side, node)
                break
            cur = getattr(cur, side)
    return root


@test("Trees:inorder-state")
def _(ns):
    f = ns["recover_tree"]
    r = random.Random(440)
    for _ in range(150):
        t = _random_bst(r, r.randint(2, 10))
        nodes = _preorder(t)
        a, b = r.sample(nodes, 2)
        a.val, b.val = b.val, a.val
        f(t)
        vals = _inorder_vals(t)
        assert vals == sorted(vals)


@test("Trees:inorder-state#Minimum difference between nodes")
def _(ns):
    f = ns["min_diff_in_bst"]
    assert f(_tree([4, 2, 6, 1, 3])) == 1
    r = random.Random(441)
    for _ in range(150):
        t = _random_bst(r, r.randint(2, 10))
        vals = sorted(_inorder_vals(t))
        assert f(t) == min(b - a for a, b in zip(vals, vals[1:]))


@test("Trees:inorder-state#Greater tree (reverse inorder)")
def _(ns):
    f = ns["convert_bst"]
    r = random.Random(442)
    for _ in range(150):
        t = _random_bst(r, r.randint(1, 10))
        vals = _inorder_vals(t)
        want = [sum(w for w in vals if w >= v) for v in vals]
        assert _inorder_vals(f(t)) == want


@test("Trees:inorder-state#Mode of a BST")
def _(ns):
    f = ns["find_mode"]
    assert f(_tree([1, None, 2, 2])) == [2]
    r = random.Random(443)
    for _ in range(200):
        vals = [r.randint(0, 5) for _ in range(r.randint(1, 10))]
        t = _bst_with_duplicates(vals)
        counts = {v: vals.count(v) for v in set(vals)}
        top = max(counts.values())
        assert sorted(f(t)) == sorted(v for v, c in counts.items() if c == top)


def _balanced_bst(t):
    def ok(n):
        return n is None or (abs(_height_edges(n.left) - _height_edges(n.right)) <= 1 and ok(n.left) and ok(n.right))

    return ok(t)


@test("Trees:sorted-to-bst")
def _(ns):
    f = ns["sorted_array_to_bst"]
    assert f([]) is None
    for n in range(1, 20):
        t = f(list(range(n)))
        assert _inorder_vals(t) == list(range(n)) and _balanced_bst(t)


@test("Trees:sorted-to-bst#Balance an existing BST")
def _(ns):
    f = ns["balance_bst"]
    r = random.Random(444)
    for _ in range(100):
        vals = sorted(r.sample(range(0, 50), r.randint(1, 12)))
        root = None
        for v in vals:  # sorted insertion: a right-leaning chain
            node = TreeNode(v)
            if root is None:
                root = cur = node
            else:
                cur.right = node
                cur = node
        t = f(root)
        assert _inorder_vals(t) == vals and _balanced_bst(t)


@test("Trees:sorted-to-bst#Sorted linked list (inorder simulation)")
def _(ns):
    f = ns["sorted_list_to_bst"]
    assert f(None) is None
    for n in range(1, 20):
        t = f(_ll(list(range(n))))
        assert _inorder_vals(t) == list(range(n)) and _balanced_bst(t)


def _pair(r):
    a = _random_tree(r, r.randint(0, 7), lo=0, hi=2)
    b = _tree_copy(a)
    if r.random() < 0.5:
        b = _random_tree(r, r.randint(0, 7), lo=0, hi=2)
    elif b is not None and r.random() < 0.5:
        r.choice(_preorder(b)).val += 1
    return a, b


@test("Trees:compare")
def _(ns):
    f = ns["is_same_tree"]
    r = random.Random(445)
    for _ in range(300):
        a, b = _pair(r)
        assert f(a, b) is (_shape(a) == _shape(b))


def _mirror_shape(t):
    return None if t is None else (t.val, _mirror_shape(t.right), _mirror_shape(t.left))


@test("Trees:compare#Symmetric")
def _(ns):
    f = ns["is_symmetric"]
    assert f(_tree([1, 2, 2, 3, 4, 4, 3])) is True and f(_tree([1, 2, 2, None, 3, None, 3])) is False
    r = random.Random(446)
    for _ in range(300):
        left = _random_tree(r, r.randint(0, 5), lo=0, hi=1)
        right = _mirror_shape_tree(left) if r.random() < 0.6 else _random_tree(r, r.randint(0, 5), lo=0, hi=1)
        t = TreeNode(1, left, right)
        want = _shape(t.left) == _mirror_shape(t.right)
        assert f(t) is want


def _mirror_shape_tree(t):
    return None if t is None else TreeNode(t.val, _mirror_shape_tree(t.right), _mirror_shape_tree(t.left))


@test("Trees:compare#Subtree of another tree")
def _(ns):
    f = ns["is_subtree"]
    assert f(_tree([3, 4, 5, 1, 2]), _tree([4, 1, 2])) is True and f(_tree([3, 4, 5, 1, 2, None, None, None, None, 0]), _tree([4, 1, 2])) is False
    r = random.Random(447)
    for _ in range(300):
        t = _random_tree(r, r.randint(1, 8), lo=0, hi=2)
        sub = _tree_copy(r.choice(_preorder(t))) if r.random() < 0.5 else _random_tree(r, r.randint(1, 4), lo=0, hi=2)
        want = any(_shape(n) == _shape(sub) for n in _preorder(t))
        assert f(t, sub) is want


def _canon(t):
    if t is None:
        return None
    kids = sorted([repr(_canon(t.left)), repr(_canon(t.right))])
    return (t.val, tuple(kids))


@test("Trees:compare#Flip equivalent")
def _(ns):
    f = ns["flip_equiv"]
    r = random.Random(448)

    def flipped(t):
        if t is None:
            return None
        a, b = flipped(t.left), flipped(t.right)
        return TreeNode(t.val, b, a) if r.random() < 0.5 else TreeNode(t.val, a, b)

    for _ in range(200):
        a = _random_tree(r, r.randint(0, 8), lo=0, hi=2)
        b = flipped(a) if r.random() < 0.6 else _random_tree(r, r.randint(0, 8), lo=0, hi=2)
        assert f(a, b) is (_canon(a) == _canon(b))


@test("Trees:compare#Merge two trees")
def _(ns):
    f = ns["merge_trees"]
    r = random.Random(449)

    def brute(a, b):
        if a is None and b is None:
            return None
        if a is None:
            return _shape(b)
        if b is None:
            return _shape(a)
        return (a.val + b.val, brute(a.left, b.left), brute(a.right, b.right))

    for _ in range(200):
        a = _random_tree(r, r.randint(0, 7))
        b = _random_tree(r, r.randint(0, 7))
        want = brute(a, b)
        assert _shape(f(_tree_copy(a), _tree_copy(b))) == want


@test("Trees:compare#Linked list in a binary tree")
def _(ns):
    f = ns["is_sub_path"]
    assert f(_ll([4, 2, 8]), _tree([1, 4, 4, None, 2, 2, None, 1, None, 6, 8, None, None, None, None, 1, 3])) is True
    r = random.Random(450)
    for _ in range(300):
        t = _random_tree(r, r.randint(1, 9), lo=0, hi=2)
        lst = [r.randint(0, 2) for _ in range(r.randint(1, 4))]

        def down(n, i):
            if i == len(lst):
                return True
            return n is not None and n.val == lst[i] and (down(n.left, i + 1) or down(n.right, i + 1))

        want = any(down(n, 0) for n in _preorder(t))
        assert f(_ll(lst), t) is want


@test("Trees:signature")
def _(ns):
    f = ns["find_duplicate_subtrees"]
    r = random.Random(451)
    for _ in range(200):
        t = _random_tree(r, r.randint(1, 12), lo=0, hi=1)
        counts = {}
        for n in _preorder(t):
            counts[repr(_shape(n))] = counts.get(repr(_shape(n)), 0) + 1
        want = sorted(k for k, c in counts.items() if c >= 2)
        got = f(t)
        assert sorted(repr(_shape(n)) for n in got) == want


@test("Trees:signature#String from a binary tree")
def _(ns):
    f = ns["tree_to_str"]
    assert f(_tree([1, 2, 3, 4])) == "1(2(4))(3)" and f(_tree([1, 2, 3, None, 4])) == "1(2()(4))(3)"
    r = random.Random(452)

    def brute(n):
        if n is None:
            return ""
        if n.left is None and n.right is None:
            return str(n.val)
        if n.right is None:
            return f"{n.val}({brute(n.left)})"
        return f"{n.val}({brute(n.left)})({brute(n.right)})"

    for _ in range(150):
        t = _random_tree(r, r.randint(1, 10))
        assert f(t) == brute(t)


class _NAry:
    def __init__(self, val=0, children=None):
        self.val = val
        self.children = children if children is not None else []


def _random_nary(r, n):
    nodes = [_NAry(i + 1) for i in range(n)]
    for i in range(1, n):
        nodes[r.randrange(i)].children.append(nodes[i])
    return nodes


def _nary_depth(t):
    return 1 + max([_nary_depth(c) for c in t.children], default=0)


@test("Trees:n-ary")
def _(ns):
    f = ns["max_depth"]
    assert f(None) == 0
    r = random.Random(453)
    for _ in range(100):
        nodes = _random_nary(r, r.randint(1, 10))
        assert f(nodes[0]) == _nary_depth(nodes[0])


@test("Trees:n-ary#Find the root (sum trick)")
def _(ns):
    f = ns["find_root"]
    r = random.Random(454)
    for _ in range(100):
        nodes = _random_nary(r, r.randint(1, 10))
        shuffled = nodes[:]
        r.shuffle(shuffled)
        assert f(shuffled) is nodes[0]


@test("Trees:n-ary#Diameter")
def _(ns):
    f = ns["diameter"]
    r = random.Random(455)
    for _ in range(100):
        nodes = _random_nary(r, r.randint(1, 10))
        adj = {id(n): [] for n in nodes}
        for n in nodes:
            for c in n.children:
                adj[id(n)].append(c)
                adj[id(c)].append(n)
        best = 0
        for s in nodes:
            seen, q = {id(s): 0}, [s]
            for u in q:
                for v in adj[id(u)]:
                    if id(v) not in seen:
                        seen[id(v)] = seen[id(u)] + 1
                        q.append(v)
            best = max(best, max(seen.values()))
        assert f(nodes[0]) == best
    assert f(None) == 0


@test("Trees:n-ary#Clone")
def _(ns):
    ns["Node"] = _NAry
    f = ns["clone_tree"]
    r = random.Random(456)
    for _ in range(50):
        nodes = _random_nary(r, r.randint(1, 10))
        c = f(nodes[0])

        def same(a, b):
            return a.val == b.val and a is not b and len(a.children) == len(b.children) and all(same(x, y) for x, y in zip(a.children, b.children))

        assert same(nodes[0], c)
    assert f(None) is None


def _random_edges(r, n):
    return [[r.randrange(i), i] for i in range(1, n)]


def _bfs_dists(n, edges, s):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    dist, q = {s: 0}, [s]
    for u in q:
        for v in adj[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


@test("Trees:rerooting")
def _(ns):
    f = ns["sum_of_distances_in_tree"]
    assert f(1, []) == [0] and f(6, [[0, 1], [0, 2], [2, 3], [2, 4], [2, 5]]) == [8, 12, 6, 10, 10, 10]
    r = random.Random(457)
    for _ in range(100):
        n = r.randint(1, 9)
        edges = _random_edges(r, n)
        assert f(n, [e[:] for e in edges]) == [sum(_bfs_dists(n, edges, s).values()) for s in range(n)]


@test("Trees:rerooting#Binary tree coloring game")
def _(ns):
    f = ns["btree_game_winning_move"]
    assert f(_tree([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]), 11, 3) is True and f(_tree([1, 2, 3]), 3, 1) is False
    r = random.Random(458)
    for _ in range(80):
        n = r.choice([1, 3, 5, 7])
        t = _random_tree(r, n, distinct=True, lo=1, hi=n)
        nodes = _preorder(t)
        adj = {n_.val: [] for n_ in nodes}
        for a in nodes:
            for c in (a.left, a.right):
                if c:
                    adj[a.val].append(c.val)
                    adj[c.val].append(a.val)
        x = r.choice([nn.val for nn in nodes])

        def play(c1, c2, turn, passes):
            if len(c1) + len(c2) == n or passes == 2:
                return len(c2) > len(c1)
            mine = c1 if turn == 1 else c2
            moves = {v for u in mine for v in adj[u] if v not in c1 and v not in c2}
            if not moves:
                return play(c1, c2, 3 - turn, passes + 1)
            res = [play(c1 | {v}, c2, 2, 0) if turn == 1 else play(c1, c2 | {v}, 1, 0) for v in moves]
            return all(res) if turn == 1 else any(res)

        want = any(play(frozenset({x}), frozenset({y}), 1, 0) for y in adj if y != x)
        assert f(t, n, x) is want, (n, x)


@test("Trees:peel-leaves")
def _(ns):
    f = ns["find_min_height_trees"]
    assert f(1, []) == [0] and sorted(f(6, [[3, 0], [3, 1], [3, 2], [3, 4], [5, 4]])) == [3, 4]
    r = random.Random(459)
    for _ in range(150):
        n = r.randint(1, 10)
        edges = _random_edges(r, n)
        ecc = [max(_bfs_dists(n, edges, s).values()) for s in range(n)]
        assert sorted(f(n, [e[:] for e in edges])) == [i for i in range(n) if ecc[i] == min(ecc)]


@test("Trees:parent-map")
def _(ns):
    f = ns["distance_k"]
    r = random.Random(460)
    for _ in range(150):
        t = _random_tree(r, r.randint(1, 10), distinct=True, lo=1, hi=40)
        nodes = _preorder(t)
        idx = {id(n): i for i, n in enumerate(nodes)}
        edges = [[idx[id(a)], idx[id(c)]] for a in nodes for c in (a.left, a.right) if c]
        target = r.choice(nodes)
        k = r.randint(0, 4)
        dist = _bfs_dists(len(nodes), edges, idx[id(target)])
        want = sorted(nodes[i].val for i, d in dist.items() if d == k)
        assert sorted(f(t, target, k)) == want


@test("Trees:parent-map#Time to infect the whole tree")
def _(ns):
    f = ns["amount_of_time"]
    assert f(_tree([1, 5, 3, None, 4, 10, 6, 9, 2]), 3) == 4 and f(_tree([1]), 1) == 0
    r = random.Random(461)
    for _ in range(150):
        t = _random_tree(r, r.randint(1, 10), distinct=True, lo=1, hi=40)
        nodes = _preorder(t)
        idx = {id(n): i for i, n in enumerate(nodes)}
        edges = [[idx[id(a)], idx[id(c)]] for a in nodes for c in (a.left, a.right) if c]
        s = r.choice(nodes)
        assert f(t, s.val) == max(_bfs_dists(len(nodes), edges, idx[id(s)]).values())


@test("Trees:complete")
def _(ns):
    f = ns["count_nodes"]
    assert f(None) == 0
    for n in range(1, 70):
        assert f(_tree(list(range(1, n + 1)))) == n


@test("Trees:complete#Complete binary tree inserter")
def _(ns):
    cls = ns["CBTInserter"]
    r = random.Random(462)
    for _ in range(40):
        n = r.randint(1, 8)
        it = cls(_tree(list(range(1, n + 1))))
        for k in range(r.randint(1, 8)):
            idx = n + k + 1  # the heap index of the new node
            parent_val = it.insert(100 + k)
            assert parent_val == idx // 2 if idx // 2 <= n else True
            want = list(range(1, n + 1)) + [100 + j for j in range(k + 1)]
            assert _shape(it.get_root()) == _shape(_tree(want))


class _QNode:
    def __init__(self, val, isLeaf, topLeft, topRight, bottomLeft, bottomRight):
        self.val, self.isLeaf = val, isLeaf
        self.topLeft, self.topRight, self.bottomLeft, self.bottomRight = topLeft, topRight, bottomLeft, bottomRight


@test("Trees:quad-tree")
def _(ns):
    ns["Node"] = _QNode
    f = ns["construct"]
    r = random.Random(463)

    def expand(q, size, grid, r0, c0):
        if q.isLeaf:
            assert q.topLeft is None
            for i in range(size):
                for j in range(size):
                    grid[r0 + i][c0 + j] = int(q.val)
            return
        h = size // 2
        expand(q.topLeft, h, grid, r0, c0)
        expand(q.topRight, h, grid, r0, c0 + h)
        expand(q.bottomLeft, h, grid, r0 + h, c0)
        expand(q.bottomRight, h, grid, r0 + h, c0 + h)

    for _ in range(100):
        n = r.choice([1, 2, 4, 8])
        grid = [[r.choice([0, 1]) if r.random() < 0.5 else 1 for _ in range(n)] for _ in range(n)]
        if r.random() < 0.3:
            grid = [[r.choice([0, 1])] * n] * n
        q = f([row[:] for row in grid])
        back = [[None] * n for _ in range(n)]
        expand(q, n, back, 0, 0)
        assert back == grid
        uniform = len({v for row in grid for v in row}) == 1
        assert q.isLeaf is uniform


@test("Trees:from-descriptions")
def _(ns):
    f = ns["create_binary_tree"]
    r = random.Random(464)
    for _ in range(100):
        t = _random_tree(r, r.randint(1, 10), distinct=True, lo=1, hi=50)
        desc = [[a.val, c.val, 1 if a.left is c else 0] for a in _preorder(t) for c in (a.left, a.right) if c]
        r.shuffle(desc)
        if not desc:
            continue
        assert _shape(f([d[:] for d in desc])) == _shape(t)


@test("Trees:from-descriptions#Depth-marked preorder (dashes)")
def _(ns):
    f = ns["recover_from_preorder"]
    assert _shape(f("1-2--3--4-5--6--7")) == _shape(_tree([1, 2, 5, 3, 4, 6, 7]))
    r = random.Random(465)

    def gen(k, vals):
        if k == 0:
            return None
        node = TreeNode(next(vals))
        left = r.randint(0, k - 1)
        node.left = gen(left, vals)
        node.right = gen(k - 1 - left, vals) if node.left else None  # a single child is the left one
        if node.left is None and k - 1 > 0:
            node.left = gen(k - 1, vals)
        return node

    def dump(n, depth, out):
        if n:
            out.append("-" * depth + str(n.val))
            dump(n.left, depth + 1, out)
            dump(n.right, depth + 1, out)

    for _ in range(100):
        k = r.randint(1, 9)
        t = gen(k, iter(r.sample(range(1, 100), k)))
        out = []
        dump(t, 0, out)
        assert _shape(f("".join(out))) == _shape(t)


@test("Trees:subtree-sums")
def _(ns):
    f = ns["find_tilt"]
    assert f(_tree([1, 2, 3])) == 1 and f(_tree([4, 2, 9, 3, 5, None, 7])) == 15
    r = random.Random(466)
    for _ in range(150):
        t = _random_tree(r, r.randint(0, 10))

        def total(n):
            return 0 if n is None else n.val + total(n.left) + total(n.right)

        assert f(t) == sum(abs(total(n.left) - total(n.right)) for n in _preorder(t))


@test("Trees:subtree-sums#Maximum product of a split")
def _(ns):
    f = ns["max_product"]
    assert f(_tree([1, 2, 3, 4, 5, 6])) == 110
    r = random.Random(467)
    for _ in range(150):
        t = _random_tree(r, r.randint(2, 10), lo=1, hi=9)

        def total(n):
            return 0 if n is None else n.val + total(n.left) + total(n.right)

        whole = total(t)
        want = max(total(n) * (whole - total(n)) for n in _preorder(t) if n is not t) % (10**9 + 7)
        assert f(t) == want


@test("Trees:flatten")
def _(ns):
    f = ns["flatten"]
    r = random.Random(468)
    for _ in range(150):
        t = _random_tree(r, r.randint(0, 11))
        want = [n.val for n in _preorder(t)]
        f(t)
        got, cur = [], t
        while cur:
            assert cur.left is None
            got.append(cur.val)
            cur = cur.right
        assert got == want


@test("Trees:valid-tree")
def _(ns):
    f = ns["validate_binary_tree_nodes"]
    assert f(4, [1, -1, 3, -1], [2, -1, -1, -1]) is True and f(4, [1, -1, 3, -1], [2, 3, -1, -1]) is False and f(2, [1, 0], [-1, -1]) is False
    r = random.Random(469)
    for _ in range(400):
        n = r.randint(1, 6)
        left = [r.choice([-1] * 2 + list(range(n))) for _ in range(n)]
        right = [r.choice([-1] * 2 + list(range(n))) for _ in range(n)]
        want = False
        for root in range(n):
            seen, stack, ok = set(), [root], True
            while stack and ok:
                u = stack.pop()
                if u in seen:
                    ok = False
                    break
                seen.add(u)
                stack += [c for c in (left[u], right[u]) if c != -1]
            if ok and len(seen) == n:
                want = True
        assert f(n, left[:], right[:]) is want, (n, left, right)


@test("Trees:from-traversals#Inorder and postorder")
def _(ns):
    f = ns["build_tree_post"]
    r = random.Random(470)
    for _ in range(100):
        t = _random_tree(r, r.randint(1, 10), distinct=True, lo=1, hi=60)
        assert _shape(f(_rec_order(t, "in"), _rec_order(t, "post"))) == _shape(t)


@test("Trees:from-traversals#Preorder and postorder")
def _(ns):
    f = ns["construct_from_pre_post"]
    r = random.Random(471)
    for _ in range(100):
        t = _random_tree(r, r.randint(1, 10), distinct=True, lo=1, hi=60)
        pre, post = _rec_order(t, "pre"), _rec_order(t, "post")
        got = f(pre[:], post[:])
        assert _rec_order(got, "pre") == pre and _rec_order(got, "post") == post


@test("Trees:hierarchy")
def _(ns):
    f = ns["num_of_minutes"]
    assert f(1, 0, [-1], [0]) == 0 and f(6, 2, [2, 2, -1, 2, 2, 2], [0, 0, 1, 0, 0, 0]) == 1
    r = random.Random(472)
    for _ in range(150):
        n = r.randint(1, 10)
        manager = [-1] + [r.randrange(i) for i in range(1, n)]
        inform = [r.randint(0, 5) for _ in range(n)]
        best = 0
        for v in range(n):
            tot, u = 0, v
            while u != -1:
                tot += inform[u]
                u = manager[u]
            best = max(best, tot)
        assert f(n, 0, manager[:], inform[:]) == best


@test("Trees:labelled")
def _(ns):
    f = ns["path_in_zig_zag_tree"]
    assert f(14) == [1, 3, 4, 14] and f(26) == [1, 2, 6, 10, 26] and f(1) == [1]
    # build the zigzag numbering level by level
    label_at = {}
    for level in range(1, 8):
        lo, hi = 1 << (level - 1), (1 << level) - 1
        row = list(range(lo, hi + 1))
        if level % 2 == 0:
            row.reverse()
        for pos, v in enumerate(row):
            label_at[(level, pos)] = v
    for (level, pos), v in label_at.items():
        path, lv, p = [], level, pos
        while lv >= 1:
            path.append(label_at[(lv, p)])
            lv, p = lv - 1, p // 2
        assert f(v) == path[::-1], v


@test("Trees:remove-subtree-heights")
def _(ns):
    f = ns["tree_queries"]
    assert f(_tree([1, 3, 4, 2, None, 6, 5, None, None, None, None, None, 7]), [4]) == [2]
    r = random.Random(473)
    for _ in range(100):
        t = _random_tree(r, r.randint(2, 11), distinct=True, lo=1, hi=60)
        qs = [n.val for n in _preorder(t) if n is not t]
        want = []
        for q in qs:
            def without(n):
                if n is None or n.val == q:
                    return None
                return TreeNode(n.val, without(n.left), without(n.right))
            want.append(_height_edges(without(t)))
        assert f(t, qs) == want


@test("Trees:remove-node-product")
def _(ns):
    f = ns["count_highest_score_nodes"]
    assert f([-1, 2, 0, 2, 0]) == 3 and f([-1, 2, 0]) == 2
    r = random.Random(474)
    for _ in range(150):
        n = r.randint(1, 9)
        parents = [-1] + [r.randrange(i) for i in range(1, n)]
        best, count = 0, 0
        for v in range(n):
            comp = list(range(n))

            def find(x):
                while comp[x] != x:
                    x = comp[x]
                return x

            for i in range(1, n):
                if i != v and parents[i] != v:
                    comp[find(i)] = find(parents[i])
            sizes = {}
            for i in range(n):
                if i != v:
                    sizes[find(i)] = sizes.get(find(i), 0) + 1
            score = 1
            for s in sizes.values():
                score *= s
            if score > best:
                best, count = score, 1
            elif score == best:
                count += 1
        assert f(parents[:]) == count


@test("Trees:path-parity")
def _(ns):
    f = ns["count_palindrome_paths"]
    assert f([-1, 0, 0, 1, 1, 2], "acaabc") == 8 and f([-1, 0, 0, 0, 0], "aaaaa") == 10
    r = random.Random(475)
    for _ in range(100):
        n = r.randint(1, 9)
        parent = [-1] + [r.randrange(i) for i in range(1, n)]
        s = "a" + "".join(r.choice("abc") for _ in range(n - 1))
        want = 0
        for u in range(n):
            for v in range(u + 1, n):
                anc_u, x = [], u
                while x != -1:
                    anc_u.append(x)
                    x = parent[x]
                y = v
                below_v = []
                while y not in anc_u:
                    below_v.append(y)
                    y = parent[y]
                below_u = anc_u[: anc_u.index(y)]
                letters = [s[k] for k in below_u + below_v]
                if sum(1 for c in set(letters) if letters.count(c) % 2) <= 1:
                    want += 1
        assert f(parent[:], s) == want


@test("Trees:binary-lifting")
def _(ns):
    cls = ns["TreeAncestor"]
    r = random.Random(476)
    for _ in range(60):
        n = r.randint(1, 12)
        parent = [-1] + [r.randrange(i) for i in range(1, n)]
        ta = cls(n, parent[:])
        for _ in range(20):
            node, k = r.randrange(n), r.randint(0, 14)
            want, cur = node, k
            while cur and want != -1:
                want = parent[want]
                cur -= 1
            assert ta.getKthAncestor(node, k) == (want if cur == 0 else -1)


class _NI:
    def __init__(self, v):
        self.v = v

    def isInteger(self):
        return not isinstance(self.v, list)

    def getInteger(self):
        return self.v

    def getList(self):
        return self.v


def _to_ni(x):
    return _NI([_to_ni(y) for y in x]) if isinstance(x, list) else _NI(x)


def _flat(x):
    return [z for y in x for z in _flat(y)] if isinstance(x, list) else [x]


@test("Trees:lazy-iterators")
def _(ns):
    cls = ns["NestedIterator"]
    r = random.Random(477)

    def gen(depth):
        return [gen(depth - 1) if depth and r.random() < 0.4 else r.randint(0, 9) for _ in range(r.randint(0, 4))]

    for _ in range(150):
        data = gen(3)
        it, got = cls([_to_ni(x) for x in data]), []
        while it.hasNext():
            if r.random() < 0.3:
                assert it.hasNext()  # asking again must not skip anything
            got.append(it.next())
        assert got == _flat(data)


@test("Trees:lazy-iterators#Peeking iterator")
def _(ns):
    cls = ns["PeekingIterator"]

    class It:
        def __init__(self, xs):
            self.xs, self.i = xs, 0

        def hasNext(self):
            return self.i < len(self.xs)

        def next(self):
            self.i += 1
            return self.xs[self.i - 1]

    r = random.Random(478)
    for _ in range(100):
        xs = [r.randint(0, 9) for _ in range(r.randint(0, 6))]
        p, got = cls(It(xs)), []
        while p.hasNext():
            assert p.peek() == xs[len(got)]
            got.append(p.next())
        assert got == xs


@test("Trees:insertion-orders")
def _(ns):
    f = ns["num_of_ways"]
    assert f([2, 1, 3]) == 1 and f([3, 4, 5, 1, 2]) == 5 and f([1, 2, 3]) == 0
    r = random.Random(479)

    def shape(seq):
        root = None
        for v in seq:
            node = TreeNode(v)
            if root is None:
                root = node
                continue
            cur = root
            while True:
                side = "left" if v < cur.val else "right"
                if getattr(cur, side) is None:
                    setattr(cur, side, node)
                    break
                cur = getattr(cur, side)
        return _shape(root)

    for _ in range(40):
        seq = r.sample(range(1, 20), r.randint(1, 6))
        want = sum(1 for p in _it.permutations(seq) if shape(p) == shape(seq)) - 1
        assert f(seq[:]) == want % (10**9 + 7)


# ---- heap / priority queue (extras) ---------------------------------------------------------------------------------

import heapq as _hq  # noqa: E402

H = "Heap / Priority Queue"


@test(f"{H}:top-k-key")
def _(ns):
    f = ns["top_k_frequent"]
    assert f(["i", "love", "leetcode", "i", "love", "coding"], 2) == ["i", "love"]
    r = random.Random(500)
    for _ in range(150):
        w = [r.choice("abcdef") for _ in range(r.randint(1, 15))]
        k = r.randint(1, len(set(w)))
        cnt = {x: w.count(x) for x in set(w)}
        assert f(w[:], k) == sorted(cnt, key=lambda x: (-cnt[x], x))[:k]


@test(f"{H}:top-k-key#K closest points (max-heap of size k)")
def _(ns):
    f = ns["k_closest"]
    r = random.Random(501)
    for _ in range(150):
        pts = [[r.randint(-9, 9), r.randint(-9, 9)] for _ in range(r.randint(1, 10))]
        k = r.randint(1, len(pts))
        got = sorted(x * x + y * y for x, y in f([p[:] for p in pts], k))
        assert got == sorted(x * x + y * y for x, y in pts)[:k]


@test(f"{H}:top-k-key#K closest elements (window)")
def _(ns):
    f = ns["find_closest_elements"]
    assert f([1, 2, 3, 4, 5], 4, 3) == [1, 2, 3, 4] and f([1, 1, 2, 3, 4, 5], 4, -1) == [1, 1, 2, 3]
    r = random.Random(502)
    for _ in range(300):
        arr = sorted(r.randint(-8, 8) for _ in range(r.randint(1, 10)))
        k, x = r.randint(1, len(arr)), r.randint(-10, 10)
        want = sorted(sorted(arr, key=lambda v: (abs(v - x), v))[:k])
        assert f(arr[:], k, x) == want


@test(f"{H}:frontier")
def _(ns):
    f = ns["k_smallest_pairs"]
    assert f([1, 7, 11], [2, 4, 6], 3) == [[1, 2], [1, 4], [1, 6]] and f([1, 1, 2], [1, 2, 3], 2) == [[1, 1], [1, 1]]
    r = random.Random(503)
    for _ in range(200):
        a = sorted(r.randint(0, 9) for _ in range(r.randint(0, 5)))
        b = sorted(r.randint(0, 9) for _ in range(r.randint(0, 5)))
        k = r.randint(1, 8)
        got = f(a[:], b[:], k)
        want = sorted(([x, y] for x in a for y in b), key=lambda p: p[0] + p[1])[:k]
        assert [x + y for x, y in got] == [x + y for x, y in want] and len(got) == len(want)


@test(f"{H}:frontier#Kth smallest in a sorted matrix")
def _(ns):
    f = ns["kth_smallest"]
    assert f([[1, 5, 9], [10, 11, 13], [12, 13, 15]], 8) == 13
    r = random.Random(504)
    for _ in range(150):
        m = [sorted(r.randint(0, 20) for _ in range(3)) for _ in range(r.randint(1, 4))]
        flat = sorted(v for row in m for v in row)
        k = r.randint(1, len(flat))
        assert f([row[:] for row in m], k) == flat[k - 1]


@test(f"{H}:frontier#Ugly numbers (merge the multiples)")
def _(ns):
    f = ns["nth_super_ugly_number"]
    assert f(12, [2, 7, 13, 19]) == 32 and f(1, [2, 3, 5]) == 1
    for primes in ([2, 3, 5], [2, 7, 13, 19]):
        want, x = [], 1
        while len(want) < 40:
            y = x
            for p in primes:
                while y % p == 0:
                    y //= p
            if y == 1:
                want.append(x)
            x += 1
        for n in range(1, 41):
            assert f(n, primes[:]) == want[n - 1]


@test(f"{H}:own-heap")
def _(ns):
    cls = ns["MinHeap"]
    r = random.Random(505)
    for _ in range(100):
        items = [r.randint(-20, 20) for _ in range(r.randint(0, 12))]
        h = cls(items)
        ref = items[:]
        _hq.heapify(ref)
        for _ in range(r.randint(0, 12)):
            if r.random() < 0.5 or not ref:
                v = r.randint(-20, 20)
                h.push(v)
                _hq.heappush(ref, v)
            else:
                assert h.pop() == _hq.heappop(ref)
            assert len(h) == len(ref)
        assert [h.pop() for _ in range(len(ref))] == sorted(ref)


@test(f"{H}:own-heap#Heap sort in place")
def _(ns):
    f = ns["heap_sort"]
    r = random.Random(506)
    for _ in range(150):
        a = [r.randint(-9, 9) for _ in range(r.randint(0, 15))]
        b = a[:]
        assert f(b) == sorted(a) and b == sorted(a)


@test(f"{H}:lazy-design")
def _(ns):
    cls = ns["FoodRatings"]
    t = cls(["kimchi", "miso", "sushi", "moussaka", "ramen", "bulgogi"], ["korean", "japanese", "japanese", "greek", "japanese", "korean"], [9, 12, 8, 15, 14, 7])
    assert t.highestRated("korean") == "kimchi" and t.highestRated("japanese") == "ramen"
    t.changeRating("sushi", 16)
    assert t.highestRated("japanese") == "sushi"
    t.changeRating("ramen", 16)
    assert t.highestRated("japanese") == "ramen"
    r = random.Random(507)
    for _ in range(60):
        foods = [f"f{i}" for i in range(6)]
        cuis = [r.choice("ab") for _ in foods]
        rat = [r.randint(1, 5) for _ in foods]
        t, cur = cls(foods, cuis, rat[:]), dict(zip(foods, rat))
        for _ in range(20):
            if r.random() < 0.5:
                f_, v = r.choice(foods), r.randint(1, 5)
                t.changeRating(f_, v)
                cur[f_] = v
            else:
                c = r.choice("ab")
                pool = [f_ for f_ in foods if cuis[foods.index(f_)] == c]
                if pool:
                    assert t.highestRated(c) == min(pool, key=lambda x: (-cur[x], x))


@test(f"{H}:lazy-design#Number containers")
def _(ns):
    r = random.Random(508)
    for _ in range(100):
        nc, at = ns["NumberContainers"](), {}
        for _ in range(25):
            if r.random() < 0.6:
                i, v = r.randint(1, 6), r.randint(1, 3)
                nc.change(i, v)
                at[i] = v
            else:
                v = r.randint(1, 3)
                idx = [i for i, x in at.items() if x == v]
                assert nc.find(v) == (min(idx) if idx else -1)


@test(f"{H}:lazy-design#Stock price (latest, max, min)")
def _(ns):
    r = random.Random(509)
    for _ in range(100):
        sp, price = ns["StockPrice"](), {}
        for _ in range(20):
            t, p = r.randint(1, 8), r.randint(1, 9)
            sp.update(t, p)
            price[t] = p
            assert sp.current() == price[max(price)] and sp.maximum() == max(price.values()) and sp.minimum() == min(price.values())


def _dijkstra_bottleneck(grid, step, start_cost):
    rows, cols = len(grid), len(grid[0])
    best = {(0, 0): start_cost}
    heap = [(start_cost, 0, 0)]
    while heap:
        c, r, k = _hq.heappop(heap)
        if c > best[(r, k)]:
            continue
        for a, b in ((r + 1, k), (r - 1, k), (r, k + 1), (r, k - 1)):
            if 0 <= a < rows and 0 <= b < cols:
                n = step(c, grid[r][k], grid[a][b])
                if n < best.get((a, b), 10**9):
                    best[(a, b)] = n
                    _hq.heappush(heap, (n, a, b))
    return best[(rows - 1, cols - 1)]


@test(f"{H}:minimax-path")
def _(ns):
    f = ns["minimum_effort_path"]
    assert f([[1, 2, 2], [3, 8, 2], [5, 3, 5]]) == 2 and f([[1, 2, 3], [3, 8, 4], [5, 3, 5]]) == 1
    r = random.Random(510)
    for _ in range(100):
        g = _grid(r, r.randint(1, 4), r.randint(1, 4), [1, 3, 5, 9])
        assert f([row[:] for row in g]) == _dijkstra_bottleneck(g, lambda c, a, b: max(c, abs(a - b)), 0)


@test(f"{H}:minimax-path#Swim in rising water")
def _(ns):
    f = ns["swim_in_water"]
    assert f([[0, 2], [1, 3]]) == 3
    r = random.Random(511)
    for _ in range(100):
        n = r.randint(1, 4)
        vals = r.sample(range(n * n), n * n)
        g = [vals[i * n:(i + 1) * n] for i in range(n)]
        assert f([row[:] for row in g]) == _dijkstra_bottleneck(g, lambda c, a, b: max(c, b), g[0][0])


@test(f"{H}:minimax-path#Maximise the minimum on a path")
def _(ns):
    f = ns["maximum_minimum_path"]
    assert f([[5, 4, 5], [1, 2, 6], [7, 4, 6]]) == 4 and f([[2, 2, 1, 2, 2, 2], [1, 2, 2, 2, 1, 2]]) == 2
    r = random.Random(512)
    for _ in range(100):
        g = _grid(r, r.randint(1, 4), r.randint(1, 4), [1, 3, 5, 9])
        neg = [[-v for v in row] for row in g]
        want = -_dijkstra_bottleneck(neg, lambda c, a, b: max(c, b), neg[0][0])
        assert f([row[:] for row in g]) == want


@test(f"{H}:sort-key-heap")
def _(ns):
    f = ns["max_performance"]
    assert f(6, [2, 10, 3, 1, 5, 8], [5, 4, 3, 9, 7, 2], 2) == 60 and f(6, [2, 10, 3, 1, 5, 8], [5, 4, 3, 9, 7, 2], 3) == 68
    r = random.Random(513)
    for _ in range(150):
        n = r.randint(1, 7)
        sp = [r.randint(1, 9) for _ in range(n)]
        ef = [r.randint(1, 9) for _ in range(n)]
        k = r.randint(1, n)
        want = max(sum(sp[i] for i in c) * min(ef[i] for i in c) for j in range(1, k + 1) for c in _it.combinations(range(n), j))
        assert f(n, sp[:], ef[:], k) == want % (10**9 + 7)


@test(f"{H}:sort-key-heap#Maximum subsequence score")
def _(ns):
    f = ns["max_score"]
    assert f([1, 3, 3, 2], [2, 1, 3, 4], 3) == 12 and f([4, 2, 3, 1, 1], [7, 5, 10, 9, 6], 1) == 30
    r = random.Random(514)
    for _ in range(150):
        n = r.randint(1, 7)
        a = [r.randint(0, 9) for _ in range(n)]
        b = [r.randint(0, 9) for _ in range(n)]
        k = r.randint(1, n)
        want = max(sum(a[i] for i in c) * min(b[i] for i in c) for c in _it.combinations(range(n), k))
        assert f(a[:], b[:], k) == want


@test(f"{H}:sort-key-heap#Minimum cost to hire k workers")
def _(ns):
    f = ns["mincost_to_hire_workers"]
    assert abs(f([10, 20, 5], [70, 50, 30], 2) - 105.0) < 1e-6 and abs(f([3, 1, 10, 10, 1], [4, 8, 2, 2, 7], 3) - 30.66667) < 1e-4
    r = random.Random(515)
    for _ in range(150):
        n = r.randint(1, 6)
        q = [r.randint(1, 9) for _ in range(n)]
        w = [r.randint(1, 20) for _ in range(n)]
        k = r.randint(1, n)
        best = float("inf")
        for c in _it.combinations(range(n), k):
            ratio = max(w[i] / q[i] for i in c)
            best = min(best, ratio * sum(q[i] for i in c))
        assert abs(f(q[:], w[:], k) - best) < 1e-6


@test(f"{H}:two-ends")
def _(ns):
    f = ns["total_cost"]
    assert f([17, 12, 10, 2, 7, 2, 11, 20, 8], 3, 4) == 11 and f([1, 2, 4, 1], 3, 3) == 4
    r = random.Random(516)
    for _ in range(300):
        c = [r.randint(1, 9) for _ in range(r.randint(1, 10))]
        k, cand = r.randint(1, len(c)), r.randint(1, 5)
        rest, total = list(range(len(c))), 0
        for _ in range(k):
            pool = rest[:cand] + rest[max(cand, len(rest) - cand):] if len(rest) > cand else rest[:]
            pool = sorted(set(rest[:cand]) | set(rest[-cand:]))
            pick = min(pool, key=lambda i: (c[i], i))
            total += c[pick]
            rest.remove(pick)
        assert f(c[:], k, cand) == total, (c, k, cand)


@test(f"{H}:marginal-gain")
def _(ns):
    f = ns["max_average_ratio"]
    assert abs(f([[1, 2], [3, 5], [2, 2]], 2) - 0.78333) < 1e-4 and abs(f([[2, 4], [3, 9], [4, 5], [2, 10]], 4) - 0.53485) < 1e-4
    r = random.Random(517)
    for _ in range(100):
        cl = []
        for _ in range(r.randint(1, 3)):
            t = r.randint(1, 5)
            cl.append([r.randint(1, t), t])
        extra = r.randint(0, 4)
        best = 0
        for alloc in _it.product(range(extra + 1), repeat=len(cl)):
            if sum(alloc) == extra:
                best = max(best, sum((p + a) / (t + a) for (p, t), a in zip(cl, alloc)) / len(cl))
        assert abs(f([c[:] for c in cl], extra) - best) < 1e-9


@test(f"{H}:order-book")
def _(ns):
    f = ns["get_number_of_backlog_orders"]
    assert f([[10, 5, 0], [15, 2, 1], [25, 1, 1], [30, 4, 0]]) == 6 and f([[7, 1000000000, 1], [15, 3, 0], [5, 999999995, 0], [5, 1, 1]]) == 999999984
    r = random.Random(518)
    for _ in range(200):
        orders = [[r.randint(1, 6), r.randint(1, 4), r.randint(0, 1)] for _ in range(r.randint(1, 8))]
        buys, sells = [], []
        for price, amt, kind in orders:
            if kind == 0:
                while amt and sells and min(s[0] for s in sells) <= price:
                    s = min(sells)
                    take = min(s[1], amt)
                    amt -= take
                    s[1] -= take
                    if s[1] == 0:
                        sells.remove(s)
                if amt:
                    buys.append([price, amt])
            else:
                while amt and buys and max(b[0] for b in buys) >= price:
                    b = max(buys)
                    take = min(b[1], amt)
                    amt -= take
                    b[1] -= take
                    if b[1] == 0:
                        buys.remove(b)
                if amt:
                    sells.append([price, amt])
        assert f([o[:] for o in orders]) == sum(b[1] for b in buys) + sum(s[1] for s in sells)


@test(f"{H}:servers")
def _(ns):
    f = ns["assign_tasks"]
    assert f([3, 3, 2], [1, 2, 3, 2, 1, 2]) == [2, 2, 0, 2, 1, 2] and f([5, 1, 4, 3, 2], [2, 1, 2, 4, 5, 2, 1]) == [1, 4, 1, 4, 1, 3, 2]
    r = random.Random(519)
    for _ in range(200):
        servers = [r.randint(1, 5) for _ in range(r.randint(1, 4))]
        tasks = [r.randint(1, 5) for _ in range(r.randint(1, 8))]
        free_at, out = [0] * len(servers), []
        t = 0
        for j, d in enumerate(tasks):
            t = max(t, j)
            avail = [i for i in range(len(servers)) if free_at[i] <= t]
            if not avail:
                t = max(t, min(free_at))
                avail = [i for i in range(len(servers)) if free_at[i] <= t]
            pick = min(avail, key=lambda i: (servers[i], i))
            out.append(pick)
            free_at[pick] = t + d
        assert f(servers[:], tasks[:]) == out


# ---- stack (extras) -------------------------------------------------------------------------------------------------

def _next_greater(a, circular=False):
    n = len(a)
    out = []
    for i in range(n):
        v = -1
        rng = range(1, n) if circular else range(1, n - i)
        for d in rng:
            x = a[(i + d) % n]
            if x > a[i]:
                v = x
                break
        out.append(v)
    return out


@test("Stack:next-greater")
def _(ns):
    f = ns["next_greater_elements"]
    assert f([1, 2, 1]) == [2, -1, 2] and f([1, 2, 3, 4, 3]) == [2, 3, 4, -1, 4]
    r = random.Random(600)
    for _ in range(200):
        a = [r.randint(0, 6) for _ in range(r.randint(1, 9))]
        assert f(a[:]) == _next_greater(a, True)


@test("Stack:next-greater#Next greater element I")
def _(ns):
    f = ns["next_greater_element"]
    assert f([4, 1, 2], [1, 3, 4, 2]) == [-1, 3, -1]
    r = random.Random(601)
    for _ in range(150):
        b = r.sample(range(10), r.randint(1, 8))
        a = r.sample(b, r.randint(1, len(b)))
        want = [next((x for x in b[b.index(v) + 1:] if x > v), -1) for v in a]
        assert f(a[:], b[:]) == want


@test("Stack:next-greater#Final prices (next smaller or equal)")
def _(ns):
    f = ns["final_prices"]
    assert f([8, 4, 6, 2, 3]) == [4, 2, 4, 2, 3]
    r = random.Random(602)
    for _ in range(200):
        p = [r.randint(1, 9) for _ in range(r.randint(1, 9))]
        want = [p[i] - next((p[j] for j in range(i + 1, len(p)) if p[j] <= p[i]), 0) for i in range(len(p))]
        assert f(p[:]) == want


def _max_rect_brute(m):
    best = 0
    R, C = len(m), len(m[0])
    for r1 in range(R):
        for r2 in range(r1, R):
            for c1 in range(C):
                for c2 in range(c1, C):
                    if all(m[i][j] in ("1", 1) for i in range(r1, r2 + 1) for j in range(c1, c2 + 1)):
                        best = max(best, (r2 - r1 + 1) * (c2 - c1 + 1))
    return best


@test("Stack:histogram-rows")
def _(ns):
    f = ns["maximal_rectangle"]
    assert f([["1", "0", "1", "0", "0"], ["1", "0", "1", "1", "1"], ["1", "1", "1", "1", "1"], ["1", "0", "0", "1", "0"]]) == 6 and f([]) == 0
    r = random.Random(603)
    for _ in range(150):
        m = [[r.choice("01") for _ in range(r.randint(1, 5))] for _ in range(1)]
        c = len(m[0])
        m = [[r.choice("01") for _ in range(c)] for _ in range(r.randint(1, 5))]
        assert f([row[:] for row in m]) == _max_rect_brute(m)


@test("Stack:histogram-rows#Count submatrices of ones")
def _(ns):
    f = ns["num_submat"]
    assert f([[1, 0, 1], [1, 1, 0], [1, 1, 0]]) == 13
    r = random.Random(604)
    for _ in range(100):
        c = r.randint(1, 4)
        m = [[r.randint(0, 1) for _ in range(c)] for _ in range(r.randint(1, 4))]
        R, C = len(m), c
        want = sum(1 for r1 in range(R) for r2 in range(r1, R) for c1 in range(C) for c2 in range(c1, C)
                   if all(m[i][j] for i in range(r1, r2 + 1) for j in range(c1, c2 + 1)))
        assert f([row[:] for row in m]) == want


@test("Stack:ramp")
def _(ns):
    f = ns["max_width_ramp"]
    assert f([6, 0, 8, 2, 1, 5]) == 4 and f([9, 8, 1, 0, 1, 9, 4, 0, 4, 1]) == 7
    r = random.Random(605)
    for _ in range(300):
        a = [r.randint(0, 8) for _ in range(r.randint(1, 10))]
        want = max([j - i for i in range(len(a)) for j in range(i, len(a)) if a[i] <= a[j]])
        assert f(a[:]) == want


@test("Stack:ramp#132 pattern")
def _(ns):
    f = ns["find132pattern"]
    assert f([1, 2, 3, 4]) is False and f([3, 1, 4, 2]) is True and f([-1, 3, 2, 0]) is True
    r = random.Random(606)
    for _ in range(300):
        a = [r.randint(-5, 5) for _ in range(r.randint(1, 8))]
        want = any(a[i] < a[k] < a[j] for i in range(len(a)) for j in range(i + 1, len(a)) for k in range(j + 1, len(a)))
        assert f(a[:]) is want


def _balanced(s):
    d = 0
    for ch in s:
        d += 1 if ch == "(" else -1
        if d < 0:
            return False
    return d == 0


def _valid_strings(n):
    out = []

    def go(s, o, c):
        if len(s) == 2 * n:
            out.append(s)
            return
        if o < n:
            go(s + "(", o + 1, c)
        if c < o:
            go(s + ")", o, c + 1)

    go("", 0, 0)
    return out


@test("Stack:parens-depth")
def _(ns):
    f = ns["score_of_parentheses"]
    assert f("()") == 1 and f("(())") == 2 and f("()()") == 2 and f("(()(()))") == 6

    def brute(s):
        if s == "()":
            return 1
        d = 0
        for i, ch in enumerate(s):
            d += 1 if ch == "(" else -1
            if d == 0:
                return brute(s[1:i]) * 2 + (brute(s[i + 1:]) if s[i + 1:] else 0) if i > 1 else 1 + (brute(s[i + 1:]) if s[i + 1:] else 0)

    for n in range(1, 6):
        for s in _valid_strings(n):
            assert f(s) == brute(s), s


@test("Stack:parens-depth#Remove outermost parentheses")
def _(ns):
    f = ns["remove_outer_parentheses"]
    assert f("(()())(())") == "()()()" and f("()()") == ""
    for n in range(1, 6):
        for s in _valid_strings(n):
            parts, d, st = [], 0, 0
            for i, ch in enumerate(s):
                d += 1 if ch == "(" else -1
                if d == 0:
                    parts.append(s[st + 1:i])
                    st = i + 1
            assert f(s) == "".join(parts)


@test("Stack:parens-depth#Split into two valid strings")
def _(ns):
    f = ns["max_depth_after_split"]
    for n in range(1, 6):
        for s in _valid_strings(n):
            g = f(s)
            groups = [[ch for ch, k in zip(s, g) if k == v] for v in (0, 1)]
            assert all(_balanced("".join(x)) for x in groups)

            def depth(x):
                d = m = 0
                for ch in x:
                    d += 1 if ch == "(" else -1
                    m = max(m, d)
                return m

            full = depth(s)
            assert max(depth(x) for x in groups) == (full + 1) // 2


@test("Stack:valid-length")
def _(ns):
    f = ns["longest_valid_parentheses"]
    assert f("(()") == 2 and f(")()())") == 4 and f("") == 0
    r = random.Random(607)
    for _ in range(300):
        s = "".join(r.choice("()") for _ in range(r.randint(0, 12)))
        want = max([j - i for i in range(len(s) + 1) for j in range(i, len(s) + 1) if _balanced(s[i:j])] or [0])
        assert f(s) == want


@test("Stack:run-length")
def _(ns):
    f = ns["remove_duplicates"]
    assert f("deeedbbcccbdaa", 3) == "aa" and f("pbbcggttciiippooaais", 2) == "ps"
    r = random.Random(608)
    for _ in range(200):
        s = "".join(r.choice("abc") for _ in range(r.randint(0, 12)))
        k = r.randint(2, 4)
        t = s
        while True:
            u = t
            for ch in "abc":
                u = u.replace(ch * k, "", 1) if ch * k in u else u
            if u == t:
                break
            t = u
        # the stack and the repeated removal agree when removals are applied leftmost first; compare to a direct simulation
        st = []
        for ch in s:
            st.append(ch)
            if len(st) >= k and len(set(st[-k:])) == 1:
                del st[-k:]
        assert f(s, k) == "".join(st)


@test("Stack:run-length#Make the string great")
def _(ns):
    f = ns["make_good"]
    assert f("leEeetcode") == "leetcode" and f("abBAcC") == "" and f("s") == "s"
    r = random.Random(609)
    for _ in range(200):
        s = "".join(r.choice("aAbB") for _ in range(r.randint(0, 10)))
        t = s
        while True:
            u = next((t[:i] + t[i + 2:] for i in range(len(t) - 1) if t[i] != t[i + 1] and t[i].lower() == t[i + 1].lower()), None)
            if u is None:
                break
            t = u
        assert f(s) == t


@test("Stack:run-length#Remove a pattern repeatedly")
def _(ns):
    f = ns["remove_occurrences"]
    assert f("daabcbaabcbc", "abc") == "dab" and f("axxxxyyyyb", "xy") == "ab"
    r = random.Random(610)
    for _ in range(200):
        s = "".join(r.choice("abc") for _ in range(r.randint(0, 12)))
        part = "".join(r.choice("abc") for _ in range(r.randint(1, 3)))
        t = s
        while part in t:
            t = t.replace(part, "", 1)
        assert f(s, part) == t


@test("Stack:call-stack")
def _(ns):
    f = ns["exclusive_time"]
    assert f(2, ["0:start:0", "1:start:2", "1:end:5", "0:end:6"]) == [3, 4]
    assert f(1, ["0:start:0", "0:start:2", "0:end:5", "0:start:6", "0:end:6", "0:end:7"]) == [8]
    assert f(2, ["0:start:0", "0:start:2", "0:end:5", "1:start:6", "1:end:6", "0:end:7"]) == [7, 1]
    r = random.Random(611)
    for _ in range(100):
        t, logs, stack, work = 0, [], [], [0] * 3
        for _ in range(r.randint(1, 6)):
            if stack and r.random() < 0.5:
                fid = stack.pop()
                work[fid] += 0
                logs.append(f"{fid}:end:{t}")
                t += 1
            else:
                stack.append(r.randrange(3))
                logs.append(f"{stack[-1]}:start:{t}")
                t += r.randint(0, 2)
        while stack:
            logs.append(f"{stack.pop()}:end:{t}")
            t += 1
        # brute force: every tick belongs to the function on top of the stack at that tick
        want, st, cur = [0] * 3, [], 0
        events = [(l.split(":")[0], l.split(":")[1], int(l.split(":")[2])) for l in logs]
        tick = 0
        for fid, kind, at in events:
            fid = int(fid)
            if kind == "start":
                while tick < at:
                    if st:
                        want[st[-1]] += 1
                    tick += 1
                st.append(fid)
            else:
                while tick <= at:
                    want[st[-1]] += 1
                    tick += 1
                st.pop()
        assert f(3, logs) == want, logs


@test("Stack:call-stack#Longest absolute file path")
def _(ns):
    f = ns["length_longest_path"]
    assert f("dir\n\tsubdir1\n\tsubdir2\n\t\tfile.ext") == 20
    assert f("dir\n\tsubdir1\n\t\tfile1.ext\n\t\tsubsubdir1\n\tsubdir2\n\t\tsubsubdir2\n\t\t\tfile2.ext") == 32 and f("a") == 0


@test("Stack:call-stack#Simplify path")
def _(ns):
    f = ns["simplify_path"]
    assert f("/home/") == "/home" and f("/../") == "/" and f("/home//foo/") == "/home/foo" and f("/a/./b/../../c/") == "/c"


@test("Stack:two-stack-cursor")
def _(ns):
    cls = ns["TextEditor"]
    r = random.Random(612)
    for _ in range(100):
        e, text, cur = cls(), [], 0
        for _ in range(15):
            op = r.choice("adlr")
            if op == "a":
                t = "".join(r.choice("xyz") for _ in range(r.randint(1, 4)))
                e.addText(t)
                text[cur:cur] = list(t)
                cur += len(t)
            elif op == "d":
                k = r.randint(1, 5)
                got = e.deleteText(k)
                k2 = min(k, cur)
                assert got == k2
                del text[cur - k2:cur]
                cur -= k2
            elif op == "l":
                k = r.randint(1, 5)
                cur = max(0, cur - k)
                assert e.cursorLeft(k) == "".join(text[max(0, cur - 10):cur])
            else:
                k = r.randint(1, 5)
                cur = min(len(text), cur + k)
                assert e.cursorRight(k) == "".join(text[max(0, cur - 10):cur])


@test("Stack:two-stack-cursor#Browser history")
def _(ns):
    cls = ns["BrowserHistory"]
    r = random.Random(613)
    for _ in range(100):
        h, pages, at = cls("home"), ["home"], 0
        for i in range(15):
            op = r.choice("vbf")
            if op == "v":
                h.visit(f"p{i}")
                pages = pages[:at + 1] + [f"p{i}"]
                at += 1
            elif op == "b":
                k = r.randint(1, 4)
                at = max(0, at - k)
                assert h.back(k) == pages[at]
            else:
                k = r.randint(1, 4)
                at = min(len(pages) - 1, at + k)
                assert h.forward(k) == pages[at]


@test("Stack:lazy-increment")
def _(ns):
    cls = ns["CustomStack"]
    r = random.Random(614)
    for _ in range(150):
        cap = r.randint(1, 5)
        s, ref = cls(cap), []
        for _ in range(25):
            op = r.choice("ppi")
            if op == "p" and r.random() < 0.6:
                x = r.randint(0, 9)
                s.push(x)
                if len(ref) < cap:
                    ref.append(x)
            elif op == "i":
                k, v = r.randint(1, 6), r.randint(1, 5)
                s.increment(k, v)
                for i in range(min(k, len(ref))):
                    ref[i] += v
            else:
                assert s.pop() == (ref.pop() if ref else -1)


@test("Stack:holding-buffer")
def _(ns):
    f = ns["validate_stack_sequences"]
    assert f([1, 2, 3, 4, 5], [4, 5, 3, 2, 1]) is True and f([1, 2, 3, 4, 5], [4, 3, 5, 1, 2]) is False
    r = random.Random(615)
    for _ in range(300):
        n = r.randint(0, 6)
        pushed = list(range(n))
        popped = pushed[:]
        r.shuffle(popped)
        seen = set()
        want = False

        def go(i, st, j):
            if j == n:
                return True
            if st and st[-1] == popped[j] and go(i, st[:-1], j + 1):
                return True
            return i < n and go(i + 1, st + [pushed[i]], j)

        want = go(0, [], 0)
        assert f(pushed[:], popped[:]) is want


@test("Stack:holding-buffer#Robot prints the smallest string")
def _(ns):
    f = ns["robot_with_string"]
    assert f("zza") == "azz" and f("bac") == "abc" and f("bdda") == "addb"
    r = random.Random(616)
    for _ in range(300):
        s = "".join(r.choice("abcd") for _ in range(r.randint(1, 7)))

        def best(i, st):
            out = [("".join(reversed(st)))] if i == len(s) else []
            if i < len(s):
                out += [best(i + 1, st + [s[i]])]
            if st:
                rest = best(i, st[:-1])
                out += [st[-1] + rest]
            return min(out)

        assert f(s) == best(0, [])


@test("Stack:chunks")
def _(ns):
    f = ns["max_chunks_to_sorted"]
    assert f([5, 4, 3, 2, 1]) == 1 and f([2, 1, 3, 4, 4]) == 4
    r = random.Random(617)
    for _ in range(300):
        a = [r.randint(0, 5) for _ in range(r.randint(1, 8))]
        best = 1
        s = sorted(a)
        for mask in range(1 << (len(a) - 1)):
            cuts = [0] + [i + 1 for i in range(len(a) - 1) if mask >> i & 1] + [len(a)]
            if all(sorted(a[x:y]) == s[x:y] for x, y in zip(cuts, cuts[1:])):
                best = max(best, len(cuts) - 1)
        assert f(a[:]) == best


@test("Stack:chunks#Shortest unsorted subarray")
def _(ns):
    f = ns["find_unsorted_subarray"]
    assert f([2, 6, 4, 8, 10, 9, 15]) == 5 and f([1, 2, 3, 4]) == 0 and f([1]) == 0
    r = random.Random(618)
    for _ in range(300):
        a = [r.randint(0, 6) for _ in range(r.randint(1, 8))]
        s = sorted(a)
        diff = [i for i in range(len(a)) if a[i] != s[i]]
        assert f(a[:]) == (diff[-1] - diff[0] + 1 if diff else 0)


@test("Stack:deque-prefix")
def _(ns):
    f = ns["shortest_subarray"]
    assert f([1], 1) == 1 and f([1, 2], 4) == -1 and f([2, -1, 2], 3) == 3
    r = random.Random(619)
    for _ in range(300):
        a = [r.randint(-4, 6) for _ in range(r.randint(1, 9))]
        k = r.randint(1, 8)
        want = min([j - i for i in range(len(a)) for j in range(i + 1, len(a) + 1) if sum(a[i:j]) >= k] or [-1])
        assert f(a[:], k) == want


@test("Stack:deque-prefix#Two deques: max and min in the window")
def _(ns):
    f = ns["longest_subarray"]
    assert f([8, 2, 4, 7], 4) == 2 and f([10, 1, 2, 4, 7, 2], 5) == 4 and f([4, 2, 2, 2, 4, 4, 2, 2], 0) == 3
    r = random.Random(620)
    for _ in range(300):
        a = [r.randint(0, 9) for _ in range(r.randint(1, 10))]
        lim = r.randint(0, 6)
        want = max(j - i for i in range(len(a)) for j in range(i + 1, len(a) + 1) if max(a[i:j]) - min(a[i:j]) <= lim)
        assert f(a[:], lim) == want


@test("Stack:parser")
def _(ns):
    f = ns["parse_ternary"]
    assert f("T?2:3") == "2" and f("F?1:T?4:5") == "4" and f("T?T?F:5:3") == "F"

    def gen(r, d):
        if d == 0 or r.random() < 0.3:
            return r.choice("0123456789TF")
        return r.choice("TF") + "?" + gen(r, d - 1) + ":" + gen(r, d - 1)

    def ev(e):
        def go(i):  # returns (value, next index)
            c = e[i]
            if i + 1 < len(e) and e[i + 1] == "?":
                a, j = go(i + 2)
                b, k = go(j + 1)
                return (a if c == "T" else b), k
            return c, i + 1

        return go(0)[0]

    r = random.Random(621)
    for _ in range(200):
        e = gen(r, 3)
        assert f(e) == ev(e), e


@test("Stack:parser#Boolean expression")
def _(ns):
    f = ns["parse_bool_expr"]
    assert f("&(|(f))") is False and f("|(f,f,f,t)") is True and f("!(&(f,t))") is True
    r = random.Random(622)

    def gen(d):
        if d == 0 or r.random() < 0.3:
            return r.choice("tf")
        op = r.choice("!&|")
        k = 1 if op == "!" else r.randint(1, 3)
        return op + "(" + ",".join(gen(d - 1) for _ in range(k)) + ")"

    def ev(e):
        def go(i):
            if e[i] in "tf":
                return e[i] == "t", i + 1
            op = e[i]
            i += 2
            vals = []
            while True:
                v, i = go(i)
                vals.append(v)
                if e[i] == ",":
                    i += 1
                else:
                    break
            return (not vals[0] if op == "!" else all(vals) if op == "&" else any(vals)), i + 1

        return go(0)[0]

    for _ in range(300):
        e = gen(3)
        assert f(e) is ev(e), e


@test("Stack:parser#Mini parser (nested integers)")
def _(ns):
    f = ns["deserialize"]
    assert f("324") == 324 and f("[123,[456,[789]]]") == [123, [456, [789]]] and f("[-1,[]]") == [-1, []] and f("[]") == []
    r = random.Random(623)

    def gen(d):
        if d == 0 or r.random() < 0.4:
            return r.randint(-50, 99)
        return [gen(d - 1) for _ in range(r.randint(0, 3))]

    def dump(x):
        return str(x) if isinstance(x, int) else "[" + ",".join(dump(y) for y in x) + "]"

    for _ in range(300):
        x = [gen(3) for _ in range(r.randint(0, 3))]
        assert f(dump(x)) == x, dump(x)


@test("Stack:encoded-index")
def _(ns):
    f = ns["decode_at_index"]
    assert f("leet2code3", 10) == "o" and f("ha22", 5) == "h" and f("a2345678999999999999999", 1) == "a"
    r = random.Random(624)
    for _ in range(300):
        s = ""
        for _ in range(r.randint(1, 5)):
            s += "".join(r.choice("abc") for _ in range(r.randint(1, 3))) + str(r.randint(2, 3))
        s = s[:-1] if r.random() < 0.5 else s
        if not s[0].isalpha():
            continue
        t = ""
        for ch in s:
            t = t * int(ch) if ch.isdigit() else t + ch
            if len(t) > 3000:
                break
        else:
            for k in range(1, min(len(t), 40) + 1):
                assert f(s, k) == t[k - 1], (s, k)


# ---- sliding window (extras) ----------------------------------------------------------------------------------------

SW = "Sliding Window"


@test(f"{SW}:both-ends")
def _(ns):
    f = ns["min_operations"]
    assert f([1, 1, 4, 2, 3], 5) == 2 and f([5, 6, 7, 8, 9], 4) == -1 and f([3, 2, 20, 1, 1, 3], 10) == 5
    r = random.Random(700)
    for _ in range(300):
        a = [r.randint(1, 5) for _ in range(r.randint(1, 8))]
        x = r.randint(1, 20)
        best = -1
        for l in range(len(a) + 1):
            for rr in range(len(a) - l + 1):
                if sum(a[:l]) + sum(a[len(a) - rr:]) == x and (best == -1 or l + rr < best):
                    best = l + rr
        assert f(a[:], x) == best, (a, x)


@test(f"{SW}:both-ends#Take k of each character")
def _(ns):
    f = ns["take_characters"]
    assert f("aabaaaacaabc", 2) == 8 and f("a", 1) == -1
    r = random.Random(701)
    for _ in range(300):
        s = "".join(r.choice("abc") for _ in range(r.randint(1, 10)))
        k = r.randint(0, 3)
        best = -1
        for l in range(len(s) + 1):
            for rr in range(len(s) - l + 1):
                t = s[:l] + s[len(s) - rr:]
                if all(t.count(c) >= k for c in "abc") and (best == -1 or l + rr < best):
                    best = l + rr
        assert f(s, k) == best, (s, k)


@test(f"{SW}:circular")
def _(ns):
    f = ns["decrypt"]
    assert f([5, 7, 1, 4], 3) == [12, 10, 16, 13] and f([1, 2, 3, 4], 0) == [0, 0, 0, 0] and f([2, 4, 9, 3], -2) == [12, 5, 6, 13]
    r = random.Random(702)
    for _ in range(300):
        c = [r.randint(1, 9) for _ in range(r.randint(1, 8))]
        n = len(c)
        k = r.randint(-(n - 1), n - 1) if n > 1 else 0
        want = [sum(c[(i + d) % n] for d in range(1, k + 1)) if k > 0 else sum(c[(i - d) % n] for d in range(1, -k + 1)) for i in range(n)]
        assert f(c[:], k) == want, (c, k)


@test(f"{SW}:circular#Alternating groups II")
def _(ns):
    f = ns["number_of_alternating_groups"]
    assert f([0, 1, 0, 1, 0], 3) == 3 and f([0, 1, 0, 0, 1, 0, 1], 6) == 2 and f([1, 1, 0, 1], 4) == 0
    r = random.Random(703)
    for _ in range(300):
        n = r.randint(3, 9)
        c = [r.randint(0, 1) for _ in range(n)]
        k = r.randint(3, n)
        want = sum(1 for i in range(n) if all(c[(i + j) % n] != c[(i + j + 1) % n] for j in range(k - 1)))
        assert f(c[:], k) == want, (c, k)


@test(f"{SW}:circular#Shortest subarray in an infinite array")
def _(ns):
    f = ns["min_size_subarray"]
    assert f([1, 2, 3], 5) == 2 and f([1, 1, 1, 2, 3], 4) == 2 and f([2, 4, 6, 8], 3) == -1
    r = random.Random(704)
    for _ in range(300):
        a = [r.randint(1, 5) for _ in range(r.randint(1, 5))]
        t = r.randint(1, 30)
        rep = a * (t // min(a) + 2)
        best = -1
        for i in range(len(a)):
            run = 0
            for j in range(i, len(rep)):
                run += rep[j]
                if run == t:
                    best = j - i + 1 if best == -1 else min(best, j - i + 1)
                    break
                if run > t:
                    break
        assert f(a[:], t) == best, (a, t)


@test(f"{SW}:cost-budget")
def _(ns):
    f = ns["max_frequency"]
    assert f([1, 2, 4], 5) == 3 and f([1, 4, 8, 13], 5) == 2 and f([3, 9, 6], 2) == 1
    r = random.Random(705)
    for _ in range(300):
        a = [r.randint(1, 8) for _ in range(r.randint(1, 8))]
        k = r.randint(0, 12)
        best = 1
        for target in range(1, 10):
            cost = sorted((target - x for x in a if x <= target), reverse=True)
            cost.sort()
            used, cnt = 0, 0
            for c in cost:
                if used + c > k:
                    break
                used += c
                cnt += 1
            best = max(best, cnt)
        assert f(a[:], k) == best, (a, k)


@test(f"{SW}:cost-budget#Equal substrings within a budget")
def _(ns):
    f = ns["equal_substring"]
    assert f("abcd", "bcdf", 3) == 3 and f("abcd", "cdef", 3) == 1 and f("abcd", "acde", 0) == 1
    r = random.Random(706)
    for _ in range(300):
        n = r.randint(1, 8)
        s = "".join(r.choice("abcd") for _ in range(n))
        t = "".join(r.choice("abcd") for _ in range(n))
        m = r.randint(0, 6)
        best = max([j - i for i in range(n) for j in range(i + 1, n + 1) if sum(abs(ord(s[x]) - ord(t[x])) for x in range(i, j)) <= m] or [0])
        assert f(s, t, m) == best


@test(f"{SW}:cost-budget#Confusion of an exam")
def _(ns):
    f = ns["max_consecutive_answers"]
    assert f("TTFF", 2) == 4 and f("TFFT", 1) == 3 and f("TTFTTFTT", 1) == 5
    r = random.Random(707)
    for _ in range(300):
        s = "".join(r.choice("TF") for _ in range(r.randint(1, 10)))
        k = r.randint(0, 4)
        best = max(j - i for i in range(len(s)) for j in range(i + 1, len(s) + 1) if min(s[i:j].count("T"), s[i:j].count("F")) <= k)
        assert f(s, k) == best


@test(f"{SW}:cost-budget#Make the array continuous")
def _(ns):
    f = ns["min_operations_continuous"]
    assert f([4, 2, 5, 3]) == 0 and f([1, 2, 3, 5, 6]) == 1 and f([1, 10, 100, 1000]) == 3
    r = random.Random(708)
    for _ in range(200):
        a = [r.randint(1, 12) for _ in range(r.randint(1, 6))]
        n = len(a)
        best = n
        for lo in range(-2, 16):
            vals = set(range(lo, lo + n))
            keep = len(vals & set(a))
            # duplicates must be replaced, so only distinct values inside the range stay
            best = min(best, n - keep)
        assert f(a[:]) == best, a


@test(f"{SW}:prefix-hash")
def _(ns):
    f = ns["subarray_sum"]
    assert f([1, 1, 1], 2) == 2 and f([1, 2, 3], 3) == 2
    r = random.Random(709)
    for _ in range(300):
        a = [r.randint(-3, 4) for _ in range(r.randint(1, 10))]
        k = r.randint(-3, 6)
        assert f(a[:], k) == sum(1 for i in range(len(a)) for j in range(i + 1, len(a) + 1) if sum(a[i:j]) == k)


@test(f"{SW}:prefix-hash#Sums divisible by k")
def _(ns):
    f = ns["subarrays_div_by_k"]
    assert f([4, 5, 0, -2, -3, 1], 5) == 7 and f([5], 9) == 0
    r = random.Random(710)
    for _ in range(300):
        a = [r.randint(-6, 6) for _ in range(r.randint(1, 10))]
        k = r.randint(1, 6)
        assert f(a[:], k) == sum(1 for i in range(len(a)) for j in range(i + 1, len(a) + 1) if sum(a[i:j]) % k == 0)


@test(f"{SW}:prefix-hash#Nice subarrays (k odd numbers)")
def _(ns):
    f = ns["number_of_subarrays"]
    assert f([1, 1, 2, 1, 1], 3) == 2 and f([2, 4, 6], 1) == 0
    r = random.Random(711)
    for _ in range(300):
        a = [r.randint(0, 5) for _ in range(r.randint(1, 10))]
        k = r.randint(1, 3)
        assert f(a[:], k) == sum(1 for i in range(len(a)) for j in range(i + 1, len(a) + 1) if sum(x & 1 for x in a[i:j]) == k)


@test(f"{SW}:anagram")
def _(ns):
    f = ns["find_anagrams"]
    assert f("cbaebabacd", "abc") == [0, 6] and f("abab", "ab") == [0, 1, 2]
    r = random.Random(712)
    for _ in range(300):
        s = "".join(r.choice("abc") for _ in range(r.randint(0, 12)))
        p = "".join(r.choice("abc") for _ in range(r.randint(1, 4)))
        want = [i for i in range(len(s) - len(p) + 1) if sorted(s[i:i + len(p)]) == sorted(p)]
        assert f(s, p) == want


@test(f"{SW}:anagram#Concatenation of all words")
def _(ns):
    f = ns["find_substring"]
    assert f("barfoothefoobarman", ["foo", "bar"]) == [0, 9] and f("wordgoodgoodgoodbestword", ["word", "good", "best", "word"]) == []
    r = random.Random(713)
    for _ in range(300):
        words = ["".join(r.choice("ab") for _ in range(2)) for _ in range(r.randint(1, 3))]
        s = "".join(r.choice("ab") for _ in range(r.randint(0, 12)))
        w, m = 2, len(words)
        want = [i for i in range(len(s) - w * m + 1) if sorted(s[i + j * w:i + j * w + w] for j in range(m)) == sorted(words)]
        assert f(s, words[:]) == want, (s, words)


@test(f"{SW}:rolling-hash")
def _(ns):
    f = ns["find_repeated_dna"]
    assert sorted(f("AAAAACCCCCAAAAACCCCCCAAAAAGGGTTT")) == ["AAAAACCCCC", "CCCCCAAAAA"] and f("AAAAAAAAAAAAA") == ["AAAAAAAAAA"]
    r = random.Random(714)
    for _ in range(100):
        s = "".join(r.choice("ACGT") for _ in range(r.randint(0, 40)))
        seen, rep = set(), set()
        for i in range(len(s) - 9):
            w = s[i:i + 10]
            (rep if w in seen else seen).add(w)
        assert sorted(f(s)) == sorted(rep)


@test(f"{SW}:rolling-hash#Rabin-Karp substring search")
def _(ns):
    f = ns["str_str"]
    assert f("sadbutsad", "sad") == 0 and f("leetcode", "leeto") == -1 and f("a", "") == 0
    r = random.Random(715)
    for _ in range(300):
        h = "".join(r.choice("ab") for _ in range(r.randint(0, 12)))
        n = "".join(r.choice("ab") for _ in range(r.randint(1, 4)))
        assert f(h, n) == h.find(n)


@test(f"{SW}:answer-window")
def _(ns):
    f = ns["max_min_power"]
    assert f([1, 2, 4, 5, 0], 1, 2) == 5 and f([4, 4, 4, 4], 0, 3) == 4
    r = random.Random(716)
    for _ in range(150):
        n = r.randint(1, 5)
        st = [r.randint(0, 4) for _ in range(n)]
        rad, k = r.randint(0, 2), r.randint(0, 3)
        best = 0
        for alloc in _it.product(range(k + 1), repeat=n):
            if sum(alloc) != k:
                continue
            s2 = [a + b for a, b in zip(st, alloc)]
            power = [sum(s2[j] for j in range(max(0, i - rad), min(n, i + rad + 1))) for i in range(n)]
            best = max(best, min(power))
        assert f(st[:], rad, k) == best, (st, rad, k)


@test(f"{SW}:count-range")
def _(ns):
    f = ns["get_subarray_beauty"]
    assert f([1, -1, -3, -2, 3], 3, 2) == [-1, -2, -2] and f([-1, -2, -3, -4, -5], 2, 2) == [-1, -2, -3, -4]
    r = random.Random(717)
    for _ in range(200):
        a = [r.randint(-5, 5) for _ in range(r.randint(1, 10))]
        k = r.randint(1, len(a))
        x = r.randint(1, k)
        want = []
        for i in range(len(a) - k + 1):
            w = sorted(a[i:i + k])
            v = w[x - 1]
            want.append(v if v < 0 else 0)
        assert f(a[:], k, x) == want


@test(f"{SW}:count-range#Nearby almost duplicate (buckets)")
def _(ns):
    f = ns["contains_nearby_almost_duplicate"]
    assert f([1, 2, 3, 1], 3, 0) is True and f([1, 0, 1, 1], 1, 2) is True and f([1, 5, 9, 1, 5, 9], 2, 3) is False
    r = random.Random(718)
    for _ in range(300):
        a = [r.randint(-8, 8) for _ in range(r.randint(1, 8))]
        k, t = r.randint(1, 5), r.randint(0, 4)
        want = any(abs(a[i] - a[j]) <= t for i in range(len(a)) for j in range(i + 1, min(len(a), i + k + 1)))
        assert f(a[:], k, t) is want, (a, k, t)


@test(f"{SW}:count-from-right")
def _(ns):
    f = ns["count_subarrays"]
    assert f([1, 3, 2, 3, 3], 2) == 6 and f([1, 4, 2, 1], 3) == 0
    r = random.Random(719)
    for _ in range(300):
        a = [r.randint(1, 4) for _ in range(r.randint(1, 9))]
        k = r.randint(1, 3)
        top = max(a)
        want = sum(1 for i in range(len(a)) for j in range(i + 1, len(a) + 1) if a[i:j].count(top) >= k)
        assert f(a[:], k) == want


@test(f"{SW}:count-from-right#Fixed bounds (last seen positions)")
def _(ns):
    f = ns["count_subarrays_bounds"]
    assert f([1, 3, 5, 2, 7, 5], 1, 5) == 2 and f([1, 1, 1, 1], 1, 1) == 10
    r = random.Random(720)
    for _ in range(300):
        a = [r.randint(1, 5) for _ in range(r.randint(1, 9))]
        lo, hi = r.randint(1, 3), r.randint(3, 5)
        want = sum(1 for i in range(len(a)) for j in range(i + 1, len(a) + 1) if min(a[i:j]) == lo and max(a[i:j]) == hi)
        assert f(a[:], lo, hi) == want


@test(f"{SW}:count-from-right#Substrings with all of a, b, c")
def _(ns):
    f = ns["number_of_substrings"]
    assert f("abcabc") == 10 and f("aaacb") == 3 and f("abc") == 1
    r = random.Random(721)
    for _ in range(300):
        s = "".join(r.choice("abc") for _ in range(r.randint(1, 10)))
        want = sum(1 for i in range(len(s)) for j in range(i + 1, len(s) + 1) if set(s[i:j]) >= set("abc"))
        assert f(s) == want


@test(f"{SW}:deque-dp")
def _(ns):
    f = ns["count_partitions"]
    assert f([9, 4, 1, 3, 7], 4) == 6 and f([3, 3, 4], 0) == 2
    r = random.Random(722)
    for _ in range(300):
        a = [r.randint(1, 6) for _ in range(r.randint(1, 8))]
        k = r.randint(0, 4)
        n = len(a)
        dp = [1] + [0] * n
        for i in range(1, n + 1):
            for j in range(i):
                if max(a[j:i]) - min(a[j:i]) <= k:
                    dp[i] += dp[j]
        assert f(a[:], k) == dp[n] % (10**9 + 7)


@test(f"{SW}:deque-dp#Continuous subarrays")
def _(ns):
    f = ns["continuous_subarrays"]
    assert f([5, 4, 2, 4]) == 8 and f([1, 2, 3]) == 6
    r = random.Random(723)
    for _ in range(300):
        a = [r.randint(1, 7) for _ in range(r.randint(1, 9))]
        want = sum(1 for i in range(len(a)) for j in range(i + 1, len(a) + 1) if max(a[i:j]) - min(a[i:j]) <= 2)
        assert f(a[:]) == want


@test(f"{SW}:rows-pairs")
def _(ns):
    f = ns["num_submatrix_sum_target"]
    assert f([[0, 1, 0], [1, 1, 1], [0, 1, 0]], 0) == 4 and f([[1, -1], [-1, 1]], 0) == 5
    r = random.Random(724)
    for _ in range(100):
        c = r.randint(1, 4)
        m = [[r.randint(-2, 3) for _ in range(c)] for _ in range(r.randint(1, 4))]
        t = r.randint(-2, 4)
        R, C = len(m), c
        want = sum(1 for r1 in range(R) for r2 in range(r1, R) for c1 in range(C) for c2 in range(c1, C)
                   if sum(m[i][j] for i in range(r1, r2 + 1) for j in range(c1, c2 + 1)) == t)
        assert f([row[:] for row in m], t) == want


@test(f"{SW}:min-changes")
def _(ns):
    f = ns["minimum_recolors"]
    assert f("WBBWWBBWBW", 7) == 3 and f("WBWBBBW", 2) == 0
    r = random.Random(725)
    for _ in range(300):
        s = "".join(r.choice("WB") for _ in range(r.randint(1, 12)))
        k = r.randint(1, len(s))
        assert f(s, k) == min(s[i:i + k].count("W") for i in range(len(s) - k + 1))


@test(f"{SW}:min-changes#Group all 1s together (circular)")
def _(ns):
    f = ns["min_swaps"]
    assert f([0, 1, 1, 1, 0, 0, 1, 1, 0]) == 2 and f([0, 1, 1, 1, 0, 0, 1, 1, 0]) == 2 and f([1, 1, 0, 0, 1]) == 0
    r = random.Random(726)
    for _ in range(300):
        a = [r.randint(0, 1) for _ in range(r.randint(1, 10))]
        n, ones = len(a), sum(a)
        if ones in (0, n):
            assert f(a[:]) == 0
            continue
        want = min(sum(1 - a[(i + j) % n] for j in range(ones)) for i in range(n))
        assert f(a[:]) == want


@test(f"{SW}:min-changes#K-radius averages")
def _(ns):
    f = ns["get_averages"]
    assert f([7, 4, 3, 9, 1, 8, 5, 2, 6], 3) == [-1, -1, -1, 5, 4, 4, -1, -1, -1] and f([100000], 0) == [100000]
    r = random.Random(727)
    for _ in range(300):
        a = [r.randint(0, 20) for _ in range(r.randint(1, 10))]
        k = r.randint(0, 3)
        want = [sum(a[i - k:i + k + 1]) // (2 * k + 1) if i - k >= 0 and i + k < len(a) else -1 for i in range(len(a))]
        assert f(a[:], k) == want


# ---- linked list (extras) -------------------------------------------------------------------------------------------

LL = "Linked List"


def _rl(r, lo=0, hi=9, n=None):
    return [r.randint(lo, hi) for _ in range(r.randint(0, 9) if n is None else n)]


@test(f"{LL}:swap-groups")
def _(ns):
    f = ns["swap_pairs"]
    r = random.Random(800)
    for _ in range(100):
        a = _rl(r)
        h = _ll(a)
        nodes = _ll_nodes_list(h)
        out = f(h)
        want = []
        for i in range(0, len(a) - 1, 2):
            want += [a[i + 1], a[i]]
        if len(a) % 2:
            want.append(a[-1])
        assert _ll_vals(out) == want
        assert {id(x) for x in _ll_nodes_list(out)} == {id(x) for x in nodes}, "relink nodes, do not copy values"


def _ll_nodes_list(h):
    out = []
    while h:
        out.append(h)
        h = h.next
    return out


@test(f"{LL}:swap-groups#Reverse nodes in even-length groups")
def _(ns):
    f = ns["reverse_even_length_groups"]
    assert _ll_vals(f(_ll([5, 2, 6, 3, 9, 1, 7, 3, 8, 4]))) == [5, 6, 2, 3, 9, 1, 4, 8, 3, 7]
    r = random.Random(801)
    for _ in range(100):
        a = _rl(r, n=r.randint(1, 12))
        want, i, size = [], 0, 1
        while i < len(a):
            g = a[i:i + size]
            want += g[::-1] if len(g) % 2 == 0 else g
            i += size
            size += 1
        assert _ll_vals(f(_ll(a))) == want


@test(f"{LL}:sort-list")
def _(ns):
    f = ns["sort_list"]
    r = random.Random(802)
    for _ in range(150):
        a = _rl(r)
        assert _ll_vals(f(_ll(a))) == sorted(a)
    assert _ll_vals(f(_ll(list(range(3000, 0, -1))))) == list(range(1, 3001))


@test(f"{LL}:sort-list#Insertion sort")
def _(ns):
    f = ns["insertion_sort_list"]
    r = random.Random(803)
    for _ in range(150):
        a = _rl(r)
        assert _ll_vals(f(_ll(a))) == sorted(a)


@test(f"{LL}:partition")
def _(ns):
    f = ns["partition"]
    r = random.Random(804)
    for _ in range(150):
        a = _rl(r)
        x = r.randint(0, 9)
        want = [v for v in a if v < x] + [v for v in a if v >= x]
        assert _ll_vals(f(_ll(a), x)) == want


@test(f"{LL}:partition#Odd even linked list")
def _(ns):
    f = ns["odd_even_list"]
    r = random.Random(805)
    for _ in range(150):
        a = _rl(r)
        assert _ll_vals(f(_ll(a))) == a[0::2] + a[1::2]


@test(f"{LL}:partition#Rotate list")
def _(ns):
    f = ns["rotate_right"]
    r = random.Random(806)
    for _ in range(150):
        a = _rl(r)
        k = r.randint(0, 20)
        want = a[-(k % len(a)):] + a[:-(k % len(a))] if a and k % len(a) else a
        assert _ll_vals(f(_ll(a), k)) == want


@test(f"{LL}:remove-runs")
def _(ns):
    f = ns["delete_duplicates"]
    r = random.Random(807)
    for _ in range(150):
        a = sorted(_rl(r, 0, 5))
        want = [v for v in a if a.count(v) == 1]
        assert _ll_vals(f(_ll(a))) == want


@test(f"{LL}:remove-runs#Unsorted: remove values that repeat")
def _(ns):
    f = ns["delete_duplicates_unsorted"]
    r = random.Random(808)
    for _ in range(150):
        a = _rl(r, 0, 5)
        assert _ll_vals(f(_ll(a))) == [v for v in a if a.count(v) == 1]


@test(f"{LL}:remove-runs#Remove zero-sum runs (prefix sums)")
def _(ns):
    f = ns["remove_zero_sum_sublists"]
    assert _ll_vals(f(_ll([1, 2, -3, 3, 1]))) in ([3, 1], [1, 2, 1]) and _ll_vals(f(_ll([1, 2, 3, -3, 4]))) == [1, 2, 4]
    r = random.Random(809)
    for _ in range(200):
        a = _rl(r, -3, 3)
        out = _ll_vals(f(_ll(a)))
        # no consecutive run sums to zero, and the output is a subsequence of the input made by cutting zero-sum runs
        assert all(sum(out[i:j]) != 0 for i in range(len(out)) for j in range(i + 1, len(out) + 1))
        it = iter(a)
        assert all(v in it for v in out)


@test(f"{LL}:delete-by-rule")
def _(ns):
    f = ns["remove_nodes"]
    assert _ll_vals(f(_ll([5, 2, 13, 3, 8]))) == [13, 8] and _ll_vals(f(_ll([1, 1, 1, 1]))) == [1, 1, 1, 1]
    r = random.Random(810)
    for _ in range(150):
        a = _rl(r, 1, 9)
        want = [v for i, v in enumerate(a) if all(v >= w for w in a[i + 1:])]
        assert _ll_vals(f(_ll(a))) == want


@test(f"{LL}:delete-by-rule#Delete nodes present in an array")
def _(ns):
    f = ns["modified_list"]
    r = random.Random(811)
    for _ in range(150):
        a = _rl(r, 0, 6)
        gone = r.sample(range(7), r.randint(0, 4))
        assert _ll_vals(f(gone, _ll(a))) == [v for v in a if v not in gone]


@test(f"{LL}:delete-by-rule#Delete the middle node")
def _(ns):
    f = ns["delete_middle"]
    r = random.Random(812)
    for _ in range(100):
        a = _rl(r, 0, 9, n=r.randint(1, 9))
        want = a[:len(a) // 2] + a[len(a) // 2 + 1:]
        assert _ll_vals(f(_ll(a))) == want


@test(f"{LL}:delete-by-rule#Delete a node given only that node")
def _(ns):
    f = ns["delete_node"]
    r = random.Random(813)
    for _ in range(100):
        a = _rl(r, 0, 9, n=r.randint(2, 9))
        h = _ll(a)
        nodes = _ll_nodes_list(h)
        i = r.randrange(len(a) - 1)
        f(nodes[i])
        assert _ll_vals(h) == a[:i] + a[i + 1:]


def _digits(v):
    return [int(c) for c in str(v)]


@test(f"{LL}:number-lists")
def _(ns):
    f = ns["add_two_numbers"]
    r = random.Random(814)
    for _ in range(200):
        x, y = r.randint(0, 10**r.randint(1, 6)), r.randint(0, 10**r.randint(1, 6))
        assert _ll_vals(f(_ll(_digits(x)), _ll(_digits(y)))) == _digits(x + y)


@test(f"{LL}:number-lists#Plus one")
def _(ns):
    f = ns["plus_one"]
    r = random.Random(815)
    for _ in range(200):
        x = int("9" * r.randint(0, 3) + str(r.randint(0, 99)) + "9" * r.randint(0, 3)) if r.random() < 0.7 else r.randint(0, 999)
        assert _ll_vals(f(_ll(_digits(x)))) == _digits(x + 1)


@test(f"{LL}:number-lists#Double a number")
def _(ns):
    f = ns["double_it"]
    r = random.Random(816)
    for _ in range(200):
        x = r.randint(1, 10**r.randint(1, 8))
        assert _ll_vals(f(_ll(_digits(x)))) == _digits(2 * x)


class _MNode:
    def __init__(self, val):
        self.val, self.prev, self.next, self.child = val, None, None, None


@test(f"{LL}:flatten-levels")
def _(ns):
    f = ns["flatten"]
    r = random.Random(817)
    counter = [0]

    def build(depth):
        n = r.randint(1, 4)
        nodes = []
        for _ in range(n):
            counter[0] += 1
            nodes.append(_MNode(counter[0]))
        for a, b in zip(nodes, nodes[1:]):
            a.next, b.prev = b, a
        for nd in nodes:
            if depth and r.random() < 0.4:
                nd.child = build(depth - 1)
        return nodes[0]

    def order(h):
        out = []
        while h:
            out.append(h.val)
            if h.child:
                out += order(h.child)
            h = h.next
        return out

    for _ in range(100):
        counter[0] = 0
        head = build(3)
        want = order(head)
        out = f(head)
        got, prev, node = [], None, out
        while node:
            assert node.child is None and node.prev is prev
            got.append(node.val)
            prev, node = node, node.next
        assert got == want
    assert f(None) is None


@test(f"{LL}:split-parts")
def _(ns):
    f = ns["split_list_to_parts"]
    r = random.Random(818)
    for _ in range(150):
        a = _rl(r)
        k = r.randint(1, 6)
        parts = f(_ll(a), k)
        assert len(parts) == k
        got = [_ll_vals(p) for p in parts]
        size, extra = divmod(len(a), k)
        want, i = [], 0
        for j in range(k):
            ln = size + (j < extra)
            want.append(a[i:i + ln])
            i += ln
        assert got == want


@test(f"{LL}:split-parts#Linked list components")
def _(ns):
    f = ns["num_components"]
    assert f(_ll([0, 1, 2, 3]), [0, 1, 3]) == 2 and f(_ll([0, 1, 2, 3, 4]), [0, 3, 1, 4]) == 2
    r = random.Random(819)
    for _ in range(150):
        a = r.sample(range(10), r.randint(0, 8))
        sub = r.sample(range(10), r.randint(0, 6))
        want, run = 0, False
        for v in a:
            if v in sub:
                want += not run
                run = True
            else:
                run = False
        assert f(_ll(a), sub) == want


@test(f"{LL}:half-reverse")
def _(ns):
    f = ns["is_palindrome"]
    r = random.Random(820)
    for _ in range(200):
        a = _rl(r, 0, 2, n=r.randint(1, 8))
        if r.random() < 0.5:
            a = a + a[::-1][r.randint(0, 1):]
        assert f(_ll(a)) is (a == a[::-1])


@test(f"{LL}:half-reverse#Maximum twin sum")
def _(ns):
    f = ns["pair_sum"]
    assert f(_ll([5, 4, 2, 1])) == 6 and f(_ll([4, 2, 2, 3])) == 7
    r = random.Random(821)
    for _ in range(150):
        a = _rl(r, 1, 9, n=2 * r.randint(1, 5))
        assert f(_ll(a)) == max(a[i] + a[-1 - i] for i in range(len(a) // 2))


@test(f"{LL}:reservoir")
def _(ns):
    import random as _random
    cls = ns["Solution"]
    _random.seed(5)
    for n in (1, 2, 5):
        s = cls(_ll(list(range(n))))
        counts = [0] * n
        for _ in range(4000):
            counts[s.getRandom()] += 1
        assert all(abs(c - 4000 / n) < 4000 / n * 0.15 for c in counts), counts


@test(f"{LL}:splice-between")
def _(ns):
    f = ns["merge_in_between"]
    r = random.Random(822)
    for _ in range(150):
        a = _rl(r, 0, 9, n=r.randint(3, 9))
        lo = r.randint(1, len(a) - 2)
        hi = r.randint(lo, len(a) - 2)
        b = _rl(r, 10, 19, n=r.randint(1, 4))
        assert _ll_vals(f(_ll(a), lo, hi, _ll(b))) == a[:lo] + b + a[hi + 1:]


@test(f"{LL}:splice-between#Merge nodes between zeros")
def _(ns):
    f = ns["merge_nodes"]
    assert _ll_vals(f(_ll([0, 3, 1, 0, 4, 5, 2, 0]))) == [4, 11]
    r = random.Random(823)
    for _ in range(150):
        groups = [[r.randint(1, 5) for _ in range(r.randint(1, 4))] for _ in range(r.randint(1, 4))]
        a = [0]
        for g in groups:
            a += g + [0]
        assert _ll_vals(f(_ll(a))) == [sum(g) for g in groups]


@test(f"{LL}:splice-between#Swap the k-th from each end")
def _(ns):
    f = ns["swap_nodes"]
    r = random.Random(824)
    for _ in range(150):
        a = _rl(r, 0, 9, n=r.randint(1, 9))
        k = r.randint(1, len(a))
        want = a[:]
        want[k - 1], want[-k] = want[-k], want[k - 1]
        assert _ll_vals(f(_ll(a), k)) == want


@test(f"{LL}:splice-between#Critical points")
def _(ns):
    f = ns["nodes_between_critical_points"]
    assert f(_ll([3, 1])) == [-1, -1] and f(_ll([5, 3, 1, 2, 5, 1, 2])) == [1, 3] and f(_ll([1, 3, 2, 2, 3, 2, 2, 2, 7])) == [3, 3]
    r = random.Random(825)
    for _ in range(300):
        a = _rl(r, 1, 5, n=r.randint(2, 10))
        crit = [i for i in range(1, len(a) - 1) if (a[i] > a[i - 1] and a[i] > a[i + 1]) or (a[i] < a[i - 1] and a[i] < a[i + 1])]
        want = [-1, -1] if len(crit) < 2 else [min(y - x for x, y in zip(crit, crit[1:])), crit[-1] - crit[0]]
        assert f(_ll(a)) == want


@test(f"{LL}:bucket-list")
def _(ns):
    cls = ns["AllOne"]
    r = random.Random(826)
    for _ in range(100):
        t, cnt = cls(), {}
        for _ in range(40):
            k = r.choice("abcd")
            if r.random() < 0.6 or not cnt.get(k):
                t.inc(k)
                cnt[k] = cnt.get(k, 0) + 1
            else:
                t.dec(k)
                cnt[k] -= 1
                if cnt[k] == 0:
                    del cnt[k]
            if cnt:
                mx, mn = max(cnt.values()), min(cnt.values())
                assert cnt[t.getMaxKey()] == mx and cnt[t.getMinKey()] == mn
            else:
                assert t.getMaxKey() == "" and t.getMinKey() == ""


@test(f"{LL}:circular-loop")
def _(ns):
    f = ns["circular_array_loop"]
    assert f([2, -1, 1, 2, 2]) is True and f([-1, -2, -3, -4, -5, 6]) is False and f([1, -1, 5, 1, 4]) is True
    r = random.Random(827)
    for _ in range(300):
        a = [r.choice([-3, -2, -1, 1, 2, 3]) for _ in range(r.randint(1, 8))]
        n = len(a)
        want = False
        for s in range(n):
            seen, i = [], s
            while i not in seen:
                seen.append(i)
                i = (i + a[i]) % n
            cyc = seen[seen.index(i):]
            if len(cyc) > 1 and (all(a[j] > 0 for j in cyc) or all(a[j] < 0 for j in cyc)):
                want = True
        assert f(a[:]) is want, a


@test(f"{LL}:circular-loop#Happy number")
def _(ns):
    f = ns["is_happy"]
    assert f(19) is True and f(2) is False
    def ref(n):
        seen = set()
        while n != 1 and n not in seen:
            seen.add(n)
            n = sum(int(d) ** 2 for d in str(n))
        return n == 1
    for n in range(1, 200):
        assert f(n) is ref(n)


@test(f"{LL}:two-deque-queue")
def _(ns):
    cls = ns["FrontMiddleBackQueue"]
    r = random.Random(828)
    for _ in range(150):
        q, ref = cls(), []
        for i in range(30):
            op = r.choice(["pf", "pm", "pb", "qf", "qm", "qb"])
            n = len(ref)
            if op == "pf":
                q.pushFront(i)
                ref.insert(0, i)
            elif op == "pm":
                q.pushMiddle(i)
                ref.insert(n // 2, i)
            elif op == "pb":
                q.pushBack(i)
                ref.append(i)
            elif op == "qf":
                assert q.popFront() == (ref.pop(0) if ref else -1)
            elif op == "qm":
                assert q.popMiddle() == (ref.pop((n - 1) // 2) if ref else -1)
            else:
                assert q.popBack() == (ref.pop() if ref else -1)


# ---- binary search (extras) -----------------------------------------------------------------------------------------

BS = "Binary Search"


def _sorted_matrix(r, rows, cols, lo=-5, hi=9):
    m = [[r.randint(lo, hi) for _ in range(cols)] for _ in range(rows)]
    for row in m:
        row.sort()
    for j in range(cols):
        col = sorted(m[i][j] for i in range(rows))
        for i in range(rows):
            m[i][j] = col[i]
    for row in m:
        row.sort()  # keep rows sorted after sorting columns (a fixed point exists after a few passes)
    for _ in range(3):
        for j in range(cols):
            col = sorted(m[i][j] for i in range(rows))
            for i in range(rows):
                m[i][j] = col[i]
        for row in m:
            row.sort()
    return m


@test(f"{BS}:matrix-sorted")
def _(ns):
    f = ns["search_matrix"]
    r = random.Random(900)
    for _ in range(200):
        m = _sorted_matrix(r, r.randint(1, 5), r.randint(1, 5))
        t = r.randint(-6, 10)
        assert f([row[:] for row in m], t) is any(t in row for row in m)


@test(f"{BS}:matrix-sorted#Count negatives")
def _(ns):
    f = ns["count_negatives"]
    assert f([[4, 3, 2, -1], [3, 2, 1, -1], [1, 1, -1, -2], [-1, -1, -2, -3]]) == 8
    r = random.Random(901)
    for _ in range(200):
        m = _sorted_matrix(r, r.randint(1, 5), r.randint(1, 5))
        g = [row[::-1] for row in m[::-1]]  # non-increasing both ways
        assert f([row[:] for row in g]) == sum(v < 0 for row in g for v in row)


@test(f"{BS}:matrix-sorted#Kth smallest by value")
def _(ns):
    f = ns["kth_smallest"]
    assert f([[1, 5, 9], [10, 11, 13], [12, 13, 15]], 8) == 13
    r = random.Random(902)
    for _ in range(200):
        n = r.randint(1, 4)
        m = _sorted_matrix(r, n, n)
        flat = sorted(v for row in m for v in row)
        k = r.randint(1, n * n)
        assert f([row[:] for row in m], k) == flat[k - 1]


@test(f"{BS}:kth-by-count")
def _(ns):
    f = ns["smallest_distance_pair"]
    assert f([1, 3, 1], 1) == 0 and f([1, 1, 1], 2) == 0 and f([1, 6, 1], 3) == 5
    r = random.Random(903)
    for _ in range(200):
        a = [r.randint(0, 12) for _ in range(r.randint(2, 8))]
        k = r.randint(1, len(a) * (len(a) - 1) // 2)
        d = sorted(abs(x - y) for x, y in _it.combinations(a, 2))
        assert f(a[:], k) == d[k - 1]


@test(f"{BS}:kth-by-count#K-th smallest prime fraction")
def _(ns):
    f = ns["kth_smallest_prime_fraction"]
    assert f([1, 2, 3, 5], 3) == [2, 5] and f([1, 7], 1) == [1, 7]
    r = random.Random(904)
    for _ in range(100):
        arr = sorted([1] + r.sample([2, 3, 5, 7, 11, 13, 17], r.randint(1, 5)))
        pairs = sorted(((a, b) for a, b in _it.combinations(arr, 2)), key=lambda p: p[0] / p[1])
        k = r.randint(1, len(pairs))
        assert f(arr[:], k) == list(pairs[k - 1])


@test(f"{BS}:min-gap")
def _(ns):
    f = ns["max_distance"]
    assert f([1, 2, 3, 4, 7], 3) == 3 and f([5, 4, 3, 2, 1, 1000000000], 2) == 999999999
    r = random.Random(905)
    for _ in range(200):
        pos = r.sample(range(0, 30), r.randint(2, 7))
        m = r.randint(2, len(pos))
        best = max(min(b - a for a, b in zip(c, c[1:])) for c in _it.combinations(sorted(pos), m))
        assert f(pos[:], m) == best


@test(f"{BS}:min-gap#Cutting ribbons")
def _(ns):
    f = ns["max_length"]
    assert f([9, 7, 5], 3) == 5 and f([7, 5, 9], 4) == 4 and f([5, 7, 9], 22) == 0
    r = random.Random(906)
    for _ in range(200):
        a = [r.randint(1, 15) for _ in range(r.randint(1, 5))]
        k = r.randint(1, 12)
        want = max([L for L in range(1, max(a) + 1) if sum(x // L for x in a) >= k] or [0])
        assert f(a[:], k) == want


@test(f"{BS}:min-gap#House robber IV (minimise the maximum)")
def _(ns):
    f = ns["min_capability"]
    assert f([2, 3, 5, 9], 2) == 5 and f([2, 7, 9, 3, 1], 2) == 2
    r = random.Random(907)
    for _ in range(200):
        a = [r.randint(1, 15) for _ in range(r.randint(1, 8))]
        k = r.randint(1, (len(a) + 1) // 2)
        best = min(max(a[i] for i in c) for c in _it.combinations(range(len(a)), k) if all(y - x > 1 for x, y in zip(c, c[1:])))
        assert f(a[:], k) == best


@test(f"{BS}:time-to-finish")
def _(ns):
    f = ns["minimum_time"]
    assert f([1, 2, 3], 5) == 3 and f([2], 1) == 2
    r = random.Random(908)
    for _ in range(200):
        t = [r.randint(1, 6) for _ in range(r.randint(1, 4))]
        n = r.randint(1, 15)
        x = 1
        while sum(x // v for v in t) < n:
            x += 1
        assert f(t[:], n) == x


@test(f"{BS}:time-to-finish#Bouquets")
def _(ns):
    f = ns["min_days"]
    assert f([1, 10, 3, 10, 2], 3, 1) == 3 and f([1, 10, 3, 10, 2], 3, 2) == -1 and f([7, 7, 7, 7, 12, 7, 7], 2, 3) == 12
    r = random.Random(909)
    for _ in range(200):
        a = [r.randint(1, 9) for _ in range(r.randint(1, 8))]
        m, k = r.randint(1, 3), r.randint(1, 3)
        if m * k > len(a):
            assert f(a[:], m, k) == -1
            continue
        for day in range(1, 10):
            b, run = 0, 0
            for v in a:
                run = run + 1 if v <= day else 0
                if run == k:
                    b, run = b + 1, 0
            if b >= m:
                assert f(a[:], m, k) == day
                break


@test(f"{BS}:time-to-finish#Smallest divisor given a threshold")
def _(ns):
    f = ns["smallest_divisor"]
    assert f([1, 2, 5, 9], 6) == 5 and f([44, 22, 33, 11, 1], 5) == 44
    r = random.Random(910)
    for _ in range(200):
        a = [r.randint(1, 20) for _ in range(r.randint(1, 6))]
        th = r.randint(len(a), 40)
        d = 1
        while sum(-(-x // d) for x in a) > th:
            d += 1
        assert f(a[:], th) == d


@test(f"{BS}:time-to-finish#Minimum speed to arrive on time")
def _(ns):
    f = ns["min_speed_on_time"]
    assert f([1, 3, 2], 6) == 1 and f([1, 3, 2], 2.7) == 3 and f([1, 3, 2], 1.9) == -1
    r = random.Random(911)
    for _ in range(200):
        d = [r.randint(1, 9) for _ in range(r.randint(1, 4))]
        h = round(r.uniform(1, 12), 2)
        got = f(d[:], h)
        want = -1
        for v in range(1, 2000):
            if sum(-(-x // v) for x in d[:-1]) + d[-1] / v <= h:
                want = v
                break
        assert got == want, (d, h)


@test(f"{BS}:real-answer")
def _(ns):
    f = ns["my_sqrt"]
    for x in list(range(0, 200)) + [10**9, 2**31 - 1]:
        assert f(x) == int(x ** 0.5) if x < 2**52 else True
        import math
        assert f(x) == math.isqrt(x)


@test(f"{BS}:real-answer#Newton's method")
def _(ns):
    import math
    f = ns["my_sqrt_newton"]
    for x in list(range(0, 300)) + [10**9, 2**31 - 1, 10**12]:
        assert f(x) == math.isqrt(x)


@test(f"{BS}:real-answer#Separate squares (real line)")
def _(ns):
    f = ns["separate_squares"]
    assert abs(f([[0, 0, 1], [2, 2, 1]]) - 1.0) < 1e-4 and abs(f([[0, 0, 2], [1, 1, 1]]) - 1.16667) < 1e-4
    r = random.Random(912)
    for _ in range(50):
        sq = [[0, r.randint(0, 6), r.randint(1, 4)] for _ in range(r.randint(1, 4))]
        y = f([s[:] for s in sq])
        total = sum(l * l for _, _, l in sq)
        below = sum(l * min(max(y - yi, 0), l) for _, yi, l in sq)
        assert abs(below * 2 - total) < 1e-3


@test(f"{BS}:bisect-other")
def _(ns):
    cls = ns["SnapshotArray"]
    r = random.Random(913)
    for _ in range(100):
        n = r.randint(1, 4)
        s, cur, snaps = cls(n), [0] * n, []
        for _ in range(25):
            op = r.choice("ssg")
            if op == "s" and r.random() < 0.7:
                i, v = r.randrange(n), r.randint(1, 9)
                s.set(i, v)
                cur[i] = v
            elif op == "g" and snaps:
                sid = r.randrange(len(snaps))
                i = r.randrange(n)
                assert s.get(i, sid) == snaps[sid][i]
            else:
                assert s.snap() == len(snaps)
                snaps.append(cur[:])


@test(f"{BS}:bisect-other#Search suggestions (sorted words)")
def _(ns):
    f = ns["suggested_products"]
    assert f(["mobile", "mouse", "moneypot", "monitor", "mousepad"], "mouse") == [["mobile", "moneypot", "monitor"], ["mobile", "moneypot", "monitor"], ["mouse", "mousepad"], ["mouse", "mousepad"], ["mouse", "mousepad"]]
    r = random.Random(914)
    for _ in range(100):
        words = ["".join(r.choice("ab") for _ in range(r.randint(1, 4))) for _ in range(r.randint(1, 6))]
        q = "".join(r.choice("ab") for _ in range(r.randint(1, 4)))
        want = [sorted(w for w in words if w.startswith(q[:i + 1]))[:3] for i in range(len(q))]
        assert f(words[:], q) == want


@test(f"{BS}:bisect-other#Plates between candles")
def _(ns):
    f = ns["plates_between_candles"]
    assert f("**|**|***|", [[2, 5], [5, 9]]) == [2, 3]
    r = random.Random(915)
    for _ in range(150):
        s = "".join(r.choice("*|") for _ in range(r.randint(1, 14)))
        q = []
        for _ in range(4):
            a = r.randrange(len(s))
            q.append([a, r.randint(a, len(s) - 1)])
        want = []
        for a, b in q:
            seg = s[a:b + 1]
            if "|" in seg:
                lo, hi = seg.index("|"), seg.rindex("|")
                want.append(seg[lo:hi + 1].count("*"))
            else:
                want.append(0)
        assert f(s, [x[:] for x in q]) == want


@test(f"{BS}:lis-tails")
def _(ns):
    f = ns["length_of_lis"]
    assert f([10, 9, 2, 5, 3, 7, 101, 18]) == 4 and f([7, 7, 7]) == 1
    r = random.Random(916)
    for _ in range(200):
        a = [r.randint(0, 9) for _ in range(r.randint(0, 10))]
        dp = [1] * len(a)
        for i in range(len(a)):
            for j in range(i):
                if a[j] < a[i]:
                    dp[i] = max(dp[i], dp[j] + 1)
        assert f(a[:]) == max(dp, default=0)


@test(f"{BS}:lis-tails#Obstacle course (non-decreasing)")
def _(ns):
    f = ns["longest_obstacle_course"]
    assert f([1, 2, 3, 2]) == [1, 2, 3, 3] and f([2, 2, 1]) == [1, 2, 1]
    r = random.Random(917)
    for _ in range(200):
        a = [r.randint(0, 6) for _ in range(r.randint(1, 10))]
        dp = [1] * len(a)
        for i in range(len(a)):
            for j in range(i):
                if a[j] <= a[i]:
                    dp[i] = max(dp[i], dp[j] + 1)
        assert f(a[:]) == dp


@test(f"{BS}:lis-tails#Russian doll envelopes")
def _(ns):
    f = ns["max_envelopes"]
    assert f([[5, 4], [6, 4], [6, 7], [2, 3]]) == 3 and f([[1, 1], [1, 1], [1, 1]]) == 1
    r = random.Random(918)
    for _ in range(200):
        e = [[r.randint(1, 6), r.randint(1, 6)] for _ in range(r.randint(1, 7))]
        s = sorted(e)
        dp = [1] * len(s)
        for i in range(len(s)):
            for j in range(i):
                if s[j][0] < s[i][0] and s[j][1] < s[i][1]:
                    dp[i] = max(dp[i], dp[j] + 1)
        assert f([x[:] for x in e]) == max(dp)


@test(f"{BS}:sorted-then-bisect")
def _(ns):
    f = ns["count_fair_pairs"]
    assert f([0, 1, 7, 4, 4, 5], 3, 6) == 6 and f([1, 7, 9, 2, 5], 11, 11) == 1
    r = random.Random(919)
    for _ in range(200):
        a = [r.randint(-5, 9) for _ in range(r.randint(1, 9))]
        lo = r.randint(-5, 8)
        hi = r.randint(lo, 12)
        assert f(a[:], lo, hi) == sum(1 for x, y in _it.combinations(a, 2) if lo <= x + y <= hi)


@test(f"{BS}:sorted-then-bisect#Successful pairs of spells and potions")
def _(ns):
    f = ns["successful_pairs"]
    assert f([5, 1, 3], [1, 2, 3, 4, 5], 7) == [4, 0, 3]
    r = random.Random(920)
    for _ in range(200):
        sp = [r.randint(1, 9) for _ in range(r.randint(1, 5))]
        po = [r.randint(1, 9) for _ in range(r.randint(1, 6))]
        s = r.randint(1, 60)
        assert f(sp[:], po[:], s) == [sum(1 for p in po if x * p >= s) for x in sp]


@test(f"{BS}:sorted-then-bisect#Most profit assigning work")
def _(ns):
    f = ns["max_profit_assignment"]
    assert f([2, 4, 6, 8, 10], [10, 20, 30, 40, 50], [4, 5, 6, 7]) == 100
    r = random.Random(921)
    for _ in range(200):
        n = r.randint(1, 6)
        d = [r.randint(1, 9) for _ in range(n)]
        p = [r.randint(1, 9) for _ in range(n)]
        w = [r.randint(0, 10) for _ in range(r.randint(1, 5))]
        want = sum(max([p[i] for i in range(n) if d[i] <= x] or [0]) for x in w)
        assert f(d[:], p[:], w[:]) == want


@test(f"{BS}:first-true")
def _(ns):
    f = ns["first_bad_version"]
    for n in range(1, 40):
        for bad in range(1, n + 1):
            assert f(n, lambda v: v >= bad) == bad


@test(f"{BS}:first-true#H-index II")
def _(ns):
    f = ns["h_index"]
    assert f([0, 1, 3, 5, 6]) == 3 and f([1, 2, 100]) == 2 and f([0]) == 0
    r = random.Random(922)
    for _ in range(300):
        c = sorted(r.randint(0, 8) for _ in range(r.randint(1, 8)))
        assert f(c[:]) == max(h for h in range(len(c) + 1) if sum(1 for x in c if x >= h) >= h)


@test(f"{BS}:first-true#Smallest letter greater than target")
def _(ns):
    f = ns["next_greatest_letter"]
    assert f(["c", "f", "j"], "a") == "c" and f(["c", "f", "j"], "c") == "f" and f(["x", "x", "y", "y"], "z") == "x"
    r = random.Random(923)
    for _ in range(200):
        letters = sorted(r.choice("bdfhj") for _ in range(r.randint(2, 6)))
        t = r.choice("abcdefghijk")
        want = next((c for c in letters if c > t), letters[0])
        assert f(letters[:], t) == want


@test(f"{BS}:missing-count")
def _(ns):
    f = ns["find_kth_positive"]
    assert f([2, 3, 4, 7, 11], 5) == 9 and f([1, 2, 3, 4], 2) == 6
    r = random.Random(924)
    for _ in range(300):
        arr = sorted(r.sample(range(1, 20), r.randint(1, 8)))
        k = r.randint(1, 15)
        missing = [x for x in range(1, 60) if x not in arr]
        assert f(arr[:], k) == missing[k - 1]


@test(f"{BS}:missing-count#Single element in a sorted array")
def _(ns):
    f = ns["single_non_duplicate"]
    assert f([1, 1, 2, 3, 3, 4, 4, 8, 8]) == 2 and f([3, 3, 7, 7, 10, 11, 11]) == 10 and f([5]) == 5
    r = random.Random(925)
    for _ in range(200):
        vals = sorted(r.sample(range(30), r.randint(1, 6)))
        single = r.choice(vals)
        arr = sorted(v for v in vals for _ in range(1 if v == single else 2))
        assert f(arr[:]) == single


@test(f"{BS}:missing-count#Missing number in an arithmetic progression")
def _(ns):
    f = ns["missing_number"]
    assert f([5, 7, 11, 13]) == 9 and f([15, 13, 9]) == 11
    r = random.Random(926)
    for _ in range(200):
        n = r.randint(3, 9)
        a0, d = r.randint(-5, 5), r.choice([-3, -2, -1, 1, 2, 3])
        full = [a0 + i * d for i in range(n + 1)]
        j = r.randint(1, n - 1)
        arr = full[:j] + full[j + 1:]
        assert f(arr[:]) == full[j]


@test(f"{BS}:merge-count")
def _(ns):
    f = ns["reverse_pairs"]
    assert f([1, 3, 2, 3, 1]) == 2 and f([2, 4, 3, 5, 1]) == 3
    r = random.Random(927)
    for _ in range(200):
        a = [r.randint(-6, 6) for _ in range(r.randint(0, 10))]
        assert f(a[:]) == sum(1 for i in range(len(a)) for j in range(i + 1, len(a)) if a[i] > 2 * a[j])


@test(f"{BS}:merge-count#Count of smaller numbers after self")
def _(ns):
    f = ns["count_smaller"]
    assert f([5, 2, 6, 1]) == [2, 1, 1, 0] and f([-1, -1]) == [0, 0]
    r = random.Random(928)
    for _ in range(200):
        a = [r.randint(-6, 6) for _ in range(r.randint(1, 10))]
        assert f(a[:]) == [sum(1 for y in a[i + 1:] if y < a[i]) for i in range(len(a))]


# ---- bit manipulation (extras) --------------------------------------------------------------------------------------

BM = "Bit Manipulation"


@test(f"{BM}:single-number-ii")
def _(ns):
    f = ns["single_number"]
    assert f([2, 2, 3, 2]) == 3 and f([0, 1, 0, 1, 0, 1, 99]) == 99 and f([-2, -2, 1, 1, 4, 1, 4, 4, -4, -2]) == -4
    r = random.Random(1000)
    for _ in range(200):
        vals = r.sample(range(-20, 20), r.randint(1, 5))
        single = r.choice(vals)
        nums = [v for v in vals if v != single] * 3 + [single]
        r.shuffle(nums)
        assert f(nums[:]) == single


@test(f"{BM}:single-number-ii#Single number III (two singles)")
def _(ns):
    f = ns["single_number_iii"]
    r = random.Random(1001)
    for _ in range(200):
        vals = r.sample(range(-30, 30), r.randint(2, 7))
        a, b = vals[0], vals[1]
        nums = [v for v in vals[2:]] * 2 + [a, b]
        r.shuffle(nums)
        assert sorted(f(nums[:])) == sorted([a, b])


@test(f"{BM}:range-bits")
def _(ns):
    f = ns["range_bitwise_and"]
    assert f(5, 7) == 4 and f(0, 0) == 0 and f(1, 2147483647) == 0
    for lo in range(0, 40):
        for hi in range(lo, 60):
            want = lo
            for x in range(lo, hi + 1):
                want &= x
            assert f(lo, hi) == want


@test(f"{BM}:range-bits#Minimum array end")
def _(ns):
    f = ns["min_end"]
    assert f(3, 4) == 6 and f(2, 7) == 15
    for n in range(1, 8):
        for x in range(1, 20):
            arr = [x]
            while len(arr) < n:
                v = arr[-1] + 1
                while v & x != x:
                    v += 1
                arr.append(v)
            assert f(n, x) == arr[-1], (n, x)


@test(f"{BM}:range-bits#Minimize XOR")
def _(ns):
    f = ns["minimize_xor"]
    assert f(3, 5) == 3 and f(1, 12) == 3
    for n1 in range(1, 64):
        for n2 in range(1, 32):
            c = bin(n2).count("1")
            want = min((x for x in range(0, 256) if bin(x).count("1") == c), key=lambda x: x ^ n1)
            assert f(n1, n2) == want


@test(f"{BM}:hamming")
def _(ns):
    f = ns["total_hamming_distance"]
    assert f([4, 14, 2]) == 6 and f([4, 14, 4]) == 4
    r = random.Random(1002)
    for _ in range(100):
        a = [r.randint(0, 255) for _ in range(r.randint(1, 8))]
        assert f(a[:]) == sum(bin(x ^ y).count("1") for x, y in _it.combinations(a, 2))


@test(f"{BM}:hamming#Hamming distance of two numbers")
def _(ns):
    f = ns["hamming_distance"]
    for x in range(0, 40):
        for y in range(0, 40):
            assert f(x, y) == bin(x ^ y).count("1")


@test(f"{BM}:hamming#Complement of a number")
def _(ns):
    f = ns["find_complement"]
    assert f(5) == 2 and f(1) == 0 and f(0) == 1
    for n in range(1, 300):
        assert f(n) == int("".join("1" if c == "0" else "0" for c in bin(n)[2:]), 2)


@test(f"{BM}:xor-decode")
def _(ns):
    f = ns["find_array"]
    r = random.Random(1003)
    for _ in range(100):
        a = [r.randint(0, 99) for _ in range(r.randint(1, 8))]
        pref = []
        run = 0
        for x in a:
            run ^= x
            pref.append(run)
        assert f(pref) == a


@test(f"{BM}:xor-decode#Neighbouring bitwise XOR")
def _(ns):
    f = ns["does_valid_array_exist"]
    assert f([1, 1, 0]) is True and f([1, 1]) is True and f([1, 0]) is False
    for n in range(1, 6):
        for derived in _it.product([0, 1], repeat=n):
            exists = any(all(o[i] ^ o[(i + 1) % n] == derived[i] for i in range(n)) for o in _it.product([0, 1], repeat=n))
            assert f(list(derived)) is exists


@test(f"{BM}:xor-decode#Maximum XOR for each query")
def _(ns):
    f = ns["get_maximum_xor"]
    assert f([0, 1, 1, 3], 2) == [0, 3, 2, 3]
    r = random.Random(1004)
    for _ in range(100):
        mb = r.randint(1, 5)
        nums = sorted(r.randint(0, (1 << mb) - 1) for _ in range(r.randint(1, 7)))
        want, cur = [], nums[:]
        while cur:
            tot = 0
            for x in cur:
                tot ^= x
            want.append(max(range(1 << mb), key=lambda k: tot ^ k))
            cur.pop()
        assert f(nums[:], mb) == want


@test(f"{BM}:parity-mask")
def _(ns):
    f = ns["find_the_longest_substring"]
    assert f("eleetminicoworoep") == 13 and f("leetcodeisgreat") == 5 and f("bcbcbc") == 6
    r = random.Random(1005)
    for _ in range(200):
        s = "".join(r.choice("aeiouxy") for _ in range(r.randint(1, 12)))
        best = max(j - i for i in range(len(s) + 1) for j in range(i, len(s) + 1) if all(s[i:j].count(v) % 2 == 0 for v in "aeiou"))
        assert f(s) == best


@test(f"{BM}:parity-mask#Palindrome queries (prefix masks)")
def _(ns):
    f = ns["can_make_pali_queries"]
    assert f("abcda", [[3, 3, 0], [1, 2, 0], [0, 3, 1], [0, 3, 2], [0, 4, 1]]) == [True, False, False, True, True]
    r = random.Random(1006)
    for _ in range(200):
        s = "".join(r.choice("abc") for _ in range(r.randint(1, 9)))
        qs = []
        for _ in range(4):
            a = r.randrange(len(s))
            qs.append([a, r.randint(a, len(s) - 1), r.randint(0, 3)])
        want = []
        for a, b, k in qs:
            seg = s[a:b + 1]
            odd = sum(1 for c in set(seg) if seg.count(c) % 2)
            want.append(odd // 2 <= k)
        assert f(s, [q[:] for q in qs]) == want


@test(f"{BM}:parity-mask#Wonderful substrings")
def _(ns):
    f = ns["wonderful_substrings"]
    assert f("aba") == 4 and f("aabb") == 9 and f("he") == 2
    r = random.Random(1007)
    for _ in range(200):
        s = "".join(r.choice("abcj") for _ in range(r.randint(1, 10)))
        want = sum(1 for i in range(len(s)) for j in range(i + 1, len(s) + 1) if sum(1 for c in set(s[i:j]) if s[i:j].count(c) % 2) <= 1)
        assert f(s) == want


@test(f"{BM}:fields")
def _(ns):
    f = ns["to_hex"]
    assert f(26) == "1a" and f(-1) == "ffffffff" and f(0) == "0"
    for n in list(range(-300, 300)) + [2**31 - 1, -(2**31)]:
        assert f(n) == format(n & 0xFFFFFFFF, "x")


@test(f"{BM}:fields#UTF-8 validation")
def _(ns):
    f = ns["valid_utf8"]
    assert f([197, 130, 1]) is True and f([235, 140, 4]) is False
    r = random.Random(1008)
    for _ in range(300):
        s = "".join(r.choice(["a", "é", "€", "😀", "z"]) for _ in range(r.randint(0, 4)))
        data = list(s.encode("utf-8"))
        assert f(data[:]) is True
        if data:
            bad = data[:]
            bad[r.randrange(len(bad))] = r.randint(0, 255)
            try:
                bytes(bad).decode("utf-8")
                ok = True
            except UnicodeDecodeError:
                ok = False
            # the problem's rules are stricter in no way that matters for our generated bytes, except overlong forms
            if ok:
                assert f(bad[:]) is True or any(b in (192, 193) for b in bad)


@test(f"{BM}:binary-arith")
def _(ns):
    f = ns["add_binary"]
    assert f("11", "1") == "100" and f("1010", "1011") == "10101"
    r = random.Random(1009)
    for _ in range(200):
        a, b = r.randint(0, 500), r.randint(0, 500)
        assert f(bin(a)[2:], bin(b)[2:]) == bin(a + b)[2:]


@test(f"{BM}:binary-arith#Steps to reduce a binary number to one")
def _(ns):
    f = ns["num_steps"]
    assert f("1101") == 6 and f("10") == 1 and f("1") == 0
    for n in range(1, 600):
        steps, x = 0, n
        while x != 1:
            x = x // 2 if x % 2 == 0 else x + 1
            steps += 1
        assert f(bin(n)[2:]) == steps, n


@test(f"{BM}:binary-arith#Concatenate consecutive binary numbers")
def _(ns):
    f = ns["concatenated_binary"]
    assert f(1) == 1 and f(3) == 27 and f(12) == 505379714
    for n in range(1, 40):
        assert f(n) == int("".join(bin(i)[2:] for i in range(1, n + 1)), 2) % (10**9 + 7)


@test(f"{BM}:binary-arith#Divide two integers (shifts)")
def _(ns):
    f = ns["divide"]
    assert f(10, 3) == 3 and f(7, -3) == -2 and f(-2**31, -1) == 2**31 - 1
    r = random.Random(1010)
    for _ in range(300):
        a, b = r.randint(-500, 500), r.choice([x for x in range(-20, 21) if x])
        q = abs(a) // abs(b)
        assert f(a, b) == (-q if (a < 0) != (b < 0) else q)


@test(f"{BM}:bit-window")
def _(ns):
    f = ns["longest_nice_subarray"]
    assert f([1, 3, 8, 48, 10]) == 3 and f([3, 1, 5, 11, 13]) == 1
    r = random.Random(1011)
    for _ in range(200):
        a = [r.randint(1, 31) for _ in range(r.randint(1, 9))]
        best = 0
        for i in range(len(a)):
            for j in range(i + 1, len(a) + 1):
                if all(x & y == 0 for x, y in _it.combinations(a[i:j], 2)):
                    best = max(best, j - i)
        assert f(a[:]) == best


@test(f"{BM}:bit-window#Shortest subarray with OR at least k")
def _(ns):
    f = ns["minimum_subarray_length"]
    assert f([1, 2, 3], 2) == 1 and f([2, 1, 8], 10) == 3 and f([1, 2], 0) == 1
    r = random.Random(1012)
    for _ in range(200):
        a = [r.randint(0, 15) for _ in range(r.randint(1, 8))]
        k = r.randint(0, 20)
        best = -1
        for i in range(len(a)):
            v = 0
            for j in range(i, len(a)):
                v |= a[j]
                if v >= k:
                    best = j - i + 1 if best == -1 else min(best, j - i + 1)
                    break
        assert f(a[:], k) == best, (a, k)


@test(f"{BM}:bit-window#Longest subarray with the maximum AND")
def _(ns):
    f = ns["longest_subarray"]
    assert f([1, 2, 3, 3, 2, 2]) == 2 and f([1, 2, 3, 4]) == 1
    r = random.Random(1013)
    for _ in range(200):
        a = [r.randint(1, 7) for _ in range(r.randint(1, 8))]

        def and_(x):
            v = x[0]
            for y in x[1:]:
                v &= y
            return v

        subs = [(and_(a[i:j]), j - i) for i in range(len(a)) for j in range(i + 1, len(a) + 1)]
        mx = max(v for v, _ in subs)
        assert f(a[:]) == max(l for v, l in subs if v == mx)


@test(f"{BM}:kth-bit")
def _(ns):
    f = ns["find_kth_bit"]
    assert f(3, 1) == "0" and f(4, 11) == "1"
    def build(n):
        s = "0"
        for _ in range(n - 1):
            s = s + "1" + "".join("1" if c == "0" else "0" for c in reversed(s))
        return s
    for n in range(1, 8):
        s = build(n)
        for k in range(1, len(s) + 1):
            assert f(n, k) == s[k - 1], (n, k)


@test(f"{BM}:kth-bit#K-th symbol in grammar")
def _(ns):
    f = ns["kth_grammar"]
    rows = ["0"]
    for _ in range(8):
        rows.append("".join("01" if c == "0" else "10" for c in rows[-1]))
    for n in range(1, 9):
        for k in range(1, 2 ** (n - 1) + 1):
            assert f(n, k) == int(rows[n - 1][k - 1])


@test(f"{BM}:column-count")
def _(ns):
    f = ns["largest_combination"]
    assert f([16, 17, 71, 62, 12, 24, 14]) == 4 and f([8, 8]) == 2
    r = random.Random(1014)
    for _ in range(200):
        a = [r.randint(1, 31) for _ in range(r.randint(1, 8))]
        best = 0
        for mask in range(1, 1 << len(a)):
            v = 31
            cnt = 0
            for i in range(len(a)):
                if mask >> i & 1:
                    v &= a[i]
                    cnt += 1
            if v > 0:
                best = max(best, cnt)
        assert f(a[:]) == best


@test(f"{BM}:column-count#K-or of an array")
def _(ns):
    f = ns["find_k_or"]
    assert f([7, 12, 9, 8, 9, 15], 4) == 9 and f([2, 12, 1, 11, 4, 5], 6) == 0
    r = random.Random(1015)
    for _ in range(200):
        a = [r.randint(0, 31) for _ in range(r.randint(1, 8))]
        k = r.randint(1, len(a))
        want = sum(1 << b for b in range(6) if sum(x >> b & 1 for x in a) >= k)
        assert f(a[:], k) == want


@test(f"{BM}:column-count#Sort by number of one bits")
def _(ns):
    f = ns["sort_by_bits"]
    assert f([0, 1, 2, 3, 4, 5, 6, 7, 8]) == [0, 1, 2, 4, 8, 3, 5, 6, 7]


@test(f"{BM}:column-count#Can the array be sorted (equal popcount swaps)")
def _(ns):
    f = ns["can_sort_array"]
    assert f([8, 4, 2, 30, 15]) is True and f([1, 2, 3, 4, 5]) is True and f([3, 16, 8, 4, 2]) is False
    r = random.Random(1016)
    for _ in range(300):
        a = [r.randint(1, 15) for _ in range(r.randint(1, 7))]
        # bubble sort restricted to swaps of equal popcount neighbours
        b = a[:]
        changed = True
        while changed:
            changed = False
            for i in range(len(b) - 1):
                if b[i] > b[i + 1] and bin(b[i]).count("1") == bin(b[i + 1]).count("1"):
                    b[i], b[i + 1] = b[i + 1], b[i]
                    changed = True
        assert f(a[:]) is (b == sorted(b))


@test(f"{BM}:binary-shape")
def _(ns):
    f = ns["has_alternating_bits"]
    for n in range(1, 500):
        s = bin(n)[2:]
        assert f(n) is all(s[i] != s[i + 1] for i in range(len(s) - 1))


@test(f"{BM}:binary-shape#Binary gap")
def _(ns):
    f = ns["binary_gap"]
    assert f(22) == 2 and f(8) == 0 and f(5) == 2 and f(6) == 1
    for n in range(1, 600):
        ones = [i for i, c in enumerate(reversed(bin(n)[2:])) if c == "1"]
        assert f(n) == max([b - a for a, b in zip(ones, ones[1:])] or [0])


# ---- tries (extras) -------------------------------------------------------------------------------------------------

TR = "Tries"


@test(f"{TR}:xor-trie")
def _(ns):
    f = ns["find_maximum_xor"]
    assert f([3, 10, 5, 25, 2, 8]) == 28
    r = random.Random(1100)
    for _ in range(200):
        a = [r.randint(0, 100) for _ in range(r.randint(1, 8))]
        assert f(a[:]) == max(x ^ y for x in a for y in a)


@test(f"{TR}:xor-trie#Maximum XOR with an element not above a limit")
def _(ns):
    f = ns["maximize_xor"]
    assert f([0, 1, 2, 3, 4], [[3, 1], [1, 3], [5, 6]]) == [3, 3, 7]
    r = random.Random(1101)
    for _ in range(200):
        a = [r.randint(0, 50) for _ in range(r.randint(1, 7))]
        qs = [[r.randint(0, 50), r.randint(0, 60)] for _ in range(5)]
        want = [max([x ^ v for v in a if v <= m] or [-1]) for x, m in qs]
        assert f(a[:], [q[:] for q in qs]) == want


@test(f"{TR}:prefix-counts")
def _(ns):
    f = ns["sum_prefix_scores"]
    assert f(["abc", "ab", "bc", "b"]) == [5, 4, 3, 2] and f(["abcd"]) == [4]
    r = random.Random(1102)
    for _ in range(150):
        w = ["".join(r.choice("ab") for _ in range(r.randint(1, 4))) for _ in range(r.randint(1, 6))]
        want = [sum(sum(1 for u in w if u.startswith(x[:i])) for i in range(1, len(x) + 1)) for x in w]
        assert f(w[:]) == want


@test(f"{TR}:prefix-counts#Map sum pairs")
def _(ns):
    cls = ns["MapSum"]
    r = random.Random(1103)
    for _ in range(100):
        m, ref = cls(), {}
        for _ in range(20):
            if r.random() < 0.5:
                k = "".join(r.choice("ab") for _ in range(r.randint(1, 3)))
                v = r.randint(1, 9)
                m.insert(k, v)
                ref[k] = v
            else:
                p = "".join(r.choice("ab") for _ in range(r.randint(0, 3)))
                assert m.sum(p) == sum(v for k, v in ref.items() if k.startswith(p))


@test(f"{TR}:prefix-counts#Count prefix and suffix pairs")
def _(ns):
    f = ns["count_prefix_suffix_pairs"]
    assert f(["a", "aba", "ababa", "aa"]) == 4 and f(["pa", "papa", "ma", "mama"]) == 2 and f(["abab", "ab"]) == 0
    r = random.Random(1104)
    for _ in range(200):
        w = ["".join(r.choice("ab") for _ in range(r.randint(1, 5))) for _ in range(r.randint(1, 6))]
        want = sum(1 for i in range(len(w)) for j in range(i + 1, len(w)) if w[j].startswith(w[i]) and w[j].endswith(w[i]))
        assert f(w[:]) == want


@test(f"{TR}:shortest-root")
def _(ns):
    f = ns["replace_words"]
    assert f(["cat", "bat", "rat"], "the cattle was rattled by the battery") == "the cat was rat by the bat"
    r = random.Random(1105)
    for _ in range(150):
        d = ["".join(r.choice("ab") for _ in range(r.randint(1, 3))) for _ in range(r.randint(1, 4))]
        sent = " ".join("".join(r.choice("abc") for _ in range(r.randint(1, 5))) for _ in range(r.randint(1, 5)))
        want = []
        for word in sent.split():
            roots = [x for x in d if word.startswith(x)]
            want.append(min(roots, key=len) if roots else word)
        assert f(d[:], sent) == " ".join(want)


@test(f"{TR}:shortest-root#Longest word in the dictionary")
def _(ns):
    f = ns["longest_word"]
    assert f(["w", "wo", "wor", "worl", "world"]) == "world" and f(["a", "banana", "app", "appl", "ap", "apply", "apple"]) == "apple"
    r = random.Random(1106)
    for _ in range(200):
        w = list({"".join(r.choice("ab") for _ in range(r.randint(1, 4))) for _ in range(r.randint(1, 8))})
        ws = set(w)
        ok = [x for x in w if all(x[:i] in ws for i in range(1, len(x) + 1))]
        want = min(ok, key=lambda x: (-len(x), x)) if ok else ""
        assert f(w[:]) == want


@test(f"{TR}:shortest-root#Short encoding of words (reversed trie)")
def _(ns):
    f = ns["minimum_length_encoding"]
    assert f(["time", "me", "bell"]) == 10 and f(["t"]) == 2
    r = random.Random(1107)
    for _ in range(200):
        w = ["".join(r.choice("ab") for _ in range(r.randint(1, 4))) for _ in range(r.randint(1, 6))]
        u = set(w)
        keep = [x for x in u if not any(y != x and y.endswith(x) for y in u)]
        assert f(w[:]) == sum(len(x) + 1 for x in keep)


@test(f"{TR}:folders")
def _(ns):
    f = ns["remove_subfolders"]
    assert sorted(f(["/a", "/a/b", "/c/d", "/c/d/e", "/c/f"])) == ["/a", "/c/d", "/c/f"]
    r = random.Random(1108)
    for _ in range(150):
        paths = list({"/" + "/".join(r.choice("abc") for _ in range(r.randint(1, 3))) for _ in range(r.randint(1, 8))})
        want = [p for p in paths if not any(q != p and p.startswith(q + "/") for q in paths)]
        assert sorted(f(paths[:])) == sorted(want)


@test(f"{TR}:folders#Design file system")
def _(ns):
    cls = ns["FileSystem"]
    fs = cls()
    assert fs.createPath("/a", 1) is True and fs.get("/a") == 1 and fs.createPath("/leet/code", 2) is False
    assert fs.createPath("/leet", 1) is True and fs.createPath("/leet/code", 2) is True and fs.get("/leet/code") == 2 and fs.createPath("/a", 5) is False and fs.get("/x") == -1


@test(f"{TR}:prefix-suffix")
def _(ns):
    cls = ns["WordFilter"]
    wf = cls(["apple"])
    assert wf.f("a", "e") == 0 and wf.f("b", "") == -1
    r = random.Random(1109)
    for _ in range(100):
        words = ["".join(r.choice("ab") for _ in range(r.randint(1, 4))) for _ in range(r.randint(1, 5))]
        wf = cls(words[:])
        for _ in range(8):
            p = "".join(r.choice("ab") for _ in range(r.randint(0, 3)))
            s = "".join(r.choice("ab") for _ in range(r.randint(0, 3)))
            want = max([i for i, w in enumerate(words) if w.startswith(p) and w.endswith(s)] or [-1])
            assert wf.f(p, s) == want


@test(f"{TR}:fuzzy")
def _(ns):
    cls = ns["MagicDictionary"]
    r = random.Random(1110)
    for _ in range(100):
        d = ["".join(r.choice("ab") for _ in range(r.randint(1, 3))) for _ in range(r.randint(1, 5))]
        m = cls()
        m.buildDict(d)
        for _ in range(8):
            q = "".join(r.choice("ab") for _ in range(r.randint(1, 3)))
            want = any(len(w) == len(q) and sum(a != b for a, b in zip(w, q)) == 1 for w in d)
            assert m.search(q) is want


@test(f"{TR}:fuzzy#Words within two edits")
def _(ns):
    f = ns["two_edit_words"]
    assert f(["word", "note", "ants", "wood"], ["wood", "joke", "moat"]) == ["word", "note", "wood"]


@test(f"{TR}:segment-dp")
def _(ns):
    f = ns["min_extra_char"]
    assert f("leetscode", ["leet", "code", "leetcode"]) == 1 and f("sayhelloworld", ["hello", "world"]) == 3
    r = random.Random(1111)
    for _ in range(200):
        s = "".join(r.choice("ab") for _ in range(r.randint(1, 9)))
        d = list({"".join(r.choice("ab") for _ in range(r.randint(1, 3))) for _ in range(r.randint(1, 4))})
        best = [0] * (len(s) + 1)
        for i in range(len(s) - 1, -1, -1):
            best[i] = best[i + 1] + 1
            for w in d:
                if s.startswith(w, i):
                    best[i] = min(best[i], best[i + len(w)])
        assert f(s, d[:]) == best[0]


@test(f"{TR}:segment-dp#Greedy segmentation (partition string)")
def _(ns):
    f = ns["partition_string"]
    assert f("abbccccd") == ["a", "b", "bc", "c", "cc", "d"]
    r = random.Random(1112)
    for _ in range(100):
        s = "".join(r.choice("ab") for _ in range(r.randint(1, 12)))
        parts = f(s)
        assert "".join(parts) in (s, s[:len("".join(parts))]) and len(parts) == len(set(parts))


@test(f"{TR}:palindrome-pairs")
def _(ns):
    f = ns["palindrome_pairs"]
    assert sorted(f(["abcd", "dcba", "lls", "s", "sssll"])) == [[0, 1], [1, 0], [2, 4], [3, 2]] and sorted(f(["a", ""])) == [[0, 1], [1, 0]]
    r = random.Random(1113)
    for _ in range(200):
        words = list({"".join(r.choice("ab") for _ in range(r.randint(0, 4))) for _ in range(r.randint(1, 6))})
        want = sorted([i, j] for i in range(len(words)) for j in range(len(words)) if i != j and (words[i] + words[j]) == (words[i] + words[j])[::-1])
        assert sorted(f(words[:])) == want


@test(f"{TR}:palindrome-pairs#Shortest palindrome")
def _(ns):
    f = ns["shortest_palindrome"]
    assert f("aacecaaa") == "aaacecaaa" and f("abcd") == "dcbabcd" and f("") == ""
    r = random.Random(1114)
    for _ in range(300):
        s = "".join(r.choice("ab") for _ in range(r.randint(0, 8)))
        out = f(s)
        assert out == out[::-1] and out.endswith(s)
        best = min((p + s for k in range(len(s) + 1) for p in [s[::-1][:k]] if (p + s) == (p + s)[::-1]), key=len)
        assert out == best


@test(f"{TR}:autocomplete")
def _(ns):
    cls = ns["AutocompleteSystem"]
    t = cls(["i love you", "island", "iroman", "i love leetcode"], [5, 3, 2, 2])
    assert t.input("i") == ["i love you", "island", "i love leetcode"] and t.input(" ") == ["i love you", "i love leetcode"] and t.input("a") == [] and t.input("#") == []
    r = random.Random(1115)
    for _ in range(60):
        sents = list({"".join(r.choice("ab ") for _ in range(r.randint(1, 4))) for _ in range(r.randint(1, 4))})
        times = [r.randint(1, 5) for _ in sents]
        sys_, count = cls(sents[:], times[:]), dict(zip(sents, times))
        for _ in range(3):
            typed = ""
            for ch in "".join(r.choice("ab ") for _ in range(r.randint(1, 3))) + "#":
                out = sys_.input(ch)
                if ch == "#":
                    count[typed] = count.get(typed, 0) + 1
                    assert out == []
                else:
                    typed += ch
                    cand = sorted((s for s in count if s.startswith(typed)), key=lambda s: (-count[s], s))[:3]
                    assert out == cand, (typed, out, cand)


# ---- math & geometry (extras) ---------------------------------------------------------------------------------------

MG = "Math & Geometry"


@test(f"{MG}:long-division")
def _(ns):
    from fractions import Fraction
    f = ns["fraction_to_decimal"]
    assert f(1, 2) == "0.5" and f(2, 1) == "2" and f(4, 333) == "0.(012)" and f(1, 6) == "0.1(6)" and f(-50, 8) == "-6.25" and f(0, -5) == "0"
    r = random.Random(1200)
    for _ in range(400):
        n, d = r.randint(-200, 200), r.choice([x for x in range(-60, 61) if x])
        out = f(n, d)
        neg = out.startswith("-")
        body = out.lstrip("-")
        whole, _, frac = body.partition(".")
        if "(" in frac:
            pre, cyc = frac.rstrip(")").split("(")
            value = Fraction(int(whole)) + (Fraction(int(pre or "0"), 10 ** len(pre)) if pre else 0) + Fraction(int(cyc), 10 ** len(pre) * (10 ** len(cyc) - 1))
        else:
            value = Fraction(int(whole)) + (Fraction(int(frac), 10 ** len(frac)) if frac else 0)
        assert (-value if neg else value) == Fraction(n, d), (n, d, out)
        assert n == 0 or neg == ((n < 0) != (d < 0))


@test(f"{MG}:count-factors")
def _(ns):
    import math
    f = ns["trailing_zeroes"]
    for n in list(range(0, 300)) + [1500]:
        s = str(math.factorial(n))
        assert f(n) == len(s) - len(s.rstrip("0"))


@test(f"{MG}:count-factors#Number of digit one")
def _(ns):
    f = ns["count_digit_one"]
    assert f(13) == 6 and f(0) == 0
    for n in list(range(0, 400)) + [1234, 99999]:
        assert f(n) == sum(str(i).count("1") for i in range(1, n + 1)), n


@test(f"{MG}:pow-count")
def _(ns):
    f = ns["count_good_numbers"]
    assert f(1) == 5 and f(4) == 400 and f(50) == 564908303
    for n in range(1, 6):
        count = sum(1 for digits in _it.product(range(10), repeat=n) if all((d % 2 == 0) if i % 2 == 0 else d in (2, 3, 5, 7) for i, d in enumerate(digits)))
        assert f(n) == count


@test(f"{MG}:pow-count#Monkeys on a polygon")
def _(ns):
    f = ns["monkey_move"]
    assert f(3) == 6 and f(4) == 14
    for n in range(3, 10):
        assert f(n) == 2**n - 2


@test(f"{MG}:pow-count#Super pow")
def _(ns):
    f = ns["super_pow"]
    assert f(2, [3]) == 8 and f(2, [1, 0]) == 1024 and f(1, [4, 3, 3, 8, 5, 2]) == 1
    r = random.Random(1201)
    for _ in range(200):
        a, b = r.randint(1, 50), [r.randint(0, 9) for _ in range(r.randint(1, 4))]
        assert f(a, b[:]) == pow(a, int("".join(map(str, b))), 1337)


@test(f"{MG}:slopes")
def _(ns):
    f = ns["max_points"]
    assert f([[1, 1], [2, 2], [3, 3]]) == 3 and f([[1, 1], [3, 2], [5, 3], [4, 1], [2, 3], [1, 4]]) == 4 and f([[0, 0]]) == 1
    r = random.Random(1202)
    for _ in range(200):
        pts = list({(r.randint(-3, 3), r.randint(-3, 3)) for _ in range(r.randint(1, 8))})
        best = min(len(pts), 2)
        for a, b in _it.combinations(pts, 2):
            n = sum(1 for c in pts if (b[0] - a[0]) * (c[1] - a[1]) == (b[1] - a[1]) * (c[0] - a[0]))
            best = max(best, n)
        assert f([list(p) for p in pts]) == best


@test(f"{MG}:slopes#Number of boomerangs")
def _(ns):
    f = ns["number_of_boomerangs"]
    assert f([[0, 0], [1, 0], [2, 0]]) == 2 and f([[1, 1]]) == 0
    r = random.Random(1203)
    for _ in range(200):
        pts = list({(r.randint(-3, 3), r.randint(-3, 3)) for _ in range(r.randint(1, 7))})
        d = lambda a, b: (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
        want = sum(1 for i in pts for j in pts for k in pts if i != j and i != k and j != k and d(i, j) == d(i, k))
        assert f([list(p) for p in pts]) == want


@test(f"{MG}:slopes#Minimum area rectangle")
def _(ns):
    f = ns["min_area_rect"]
    assert f([[1, 1], [1, 3], [3, 1], [3, 3], [2, 2]]) == 4 and f([[1, 1], [1, 3], [3, 1], [3, 3], [4, 1], [4, 3]]) == 2 and f([[1, 1], [2, 2]]) == 0
    r = random.Random(1204)
    for _ in range(200):
        pts = list({(r.randint(0, 4), r.randint(0, 4)) for _ in range(r.randint(1, 9))})
        s = set(pts)
        best = min([abs(a[0] - b[0]) * abs(a[1] - b[1]) for a in pts for b in pts if a[0] != b[0] and a[1] != b[1] and (a[0], b[1]) in s and (b[0], a[1]) in s] or [0])
        assert f([list(p) for p in pts]) == best


@test(f"{MG}:divisors")
def _(ns):
    f = ns["bulb_switch"]
    for n in range(0, 200):
        assert f(n) == sum(1 for i in range(1, n + 1) if sum(1 for d in range(1, i + 1) if i % d == 0) % 2)


@test(f"{MG}:divisors#The k-th factor")
def _(ns):
    f = ns["kth_factor"]
    assert f(12, 3) == 3 and f(7, 2) == 7 and f(4, 4) == -1
    for n in range(1, 120):
        divs = [d for d in range(1, n + 1) if n % d == 0]
        for k in range(1, len(divs) + 2):
            assert f(n, k) == (divs[k - 1] if k <= len(divs) else -1)


@test(f"{MG}:divisors#Water and jug")
def _(ns):
    f = ns["can_measure_water"]
    assert f(3, 5, 4) is True and f(2, 6, 5) is False and f(1, 2, 3) is True
    for x in range(1, 9):
        for y in range(1, 9):
            reach, stack = set(), [(0, 0)]
            while stack:
                a, b = stack.pop()
                if (a, b) in reach:
                    continue
                reach.add((a, b))
                stack += [(x, b), (a, y), (0, b), (a, 0), (a - min(a, y - b), b + min(a, y - b)), (a + min(b, x - a), b - min(b, x - a))]
            for t in range(0, x + y + 2):
                assert f(x, y, t) is any(a + b == t for a, b in reach), (x, y, t)


@test(f"{MG}:divisors#Power of three")
def _(ns):
    f = ns["is_power_of_three"]
    for n in range(-5, 3000):
        assert f(n) is (n > 0 and any(3**k == n for k in range(0, 10)))


@test(f"{MG}:diagonals")
def _(ns):
    f = ns["find_diagonal_order"]
    assert f([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == [1, 2, 4, 7, 5, 3, 6, 8, 9]
    r = random.Random(1205)
    for _ in range(100):
        R, C = r.randint(1, 5), r.randint(1, 5)
        m = [[r.randint(0, 99) for _ in range(C)] for _ in range(R)]
        # LeetCode order: up-right first, then down-left, and so on
        want, i, j, up = [], 0, 0, True
        for _ in range(R * C):
            want.append(m[i][j])
            if up:
                if j == C - 1:
                    i, up = i + 1, False
                elif i == 0:
                    j, up = j + 1, False
                else:
                    i, j = i - 1, j + 1
            else:
                if i == R - 1:
                    j, up = j + 1, True
                elif j == 0:
                    i, up = i + 1, True
                else:
                    i, j = i + 1, j - 1
        assert f([row[:] for row in m]) == want


@test(f"{MG}:diagonals#Sort matrix by diagonals")
def _(ns):
    f = ns["sort_matrix"]
    assert f([[1, 7, 3], [9, 8, 2], [4, 5, 6]]) == [[8, 2, 3], [9, 6, 7], [4, 5, 1]]
    r = random.Random(1206)
    for _ in range(100):
        n = r.randint(1, 5)
        g = [[r.randint(0, 20) for _ in range(n)] for _ in range(n)]
        out = f([row[:] for row in g])
        for k in range(-(n - 1), n):
            cells = [out[i][i - k] for i in range(n) if 0 <= i - k < n]
            src = sorted(g[i][i - k] for i in range(n) if 0 <= i - k < n)
            assert sorted(cells) == src
            assert cells == (sorted(cells, reverse=True) if k >= 0 else sorted(cells))


@test(f"{MG}:diagonals#Toeplitz matrix")
def _(ns):
    f = ns["is_toeplitz_matrix"]
    assert f([[1, 2, 3, 4], [5, 1, 2, 3], [9, 5, 1, 2]]) is True and f([[1, 2], [2, 2]]) is False
    r = random.Random(1207)
    for _ in range(100):
        R, C = r.randint(1, 4), r.randint(1, 4)
        top = [r.randint(0, 2) for _ in range(R + C - 1)]
        m = [[top[C - 1 - j + i] for j in range(C)] for i in range(R)]
        assert f(m) is True
        if R > 1 and C > 1:
            m[R - 1][C - 1] += 1
            assert f(m) is False


@test(f"{MG}:encode-state")
def _(ns):
    f = ns["game_of_life"]
    r = random.Random(1208)
    for _ in range(100):
        R, C = r.randint(1, 5), r.randint(1, 5)
        b = [[r.randint(0, 1) for _ in range(C)] for _ in range(R)]
        want = [[0] * C for _ in range(R)]
        for i in range(R):
            for j in range(C):
                live = sum(b[a][c] for a in range(max(0, i - 1), min(R, i + 2)) for c in range(max(0, j - 1), min(C, j + 2)) if (a, c) != (i, j))
                want[i][j] = 1 if live == 3 or (b[i][j] and live == 2) else 0
        got = [row[:] for row in b]
        f(got)
        assert got == want


@test(f"{MG}:encode-state#Rotating the box")
def _(ns):
    f = ns["rotate_the_box"]
    assert f([["#", ".", "#"]]) == [["."], ["#"], ["#"]]
    r = random.Random(1209)
    for _ in range(100):
        R, C = r.randint(1, 4), r.randint(1, 6)
        box = [[r.choice("#.*") for _ in range(C)] for _ in range(R)]
        fallen = []
        for row in box:
            out, stones = [], 0
            seg = []
            for ch in row + ["*"]:
                if ch == "#":
                    stones += 1
                elif ch == ".":
                    seg.append(".")
                else:
                    out += ["."] * (len(seg)) + ["#"] * stones + ([] if ch == "*" and False else [])
                    out.append("*")
                    seg, stones = [], 0
            out = out[:-1]
            fallen.append(out)
        want = [list(col) for col in zip(*fallen[::-1])]
        assert f([row[:] for row in box]) == want, box


@test(f"{MG}:robot")
def _(ns):
    f = ns["is_robot_bounded"]
    assert f("GGLLGG") is True and f("GG") is False and f("GL") is True
    r = random.Random(1210)
    for _ in range(200):
        ins = "".join(r.choice("GLR") for _ in range(r.randint(1, 8)))
        dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        x = y = d = 0
        for _ in range(4):
            for ch in ins:
                if ch == "G":
                    x, y = x + dirs[d][0], y + dirs[d][1]
                else:
                    d = (d + (3 if ch == "L" else 1)) % 4
        assert f(ins) is ((x, y) == (0, 0))


@test(f"{MG}:robot#Walking robot simulation")
def _(ns):
    f = ns["robot_sim"]
    assert f([4, -1, 3], []) == 25 and f([4, -1, 4, -2, 4], [[2, 4]]) == 65
    r = random.Random(1211)
    for _ in range(100):
        cmds = [r.choice([-2, -1, 1, 2, 3, 4]) for _ in range(r.randint(1, 8))]
        obs = [[r.randint(-3, 3), r.randint(-3, 3)] for _ in range(r.randint(0, 4))]
        blocked = {tuple(o) for o in obs}
        x = y = d = best = 0
        dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for c in cmds:
            if c < 0:
                d = (d + (3 if c == -2 else 1)) % 4
            else:
                for _ in range(c):
                    nx, ny = x + dirs[d][0], y + dirs[d][1]
                    if (nx, ny) in blocked:
                        break
                    x, y = nx, ny
                    best = max(best, x * x + y * y)
        assert f(cmds[:], [o[:] for o in obs]) == best


@test(f"{MG}:dates")
def _(ns):
    import datetime
    f = ns["days_between_dates"]
    assert f("2019-06-29", "2019-06-30") == 1 and f("2020-01-15", "2019-12-31") == 15
    r = random.Random(1212)
    for _ in range(200):
        a = datetime.date(1971, 1, 1) + datetime.timedelta(days=r.randint(0, 40000))
        b = datetime.date(1971, 1, 1) + datetime.timedelta(days=r.randint(0, 40000))
        assert f(a.isoformat(), b.isoformat()) == abs((a - b).days)


@test(f"{MG}:dates#Angle between clock hands")
def _(ns):
    f = ns["angle_clock"]
    assert f(12, 30) == 165 and f(3, 30) == 75 and f(3, 15) == 7.5
    for h in range(1, 13):
        for m in range(60):
            hh = (h % 12) * 30 + m * 0.5
            mm = m * 6
            diff = abs(hh - mm)
            assert abs(f(h, m) - min(diff, 360 - diff)) < 1e-9 and 0 <= f(h, m) <= 180


@test(f"{MG}:dates#Minimum time visiting all points")
def _(ns):
    f = ns["min_time_to_visit_all_points"]
    assert f([[1, 1], [3, 4], [-1, 0]]) == 7 and f([[3, 2], [-2, 2]]) == 5
    r = random.Random(1213)
    for _ in range(100):
        pts = [[r.randint(-5, 5), r.randint(-5, 5)] for _ in range(r.randint(2, 5))]
        total = 0
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            x, y, t = x1, y1, 0
            while (x, y) != (x2, y2):
                x += (x2 > x) - (x2 < x)
                y += (y2 > y) - (y2 < y)
                t += 1
            total += t
        assert f([p[:] for p in pts]) == total


@test(f"{MG}:square-sums")
def _(ns):
    f = ns["judge_square_sum"]
    assert f(5) is True and f(3) is False and f(0) is True and f(2) is True
    for c in range(0, 300):
        assert f(c) is any(a * a + b * b == c for a in range(0, 18) for b in range(0, 18))


@test(f"{MG}:square-sums#Sum of distinct powers of three")
def _(ns):
    f = ns["check_powers_of_three"]
    assert f(12) is True and f(91) is True and f(21) is False
    for n in range(1, 600):
        assert f(n) is any(sum(3**i for i in range(8) if mask >> i & 1) == n for mask in range(256))


@test(f"{MG}:josephus")
def _(ns):
    from collections import deque
    f = ns["find_the_winner"]
    assert f(5, 2) == 3 and f(6, 5) == 1
    for n in range(1, 30):
        for k in range(1, 8):
            q = deque(range(1, n + 1))
            while len(q) > 1:
                q.rotate(-(k - 1))
                q.popleft()
            assert f(n, k) == q[0]


@test(f"{MG}:josephus#Elimination game")
def _(ns):
    f = ns["last_remaining"]
    assert f(9) == 6 and f(1) == 1
    for n in range(1, 120):
        a, left = list(range(1, n + 1)), True
        while len(a) > 1:
            a = a[1::2] if left else a[::-1][1::2][::-1]
            left = not left
        assert f(n) == a[0], n


@test(f"{MG}:int-to-text")
def _(ns):
    f = ns["int_to_roman"]
    vals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}

    def back(s):
        total = 0
        for i, c in enumerate(s):
            v = vals[c]
            total += -v if i + 1 < len(s) and vals[s[i + 1]] > v else v
        return total

    assert f(3749) == "MMMDCCXLIX" and f(58) == "LVIII" and f(1994) == "MCMXCIV"
    for n in range(1, 4000):
        assert back(f(n)) == n


@test(f"{MG}:int-to-text#Integer to English words")
def _(ns):
    f = ns["number_to_words"]
    assert f(0) == "Zero" and f(123) == "One Hundred Twenty Three" and f(12345) == "Twelve Thousand Three Hundred Forty Five"
    assert f(1234567) == "One Million Two Hundred Thirty Four Thousand Five Hundred Sixty Seven" and f(1000000) == "One Million" and f(2**31 - 1).startswith("Two Billion One Hundred Forty Seven")
    names = {w: i + 1 for i, w in enumerate("One Two Three Four Five Six Seven Eight Nine Ten Eleven Twelve Thirteen Fourteen Fifteen Sixteen Seventeen Eighteen Nineteen".split())}
    names.update({w: 10 * (i + 2) for i, w in enumerate("Twenty Thirty Forty Fifty Sixty Seventy Eighty Ninety".split())})
    scale = {"Thousand": 10**3, "Million": 10**6, "Billion": 10**9}

    def parse(s):
        total = cur = 0
        for w in s.split():
            if w in names:
                cur += names[w]
            elif w == "Hundred":
                cur *= 100
            else:
                total += cur * scale[w]
                cur = 0
        return total + cur

    r = random.Random(1214)
    for _ in range(300):
        n = r.choice([r.randint(1, 999), r.randint(1, 99999), r.randint(1, 10**9), r.randint(1, 2**31 - 1)])
        assert parse(f(n)) == n, n


@test(f"{MG}:shuffle")
def _(ns):
    import random as _random
    cls = ns["Solution"]
    _random.seed(7)
    s = cls([1, 2, 3])
    counts = {}
    for _ in range(6000):
        out = tuple(s.shuffle())
        counts[out] = counts.get(out, 0) + 1
        assert sorted(out) == [1, 2, 3]
        s.reset()
    assert len(counts) == 6 and all(abs(c - 1000) < 150 for c in counts.values()), counts
    assert s.reset() == [1, 2, 3]


# ---- arrays & hashing (extras) --------------------------------------------------------------------------------------

AH = "Arrays & Hashing"


def _perm_with_dups(r, n):
    return [r.randint(1, n) for _ in range(n)]


@test(f"{AH}:index-hash")
def _(ns):
    f = ns["find_disappeared_numbers"]
    assert f([4, 3, 2, 7, 8, 2, 3, 1]) == [5, 6] and f([1, 1]) == [2]
    r = random.Random(1300)
    for _ in range(200):
        n = r.randint(1, 8)
        a = _perm_with_dups(r, n)
        assert f(a[:]) == [v for v in range(1, n + 1) if v not in a]


@test(f"{AH}:index-hash#Find all duplicates")
def _(ns):
    f = ns["find_duplicates"]
    assert sorted(f([4, 3, 2, 7, 8, 2, 3, 1])) == [2, 3]
    r = random.Random(1301)
    for _ in range(200):
        n = r.randint(1, 8)
        a = [r.randint(1, n) for _ in range(n)]
        want = [v for v in set(a) if a.count(v) == 2]
        a = [v for v in a]
        if any(a.count(v) > 2 for v in a):
            continue
        assert sorted(f(a[:])) == sorted(want)


@test(f"{AH}:index-hash#Set mismatch (cyclic sort)")
def _(ns):
    f = ns["find_error_nums"]
    assert f([1, 2, 2, 4]) == [2, 3] and f([1, 1]) == [1, 2]
    r = random.Random(1302)
    for _ in range(200):
        n = r.randint(2, 8)
        a = list(range(1, n + 1))
        dup, miss = r.sample(a, 2)
        a[a.index(miss)] = dup
        r.shuffle(a)
        assert f(a[:]) == [dup, miss]


@test(f"{AH}:pattern-key")
def _(ns):
    f = ns["is_isomorphic"]
    assert f("egg", "add") is True and f("foo", "bar") is False and f("paper", "title") is True and f("badc", "baba") is False
    r = random.Random(1303)
    for _ in range(300):
        s = "".join(r.choice("abc") for _ in range(r.randint(1, 6)))
        t = "".join(r.choice("xyz") for _ in range(len(s)))
        ok = all(((a == b) == (x == y)) for (a, x) in zip(s, t) for (b, y) in zip(s, t))
        assert f(s, t) is ok


@test(f"{AH}:pattern-key#Word pattern")
def _(ns):
    f = ns["word_pattern"]
    assert f("abba", "dog cat cat dog") is True and f("abba", "dog cat cat fish") is False and f("aaaa", "dog cat cat dog") is False
    r = random.Random(1304)
    for _ in range(200):
        p = "".join(r.choice("ab") for _ in range(r.randint(1, 4)))
        words = [r.choice(["x", "y"]) for _ in range(r.randint(1, 4))]
        ok = len(p) == len(words) and all((p[i] == p[j]) == (words[i] == words[j]) for i in range(len(p)) for j in range(len(p)))
        assert f(p, " ".join(words)) is ok


@test(f"{AH}:pattern-key#Find and replace pattern")
def _(ns):
    f = ns["find_and_replace_pattern"]
    assert f(["abc", "deq", "mee", "aqq", "dkd", "ccc"], "abb") == ["mee", "aqq"]


@test(f"{AH}:random-set")
def _(ns):
    import random as _random
    cls = ns["RandomizedSet"]
    r = random.Random(1305)
    for _ in range(100):
        s, ref = cls(), set()
        for _ in range(40):
            v = r.randint(0, 6)
            if r.random() < 0.5:
                assert s.insert(v) is (v not in ref)
                ref.add(v)
            else:
                assert s.remove(v) is (v in ref)
                ref.discard(v)
            if ref:
                assert s.getRandom() in ref
    _random.seed(3)
    s = cls()
    for v in range(3):
        s.insert(v)
    counts = [0] * 3
    for _ in range(3000):
        counts[s.getRandom()] += 1
    assert all(abs(c - 1000) < 150 for c in counts)


@test(f"{AH}:random-set#Duplicates allowed")
def _(ns):
    cls = ns["RandomizedCollection"]
    r = random.Random(1306)
    for _ in range(100):
        s, ref = cls(), []
        for _ in range(40):
            v = r.randint(0, 3)
            if r.random() < 0.5:
                assert s.insert(v) is (v not in ref)
                ref.append(v)
            else:
                assert s.remove(v) is (v in ref)
                if v in ref:
                    ref.remove(v)
            if ref:
                assert s.getRandom() in ref


@test(f"{AH}:stream-window")
def _(ns):
    cls = ns["RecentCounter"]
    r = random.Random(1307)
    for _ in range(100):
        c, t, seen = cls(), 0, []
        for _ in range(30):
            t += r.randint(1, 1500)
            seen.append(t)
            assert c.ping(t) == sum(1 for x in seen if x >= t - 3000)


@test(f"{AH}:stream-window#Moving average")
def _(ns):
    cls = ns["MovingAverage"]
    r = random.Random(1308)
    for _ in range(100):
        size = r.randint(1, 4)
        m, vals = cls(size), []
        for _ in range(15):
            v = r.randint(-5, 9)
            vals.append(v)
            w = vals[-size:]
            assert abs(m.next(v) - sum(w) / len(w)) < 1e-9


@test(f"{AH}:stream-window#Logger rate limiter")
def _(ns):
    cls = ns["Logger"]
    r = random.Random(1309)
    for _ in range(100):
        lg, last, t = cls(), {}, 0
        for _ in range(30):
            t += r.randint(0, 6)
            msg = r.choice("abc")
            ok = msg not in last or t - last[msg] >= 10
            assert lg.shouldPrintMessage(t, msg) is ok
            if ok:
                last[msg] = t


@test(f"{AH}:stream-window#Underground system")
def _(ns):
    cls = ns["UndergroundSystem"]
    u = cls()
    u.checkIn(45, "Leyton", 3)
    u.checkIn(32, "Paradise", 8)
    u.checkIn(27, "Leyton", 10)
    u.checkOut(45, "Waterloo", 15)
    u.checkOut(27, "Waterloo", 20)
    u.checkOut(32, "Cambridge", 22)
    assert u.getAverageTime("Paradise", "Cambridge") == 14.0 and u.getAverageTime("Leyton", "Waterloo") == 11.0


@test(f"{AH}:sparse")
def _(ns):
    cls = ns["SparseVector"]
    r = random.Random(1310)
    for _ in range(100):
        n = r.randint(1, 10)
        a = [r.choice([0, 0, 0, r.randint(-5, 5)]) for _ in range(n)]
        b = [r.choice([0, 0, r.randint(-5, 5)]) for _ in range(n)]
        assert cls(a).dotProduct(cls(b)) == sum(x * y for x, y in zip(a, b))


@test(f"{AH}:sparse#Sparse matrix multiplication")
def _(ns):
    f = ns["multiply"]
    r = random.Random(1311)
    for _ in range(100):
        m, k, n = r.randint(1, 4), r.randint(1, 4), r.randint(1, 4)
        a = [[r.choice([0, 0, r.randint(-3, 3)]) for _ in range(k)] for _ in range(m)]
        b = [[r.choice([0, 0, r.randint(-3, 3)]) for _ in range(n)] for _ in range(k)]
        want = [[sum(a[i][t] * b[t][j] for t in range(k)) for j in range(n)] for i in range(m)]
        assert f([row[:] for row in a], [row[:] for row in b]) == want


@test(f"{AH}:game-counters")
def _(ns):
    cls = ns["TicTacToe"]
    r = random.Random(1312)
    for _ in range(100):
        n = r.randint(2, 4)
        g, board, winner = cls(n), [[0] * n for _ in range(n)], 0
        cells = [(i, j) for i in range(n) for j in range(n)]
        r.shuffle(cells)
        player = 1
        for i, j in cells:
            if winner:
                break
            board[i][j] = player
            lines = [row for row in board] + [list(c) for c in zip(*board)] + [[board[k][k] for k in range(n)], [board[k][n - 1 - k] for k in range(n)]]
            won = player if any(all(v == player for v in line) for line in lines) else 0
            assert g.move(i, j, player) == won
            winner = won
            player = 3 - player


@test(f"{AH}:game-counters#Leaderboard")
def _(ns):
    cls = ns["Leaderboard"]
    lb = cls()
    for pid, sc in [(1, 73), (2, 56), (3, 39), (4, 51), (5, 4)]:
        lb.addScore(pid, sc)
    assert lb.top(1) == 73
    lb.reset(1)
    lb.reset(2)
    lb.addScore(2, 51)
    assert lb.top(3) == 141


@test(f"{AH}:split-sums")
def _(ns):
    f = ns["pivot_index"]
    assert f([1, 7, 3, 6, 5, 6]) == 3 and f([1, 2, 3]) == -1 and f([2, 1, -1]) == 0
    r = random.Random(1313)
    for _ in range(300):
        a = [r.randint(-3, 5) for _ in range(r.randint(1, 8))]
        want = next((i for i in range(len(a)) if sum(a[:i]) == sum(a[i + 1:])), -1)
        assert f(a[:]) == want


@test(f"{AH}:split-sums#Number of ways to split array")
def _(ns):
    f = ns["ways_to_split_array"]
    assert f([10, 4, -8, 7]) == 2 and f([2, 3, 1, 0]) == 2
    r = random.Random(1314)
    for _ in range(200):
        a = [r.randint(-5, 9) for _ in range(r.randint(2, 8))]
        assert f(a[:]) == sum(1 for i in range(1, len(a)) if sum(a[:i]) >= sum(a[i:]))


@test(f"{AH}:split-sums#Sum of absolute differences (sorted)")
def _(ns):
    f = ns["get_sum_absolute_differences"]
    assert f([2, 3, 5]) == [4, 3, 5]
    r = random.Random(1315)
    for _ in range(200):
        a = sorted(r.randint(1, 20) for _ in range(r.randint(1, 8)))
        assert f(a[:]) == [sum(abs(x - y) for y in a) for x in a]


@test(f"{AH}:split-sums#Grid game")
def _(ns):
    f = ns["grid_game"]
    assert f([[2, 5, 4], [1, 5, 1]]) == 4 and f([[3, 3, 1], [8, 5, 2]]) == 4 and f([[1, 3, 1, 15], [1, 3, 3, 1]]) == 7
    r = random.Random(1316)
    for _ in range(200):
        n = r.randint(1, 5)
        g = [[r.randint(1, 9) for _ in range(n)] for _ in range(2)]
        best = float("inf")
        for a in range(n):
            h = [row[:] for row in g]
            for j in range(a + 1):
                h[0][j] = 0
            for j in range(a, n):
                h[1][j] = 0
            second = max(sum(h[0][:b + 1]) + sum(h[1][b:]) for b in range(n))  # down at column b
            best = min(best, second)
        # the first robot's path zeroes top[0..a] and bottom[a..n-1]
        assert f([row[:] for row in g]) == best


@test(f"{AH}:fenwick")
def _(ns):
    cls = ns["NumArray"]
    r = random.Random(1317)
    for _ in range(100):
        a = [r.randint(-5, 9) for _ in range(r.randint(1, 9))]
        t, ref = cls(a[:]), a[:]
        for _ in range(25):
            if r.random() < 0.5:
                i, v = r.randrange(len(a)), r.randint(-5, 9)
                t.update(i, v)
                ref[i] = v
            else:
                lo = r.randrange(len(a))
                hi = r.randint(lo, len(a) - 1)
                assert t.sumRange(lo, hi) == sum(ref[lo:hi + 1])


@test(f"{AH}:fenwick#2-D Fenwick tree")
def _(ns):
    cls = ns["NumMatrix"]
    r = random.Random(1318)
    for _ in range(60):
        R, C = r.randint(1, 4), r.randint(1, 4)
        m = [[r.randint(-3, 5) for _ in range(C)] for _ in range(R)]
        t, ref = cls([row[:] for row in m]), [row[:] for row in m]
        for _ in range(15):
            if r.random() < 0.5:
                i, j, v = r.randrange(R), r.randrange(C), r.randint(-3, 5)
                t.update(i, j, v)
                ref[i][j] = v
            else:
                r1 = r.randrange(R)
                r2 = r.randint(r1, R - 1)
                c1 = r.randrange(C)
                c2 = r.randint(c1, C - 1)
                assert t.sumRegion(r1, c1, r2, c2) == sum(ref[i][j] for i in range(r1, r2 + 1) for j in range(c1, c2 + 1))


@test(f"{AH}:set-ops")
def _(ns):
    f = ns["intersect"]
    r = random.Random(1319)
    for _ in range(200):
        a = [r.randint(0, 4) for _ in range(r.randint(0, 7))]
        b = [r.randint(0, 4) for _ in range(r.randint(0, 7))]
        from collections import Counter
        want = sorted((Counter(a) & Counter(b)).elements())
        assert sorted(f(a[:], b[:])) == want


@test(f"{AH}:set-ops#Difference of two arrays")
def _(ns):
    f = ns["find_difference"]
    got = f([1, 2, 3], [2, 4, 6])
    assert sorted(got[0]) == [1, 3] and sorted(got[1]) == [4, 6]


@test(f"{AH}:set-ops#Intersection of multiple arrays")
def _(ns):
    f = ns["intersection"]
    assert f([[3, 1, 2, 4, 5], [1, 2, 3, 4], [3, 4, 5, 6]]) == [3, 4]
    r = random.Random(1320)
    for _ in range(100):
        arrs = [[r.randint(0, 5) for _ in range(r.randint(1, 5))] for _ in range(r.randint(1, 4))]
        want = sorted(set.intersection(*map(set, arrs)))
        assert f([a[:] for a in arrs]) == want


@test(f"{AH}:custom-sort")
def _(ns):
    f = ns["relative_sort_array"]
    assert f([2, 3, 1, 3, 2, 4, 6, 7, 9, 2, 19], [2, 1, 4, 3, 9, 6]) == [2, 2, 2, 1, 4, 3, 3, 9, 6, 7, 19]


@test(f"{AH}:custom-sort#Sort by increasing frequency")
def _(ns):
    f = ns["frequency_sort"]
    assert f([1, 1, 2, 2, 2, 3]) == [3, 1, 1, 2, 2, 2] and f([2, 3, 1, 3, 2]) == [1, 3, 3, 2, 2]


@test(f"{AH}:custom-sort#Rank teams by votes")
def _(ns):
    f = ns["rank_teams"]
    assert f(["ABC", "ACB", "ABC", "ACB", "ACB"]) == "ACB" and f(["WXYZ", "XYZW"]) == "XWYZ" and f(["BCA", "CAB", "CBA", "ABC", "ACB", "BAC"]) == "ABC"


@test(f"{AH}:justify")
def _(ns):
    f = ns["full_justify"]
    assert f(["This", "is", "an", "example", "of", "text", "justification."], 16) == ["This    is    an", "example  of text", "justification.  "]
    assert f(["What", "must", "be", "acknowledgment", "shall", "be"], 16) == ["What   must   be", "acknowledgment  ", "shall be        "]
    r = random.Random(1321)
    for _ in range(100):
        words = ["".join("x" for _ in range(r.randint(1, 6))) for _ in range(r.randint(1, 9))]
        w = r.randint(6, 12)
        out = f(words[:], w)
        assert all(len(line) == w for line in out)
        assert " ".join(" ".join(line.split()) for line in out).split() == words


@test(f"{AH}:transformed-key")
def _(ns):
    f = ns["count_bad_pairs"]
    assert f([4, 1, 3, 3]) == 5 and f([1, 2, 3, 4, 5]) == 0
    r = random.Random(1322)
    for _ in range(200):
        a = [r.randint(0, 6) for _ in range(r.randint(1, 9))]
        assert f(a[:]) == sum(1 for i in range(len(a)) for j in range(i + 1, len(a)) if j - i != a[j] - a[i])


@test(f"{AH}:transformed-key#Count nice pairs (reverse digits)")
def _(ns):
    f = ns["count_nice_pairs"]
    assert f([42, 11, 1, 97]) == 2 and f([13, 10, 35, 24, 76]) == 4
    r = random.Random(1323)
    for _ in range(200):
        a = [r.randint(0, 200) for _ in range(r.randint(1, 8))]
        rev = lambda x: int(str(x)[::-1])
        want = sum(1 for i in range(len(a)) for j in range(i + 1, len(a)) if a[i] + rev(a[j]) == a[j] + rev(a[i]))
        assert f(a[:]) == want


@test(f"{AH}:transformed-key#Interchangeable rectangles")
def _(ns):
    f = ns["interchangeable_rectangles"]
    assert f([[4, 8], [3, 6], [10, 20], [15, 30]]) == 6 and f([[4, 5], [7, 8]]) == 0
    r = random.Random(1324)
    for _ in range(200):
        rects = [[r.randint(1, 6), r.randint(1, 6)] for _ in range(r.randint(1, 8))]
        want = sum(1 for i in range(len(rects)) for j in range(i + 1, len(rects)) if rects[i][0] * rects[j][1] == rects[i][1] * rects[j][0])
        assert f([x[:] for x in rects]) == want


@test(f"{AH}:transformed-key#4Sum II")
def _(ns):
    f = ns["four_sum_count"]
    assert f([1, 2], [-2, -1], [-1, 2], [0, 2]) == 2
    r = random.Random(1325)
    for _ in range(100):
        arrs = [[r.randint(-2, 2) for _ in range(r.randint(1, 4))] for _ in range(4)]
        want = sum(1 for a in arrs[0] for b in arrs[1] for c in arrs[2] for d in arrs[3] if a + b + c + d == 0)
        assert f(*[x[:] for x in arrs]) == want


@test(f"{AH}:pascal")
def _(ns):
    from math import comb
    f = ns["generate"]
    for n in range(1, 12):
        assert f(n) == [[comb(i, j) for j in range(i + 1)] for i in range(n)]


@test(f"{AH}:pascal#Pascal's triangle II (one row)")
def _(ns):
    from math import comb
    f = ns["get_row"]
    for n in range(0, 14):
        assert f(n) == [comb(n, j) for j in range(n + 1)]


@test(f"{AH}:pascal#Champagne tower")
def _(ns):
    f = ns["champagne_tower"]
    assert f(1, 1, 1) == 0.0 and f(2, 1, 1) == 0.5 and f(100000009, 33, 17) == 1.0
    r = random.Random(1326)
    for _ in range(100):
        poured, row = r.randint(0, 30), r.randint(0, 6)
        glasses = {(0, 0): float(poured)}
        for rr in range(row):
            for c in range(rr + 1):
                spill = max(0.0, glasses.get((rr, c), 0) - 1) / 2
                glasses[(rr + 1, c)] = glasses.get((rr + 1, c), 0) + spill
                glasses[(rr + 1, c + 1)] = glasses.get((rr + 1, c + 1), 0) + spill
        col = r.randint(0, row)
        assert abs(f(poured, row, col) - min(1.0, glasses.get((row, col), 0))) < 1e-9


@test(f"{AH}:letter-counts")
def _(ns):
    f = ns["word_subsets"]
    assert f(["amazon", "apple", "facebook", "google", "leetcode"], ["e", "o"]) == ["facebook", "google", "leetcode"]
    r = random.Random(1327)
    for _ in range(150):
        w1 = ["".join(r.choice("abc") for _ in range(r.randint(1, 5))) for _ in range(r.randint(1, 5))]
        w2 = ["".join(r.choice("abc") for _ in range(r.randint(1, 3))) for _ in range(r.randint(1, 3))]
        want = [a for a in w1 if all(all(a.count(c) >= b.count(c) for c in "abc") for b in w2)]
        assert f(w1[:], w2[:]) == want


@test(f"{AH}:letter-counts#Find common characters")
def _(ns):
    f = ns["common_chars"]
    assert sorted(f(["bella", "label", "roller"])) == ["e", "l", "l"]
    r = random.Random(1328)
    for _ in range(150):
        words = ["".join(r.choice("abc") for _ in range(r.randint(1, 5))) for _ in range(r.randint(1, 4))]
        want = sorted(c for c in "abc" for _ in range(min(w.count(c) for w in words)))
        assert sorted(f(words[:])) == want


@test(f"{AH}:letter-counts#Close strings")
def _(ns):
    f = ns["close_strings"]
    assert f("abc", "bca") is True and f("a", "aa") is False and f("cabbba", "abbccc") is True and f("cabbba", "aabbss") is False


@test(f"{AH}:run-counts")
def _(ns):
    f = ns["zero_filled_subarray"]
    assert f([1, 3, 0, 0, 2, 0, 0, 4]) == 6 and f([0, 0, 0, 2, 0, 0]) == 9
    r = random.Random(1329)
    for _ in range(200):
        a = [r.choice([0, 0, 1]) for _ in range(r.randint(1, 10))]
        assert f(a[:]) == sum(1 for i in range(len(a)) for j in range(i + 1, len(a) + 1) if all(x == 0 for x in a[i:j]))


@test(f"{AH}:run-counts#Maximum ascending subarray sum")
def _(ns):
    f = ns["max_ascending_sum"]
    assert f([10, 20, 30, 5, 10, 50]) == 65 and f([12, 17, 15, 13, 10, 11, 12]) == 33
    r = random.Random(1330)
    for _ in range(200):
        a = [r.randint(1, 9) for _ in range(r.randint(1, 9))]
        want = max(sum(a[i:j]) for i in range(len(a)) for j in range(i + 1, len(a) + 1) if all(a[k] < a[k + 1] for k in range(i, j - 1)))
        assert f(a[:]) == want


@test(f"{AH}:run-counts#Longest monotone subarray")
def _(ns):
    f = ns["longest_monotonic_subarray"]
    assert f([1, 4, 3, 3, 2]) == 2 and f([3, 3, 3]) == 1 and f([3, 2, 1]) == 3
    r = random.Random(1331)
    for _ in range(200):
        a = [r.randint(1, 5) for _ in range(r.randint(1, 9))]
        want = max(j - i for i in range(len(a)) for j in range(i + 1, len(a) + 1)
                   if all(a[k] < a[k + 1] for k in range(i, j - 1)) or all(a[k] > a[k + 1] for k in range(i, j - 1)))
        assert f(a[:]) == want


@test(f"{AH}:run-length")
def _(ns):
    f = ns["count_and_say"]
    assert [f(n) for n in range(1, 7)] == ["1", "11", "21", "1211", "111221", "312211"]


@test(f"{AH}:run-length#Count binary substrings")
def _(ns):
    f = ns["count_binary_substrings"]
    assert f("00110011") == 6 and f("10101") == 4
    r = random.Random(1332)
    for _ in range(200):
        s = "".join(r.choice("01") for _ in range(r.randint(1, 10)))
        want = 0
        for i in range(len(s)):
            for j in range(i + 2, len(s) + 1, 2):
                t = s[i:j]
                h = len(t) // 2
                if t[:h] == t[0] * h and t[h:] == ("1" if t[0] == "0" else "0") * h:
                    want += 1
        assert f(s) == want


@test(f"{AH}:prefix-function")
def _(ns):
    f = ns["longest_prefix"]
    assert f("level") == "l" and f("ababab") == "abab" and f("abc") == ""
    r = random.Random(1333)
    for _ in range(300):
        s = "".join(r.choice("ab") for _ in range(r.randint(1, 10)))
        want = max([s[:k] for k in range(len(s)) if s[:k] == s[len(s) - k:] and k > 0] or [""], key=len)
        assert f(s) == want


@test(f"{AH}:prefix-function#Repeated substring pattern")
def _(ns):
    f = ns["repeated_substring_pattern"]
    assert f("abab") is True and f("aba") is False and f("abcabcabcabc") is True
    r = random.Random(1334)
    for _ in range(300):
        s = "".join(r.choice("ab") for _ in range(r.randint(1, 10)))
        want = any(len(s) % k == 0 and s == s[:k] * (len(s) // k) for k in range(1, len(s)))
        assert f(s) is want
