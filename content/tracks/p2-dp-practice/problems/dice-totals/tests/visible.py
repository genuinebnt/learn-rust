from anneal_prelude import check, ensure
from solution import dice_ways


def test_two_dice_seven():
    check('dice_ways(2, 6, 7)', dice_ways(2, 6, 7), 6)


def test_too_big_for_one_die():
    check('dice_ways(1, 6, 7)', dice_ways(1, 6, 7), 0)


def test_no_dice_total_zero():
    check('dice_ways(0, 6, 0)', dice_ways(0, 6, 0), 1)


def test_no_dice_other_total():
    check('dice_ways(0, 6, 3)', dice_ways(0, 6, 3), 0)


def test_three_dice():
    check('dice_ways(3, 6, 10)', dice_ways(3, 6, 10), 27)


def test_coin_flips():
    check('dice_ways(3, 2, 5)', dice_ways(3, 2, 5), 3)
