"""Behaviour tests for the templates in content/dsa/lessons. TESTS maps a technique id to a function(ns) that exercises
the names the template defines (ns is the namespace the template was run in). Not every template has one: the ones with a
clear contract do, and check_lessons.py reports the count."""
import random
from collections import deque

TESTS = {}


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
