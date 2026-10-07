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
