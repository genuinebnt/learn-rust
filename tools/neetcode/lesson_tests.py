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
