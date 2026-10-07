from anneal_prelude import check, ensure
from solution import best_picks


def test_house_robber_shape():
    check('best_picks([3, 2, 7, 10], 2)', best_picks([3, 2, 7, 10], 2), 13)


def test_wider_gap():
    check('best_picks([4, 1, 1, 9, 1], 3)', best_picks([4, 1, 1, 9, 1], 3), 13)


def test_gap_of_one_takes_everything():
    check('best_picks([1, 2, 3], 1)', best_picks([1, 2, 3], 1), 6)


def test_empty():
    check('best_picks([], 2)', best_picks([], 2), 0)


def test_single():
    check('best_picks([5], 4)', best_picks([5], 4), 5)


def test_gap_longer_than_the_list():
    check('best_picks([4, 9, 2], 10)', best_picks([4, 9, 2], 10), 9)
