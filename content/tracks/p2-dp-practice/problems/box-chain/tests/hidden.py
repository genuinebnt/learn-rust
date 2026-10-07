import random

from anneal_prelude import check, ensure
from solution import longest_nesting


def test_same_height_cannot_nest():
    check('longest_nesting([(1, 5), (2, 5), (3, 5)])', longest_nesting([(1, 5), (2, 5), (3, 5)]), 1)


def test_reversed_input_order():
    check('longest_nesting([(3, 3), (2, 2), (1, 1)])', longest_nesting([(3, 3), (2, 2), (1, 1)]), 3)


def test_width_grows_height_shrinks():
    check('longest_nesting([(1, 9), (2, 8), (3, 7)])', longest_nesting([(1, 9), (2, 8), (3, 7)]), 1)


def test_chain_with_noise():
    check('longest_nesting([(1, 1), (5, 1), (2, 2), (1, 5), (3, 3)])', longest_nesting([(1, 1), (5, 1), (2, 2), (1, 5), (3, 3)]), 3)


def test_equal_width_pair_inside_a_bigger_one():
    check('longest_nesting([(2, 1), (2, 2), (3, 3)])', longest_nesting([(2, 1), (2, 2), (3, 3)]), 2)


def test_two_chains():
    check('longest_nesting([(1, 3), (2, 4), (3, 1), (4, 2), (5, 3)])', longest_nesting([(1, 3), (2, 4), (3, 1), (4, 2), (5, 3)]), 3)


def reference(boxes):
    order = sorted(boxes)
    best = [1] * len(order)
    for i in range(len(order)):
        for j in range(i):
            if order[j][0] < order[i][0] and order[j][1] < order[i][1]:
                best[i] = max(best[i], best[j] + 1)
    return max(best, default=0)


def test_random_boxes_against_the_quadratic_dp():
    rng = random.Random(22)
    for _ in range(400):
        boxes = [(rng.randint(1, 6), rng.randint(1, 6)) for _ in range(rng.randint(0, 10))]
        check(f"longest_nesting({boxes})", longest_nesting(list(boxes)), reference(boxes))


def test_a_hundred_thousand_boxes_is_fast():
    boxes = [(i, i) for i in range(100000)]
    check("longest_nesting(100000 nested boxes)", longest_nesting(boxes), 100000)
