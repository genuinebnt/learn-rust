import random

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


def test_a_loop_hidden_behind_a_good_start():
    check("build_order(4, [(1, 0), (2, 1), (3, 2), (1, 3)])", build_order(4, [(1, 0), (2, 1), (3, 2), (1, 3)]), None)


def test_a_package_that_needs_itself():
    check("build_order(1, [(0, 0)])", build_order(1, [(0, 0)]), None)


def test_a_loop_in_a_separate_group():
    check("build_order(5, [(1, 0), (3, 2), (2, 3)])", build_order(5, [(1, 0), (3, 2), (2, 3)]), None)


def test_several_packages_need_the_same_one():
    expect_order(5, [(1, 0), (2, 0), (3, 0), (4, 0)])


def test_one_package_needs_several():
    expect_order(5, [(4, 0), (4, 1), (4, 2), (4, 3)])


def test_repeated_pairs():
    expect_order(3, [(1, 0), (1, 0), (2, 1)])


def test_a_long_chain_is_fast_and_not_recursive():
    n = 20000
    expect_order(n, [(i + 1, i) for i in range(n - 1)])


def test_random_graphs_against_a_loop_check():
    rng = random.Random(13)
    for _ in range(300):
        n = rng.randint(1, 6)
        needs = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randint(0, 8))]
        got = build_order(n, [tuple(x) for x in needs])
        if has_loop(n, needs):
            check(f"build_order({n}, {needs}) has a loop", got, None)
        else:
            ensure(got is not None and valid(n, needs, got), f"build_order({n}, {needs}) returned {got}")
