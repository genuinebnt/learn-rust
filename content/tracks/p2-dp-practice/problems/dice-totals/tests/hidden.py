import random

from anneal_prelude import check, ensure
from solution import dice_ways


def test_minimum_total():
    check('dice_ways(4, 6, 4)', dice_ways(4, 6, 4), 1)


def test_total_below_the_minimum():
    check('dice_ways(4, 6, 3)', dice_ways(4, 6, 3), 0)


def test_maximum_total():
    check('dice_ways(3, 4, 12)', dice_ways(3, 4, 12), 1)


def test_one_face_dice():
    check('dice_ways(5, 1, 5)', dice_ways(5, 1, 5), 1)


def test_ten_dice():
    check('dice_ways(10, 6, 35)', dice_ways(10, 6, 35), 4395456)


def test_single_die():
    check('dice_ways(1, 6, 4)', dice_ways(1, 6, 4), 1)


def reference(dice, faces, total):
    if dice == 0:
        return 1 if total == 0 else 0
    return sum(reference(dice - 1, faces, total - f) for f in range(1, faces + 1) if total - f >= 0)


def test_random_rolls_against_trying_every_outcome():
    rng = random.Random(15)
    for _ in range(300):
        dice, faces = rng.randint(0, 5), rng.randint(1, 6)
        total = rng.randint(0, dice * faces + 2)
        check(f"dice_ways({dice}, {faces}, {total})", dice_ways(dice, faces, total), reference(dice, faces, total))


def test_many_dice_is_fast():
    ensure(dice_ways(100, 6, 350) > 0, "100 dice can make 350")
    check("dice_ways(100, 6, 99)", dice_ways(100, 6, 99), 0)
