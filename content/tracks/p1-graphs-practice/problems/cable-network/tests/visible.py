from anneal_prelude import check, ensure
from solution import networks_after_each_cable


def test_chain_and_a_loop():
    check('networks_after_each_cable(4, [(0, 1), (2, 3), (1, 2), (0, 3)])', networks_after_each_cable(4, [(0, 1), (2, 3), (1, 2), (0, 3)]), [3, 2, 1, 1])


def test_no_cables():
    check('networks_after_each_cable(5, [])', networks_after_each_cable(5, []), [])


def test_same_cable_twice():
    check('networks_after_each_cable(3, [(0, 1), (1, 0)])', networks_after_each_cable(3, [(0, 1), (1, 0)]), [2, 2])


def test_cable_to_itself():
    check('networks_after_each_cable(2, [(0, 0)])', networks_after_each_cable(2, [(0, 0)]), [2])


def test_everything_joined_at_once():
    check('networks_after_each_cable(3, [(0, 1), (1, 2)])', networks_after_each_cable(3, [(0, 1), (1, 2)]), [2, 1])


def test_no_computers():
    check('networks_after_each_cable(0, [])', networks_after_each_cable(0, []), [])
