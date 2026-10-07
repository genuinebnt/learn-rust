import random

from anneal_prelude import check, ensure
from solution import best_profit_with_fee


def test_one_big_rise():
    check('best_profit_with_fee([1, 10], 2)', best_profit_with_fee([1, 10], 2), 7)


def test_a_dip_that_is_not_worth_a_second_fee():
    check('best_profit_with_fee([1, 5, 4, 8], 3)', best_profit_with_fee([1, 5, 4, 8], 3), 4)


def test_flat():
    check('best_profit_with_fee([3, 3, 3, 3], 1)', best_profit_with_fee([3, 3, 3, 3], 1), 0)


def test_zig_zag_with_a_small_fee():
    check('best_profit_with_fee([1, 4, 1, 4, 1, 4], 1)', best_profit_with_fee([1, 4, 1, 4, 1, 4], 1), 6)


def test_zig_zag_where_the_fee_eats_the_profit():
    check('best_profit_with_fee([1, 4, 1, 4, 1, 4], 3)', best_profit_with_fee([1, 4, 1, 4, 1, 4], 3), 0)


def test_rising_all_the_way():
    check('best_profit_with_fee([1, 2, 3, 4, 5], 1)', best_profit_with_fee([1, 2, 3, 4, 5], 1), 3)


def test_two_days_a_profit():
    check('best_profit_with_fee([2, 9], 3)', best_profit_with_fee([2, 9], 3), 4)


def reference(prices, fee, day=0, holding=False):
    if day == len(prices):
        return 0
    best = reference(prices, fee, day + 1, holding)
    if holding:
        best = max(best, prices[day] - fee + reference(prices, fee, day + 1, False))
    else:
        best = max(best, -prices[day] + reference(prices, fee, day + 1, True))
    return best


def test_random_prices_against_trying_every_plan():
    rng = random.Random(16)
    for _ in range(300):
        prices = [rng.randint(1, 9) for _ in range(rng.randint(0, 9))]
        fee = rng.randint(0, 4)
        check(f"best_profit_with_fee({prices}, {fee})", best_profit_with_fee(prices, fee), reference(prices, fee))
