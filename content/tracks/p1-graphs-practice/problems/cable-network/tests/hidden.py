import random

from anneal_prelude import check, ensure
from solution import networks_after_each_cable


def test_a_star():
    check('networks_after_each_cable(5, [(0, 1), (0, 2), (0, 3), (0, 4)])', networks_after_each_cable(5, [(0, 1), (0, 2), (0, 3), (0, 4)]), [4, 3, 2, 1])


def test_two_groups_then_merged():
    check('networks_after_each_cable(6, [(0, 1), (1, 2), (3, 4), (4, 5), (2, 3)])', networks_after_each_cable(6, [(0, 1), (1, 2), (3, 4), (4, 5), (2, 3)]), [5, 4, 3, 2, 1])


def test_loops_do_not_change_the_count():
    check('networks_after_each_cable(3, [(0, 1), (1, 2), (2, 0)])', networks_after_each_cable(3, [(0, 1), (1, 2), (2, 0)]), [2, 1, 1])


def test_single_computer():
    check('networks_after_each_cable(1, [(0, 0), (0, 0)])', networks_after_each_cable(1, [(0, 0), (0, 0)]), [1, 1])


def test_isolated_computers_stay_separate():
    check('networks_after_each_cable(4, [(0, 1)])', networks_after_each_cable(4, [(0, 1)]), [3])


def test_merging_two_groups():
    check('networks_after_each_cable(4, [(0, 1), (2, 3), (1, 3)])', networks_after_each_cable(4, [(0, 1), (2, 3), (1, 3)]), [3, 2, 1])


def reference(n, cables):
    comp = list(range(n))
    out = []
    for a, b in cables:
        ca, cb = comp[a], comp[b]
        comp = [ca if c == cb else c for c in comp]
        out.append(len(set(comp)))
    return out


def test_random_cables_against_a_relabelling_reference():
    rng = random.Random(23)
    for _ in range(200):
        n = rng.randint(1, 8)
        cables = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randint(0, 12))]
        check(f"networks_after_each_cable({n}, {cables})", networks_after_each_cable(n, list(cables)), reference(n, cables))


def test_a_long_chain_is_fast():
    n = 100000
    cables = [(i, i + 1) for i in range(n - 1)]
    got = networks_after_each_cable(n, cables)
    check("count after the last of 99999 cables", got[-1], 1)
    check("count after the first", got[0], n - 1)
