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
