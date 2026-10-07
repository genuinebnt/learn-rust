from anneal_prelude import check, ensure
from solution import build_order

def valid(n, needs, order):
    """Whether `order` lists every package once, each after what it needs."""
    if sorted(order) != list(range(n)):
        return False
    position = {p: i for i, p in enumerate(order)}
    return all(position[need] < position[package] for package, need in needs)


def has_loop(n, needs):
    reach = [[False] * n for _ in range(n)]
    for package, need in needs:
        reach[need][package] = True
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if reach[i][k] and reach[k][j]:
                    reach[i][j] = True
    return any(reach[i][i] for i in range(n))


def expect_order(n, needs):
    got = build_order(n, [tuple(x) for x in needs])
    ensure(got is not None, f"build_order({n}, {needs}) should find an order, got None")
    ensure(valid(n, needs, got), f"build_order({n}, {needs}) returned {got}, which breaks a dependency or misses a package")


def test_a_chain():
    check("build_order(3, [(1, 0), (2, 1)])", build_order(3, [(1, 0), (2, 1)]), [0, 1, 2])


def test_a_loop_has_no_order():
    check("build_order(2, [(0, 1), (1, 0)])", build_order(2, [(0, 1), (1, 0)]), None)


def test_no_dependencies():
    expect_order(4, [])


def test_a_diamond():
    expect_order(4, [(1, 0), (2, 0), (3, 1), (3, 2)])


def test_no_packages():
    check("build_order(0, [])", build_order(0, []), [])
