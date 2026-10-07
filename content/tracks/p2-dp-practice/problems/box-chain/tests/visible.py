from anneal_prelude import check, ensure
from solution import longest_nesting


def test_three_nested():
    check('longest_nesting([(5, 4), (6, 4), (6, 7), (2, 3)])', longest_nesting([(5, 4), (6, 4), (6, 7), (2, 3)]), 3)


def test_identical_boxes():
    check('longest_nesting([(2, 2), (2, 2)])', longest_nesting([(2, 2), (2, 2)]), 1)


def test_no_boxes():
    check('longest_nesting([])', longest_nesting([]), 0)


def test_one_box():
    check('longest_nesting([(3, 9)])', longest_nesting([(3, 9)]), 1)


def test_same_width_cannot_nest():
    check('longest_nesting([(4, 1), (4, 2), (4, 3)])', longest_nesting([(4, 1), (4, 2), (4, 3)]), 1)


def test_a_perfect_chain():
    check('longest_nesting([(1, 1), (2, 2), (3, 3)])', longest_nesting([(1, 1), (2, 2), (3, 3)]), 3)
